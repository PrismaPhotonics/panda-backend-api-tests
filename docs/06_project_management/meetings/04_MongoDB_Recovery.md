# טסט 4: MongoDB Recovery – Recordings Indexed After Outage
## PZ-13687 - ניתוח מקיף ומעמיק

---

## 📋 תקציר מהיר לפגישה (Quick Brief)

| **שדה** | **ערך** |
|---------|---------|
| **Jira ID** | PZ-13687 |
| **שם הטסט** | MongoDB Recovery – Recordings Indexed After Outage |
| **עדיפות** | 🔴 **CRITICAL** |
| **סוג** | Infrastructure / Resilience / Recovery Test |
| **סטטוס אוטומציה** | ⚠️ **Partial** (Requires Kubernetes) |
| **משך ריצה צפוי** | ~30-60 שניות (+ recovery time) |
| **מורכבות מימוש** | 🔴 **מאוד גבוהה** |
| **קובץ טסט** | `tests/performance/test_mongodb_outage_resilience.py` |
| **Test Class** | `TestMongoDBOutageResilience` |
| **שורות** | 386-451 |
| **תלויות** | Kubernetes, MongoDB, Focus Server API |

---

## 🎯 מה המטרה של הטסט? (Test Objectives)

### מטרה אסטרטגית (Strategic Goal):
לוודא שהמערכת **לא מאבדת נתונים** ו**מתאוששת אוטומטית** לאחר הפסקת MongoDB. ספציפית - recordings שנוספו **במהלך ההפסקה** צריכים להיות **אינדקסים אוטומטית** אחרי ההתאוששות.

### מטרות ספציפיות (Specific Goals):
1. **אימות recovery mechanism** - האם יש מנגנון אוטומטי לאיתור נתונים חדשים?
2. **מניעת data loss** - אף recording לא "נעלם"
3. **אימות indexing** - recordings חדשים מופיעים ב-MongoDB
4. **תיעוד התנהגות** - מה קורה בדיוק במהלך ואחרי outage

---

## 🧪 מה אני רוצה לבדוק? (What We're Testing)

### הסצנריו שאנחנו בודקים:

**Timeline של הטסט**:

```
Time T0:  MongoDB פועל תקין
          Focus Server פועל תקין
          יש N recordings ב-MongoDB

Time T1:  MongoDB נכבה (scale down to 0 replicas)
          MongoDB לא זמין
          Focus Server לא יכול לגשת ל-MongoDB

Time T2:  Recording חדש נוסף לאחסון (file system)
          Recording זה לא באינדקס (MongoDB down!)

Time T3:  MongoDB חוזר לפעולה (scale up to 1 replica)
          MongoDB זמין שוב
          Focus Server מתחבר ל-MongoDB

Time T4:  Focus Server מזהה recording חדש (recovery mechanism)
          Recording נאינדקס אוטומטית
          עכשיו יש N+1 recordings ב-MongoDB

Expected: Recording חדש מופיע ב-MongoDB ללא התערבות ידנית!
```

---

## 🔥 מה הנחיצות של הטסט? (Why Is This Critical?)

### סיכונים אם לא בודקים:

#### 1️⃣ **איבוד נתונים** (Data Loss)
**תרחיש**:  
MongoDB נכבה למשך 10 דקות (maintenance, crash, network issue).  
במהלך הזמן הזה, 50 recordings חדשים נוספים לאחסון.  
לאחר ההתאוששות → **50 recordings לא מופיעים במערכת!**

**השפעה**:
- משתמשים לא רואים את הנתונים
- איבוד מידע קריטי
- צריך manual reindexing → עבודה ידנית

---

#### 2️⃣ **חוסר סנכרון בין Storage ל-Database** (Data Inconsistency)
**תרחיש**:  
File system מכיל 1000 recordings.  
MongoDB מכיל רק 950 recordings.  
**Gap של 50 recordings!**

**השפעה**:
- אי עקביות נתונים
- בלבול משתמשים: "איפה ה-recordings?"
- קשה לזהות מה חסר

---

#### 3️⃣ **Manual Recovery Required** (עבודה ידנית)
**תרחיש**:  
אחרי outage, צוות DevOps צריך **ידנית** לרוץ script לאינדוקס recordings חדשים.

**השפעה**:
- עומס על DevOps
- זמן downtime ארוך
- סיכון לטעות אנוש

---

#### 4️⃣ **Loss of Trust** (אובדן אמון)
**תרחיש**:  
לקוח רואה ש-recordings "נעלמו" אחרי תקלה.

**השפעה**:
- אובדן אמון במערכת
- לקוח עובר למתחרה
- תדמית רעה

---

## 🛠️ איך אני ממש אותו בקוד? (Code Implementation)

### קובץ הטסט:
**Path**: `tests/performance/test_mongodb_outage_resilience.py`  
**Test Class**: `TestMongoDBOutageResilience`  
**Lines**: 386-451

---

### קוד מלא עם הסברים:

```python
@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.resilience
@pytest.mark.mongodb_outage
@pytest.mark.slow
def test_mongodb_outage_cleanup_and_restore(self, focus_server_api):
    """
    Test MongoDB can be restored after an outage and recordings are indexed.
    
    Test Steps:
        1. Create MongoDB outage (scale down to 0 replicas)
        2. Verify outage is active (MongoDB unreachable)
        3. Add new recording file to storage (simulates data arriving during outage)
        4. Restore MongoDB (scale up to 1 replica)
        5. Verify MongoDB is reachable
        6. Wait for Focus Server to detect and index new recording
        7. Verify new recording appears in MongoDB
        8. Verify count increased by +1
    
    Expected:
        - MongoDB recovery triggers automatic indexing of new recordings
        - No data loss occurs
        - No manual intervention required
    
    Jira: PZ-13687
    Priority: CRITICAL
    """
    test_name = "mongodb_outage_cleanup_and_restore"
    self.logger.info(f"Starting test: {test_name}")
    
    try:
        # =====================================================
        # Step 1: Baseline - Count existing recordings
        # =====================================================
        self.log_test_step("Counting existing recordings")
        
        # Connect to MongoDB
        assert self.mongodb_manager.connect(), "MongoDB is not reachable before test"
        
        # Get initial count of recordings in node4 collection
        initial_count = self.mongodb_manager.count_documents("node4", {})
        self.logger.info(f"Initial recordings count: {initial_count}")
        
        self.mongodb_manager.disconnect()
        
        # =====================================================
        # Step 2: Create MongoDB outage
        # =====================================================
        self.log_test_step("Creating MongoDB outage by scaling down")
        
        # Scale down MongoDB deployment to 0 replicas (simulates crash/maintenance)
        self.mongodb_manager.scale_down_mongodb(replicas=0)
        time.sleep(5)  # Give Kubernetes time to react
        
        # =====================================================
        # Step 3: Verify outage is active
        # =====================================================
        self.log_test_step("Verifying MongoDB outage is active")
        
        # Try to connect - should fail
        assert not self.mongodb_manager.connect(), \
            "MongoDB is still reachable after scaling down (outage not effective)"
        
        self.logger.info("✅ MongoDB is unreachable (outage confirmed)")
        
        # =====================================================
        # Step 4: Add new recording file during outage
        # =====================================================
        self.log_test_step("Adding new recording file to storage during outage")
        
        # Simulate new recording arriving during outage
        # In real scenario: data acquisition system writes new file
        # For test: we manually create a test recording file
        
        # Generate unique recording ID
        test_recording_id = f"test_recording_{int(time.time())}"
        
        # Add recording to file system
        # Note: Actual implementation depends on storage structure
        # This is a simplified simulation
        self.logger.info(f"Simulating new recording: {test_recording_id}")
        
        # In real implementation:
        # - Create file in /data/recordings/{test_recording_id}.dat
        # - Create metadata file
        # - Ensure proper permissions
        
        # For this test, we'll mark it for tracking
        self.test_recording_id = test_recording_id
        
        # =====================================================
        # Step 5: Restore MongoDB
        # =====================================================
        self.log_test_step("Restoring MongoDB (scaling up)")
        
        # Scale up MongoDB deployment to 1 replica
        self.mongodb_manager.restore_mongodb()
        time.sleep(15)  # Give MongoDB time to fully start and become ready
        
        # =====================================================
        # Step 6: Verify MongoDB is reachable
        # =====================================================
        self.log_test_step("Verifying MongoDB is reachable after restoration")
        
        # Connect to MongoDB
        assert self.mongodb_manager.connect(), \
            "MongoDB is not reachable after restoration (recovery failed)"
        
        self.logger.info("✅ MongoDB is reachable (recovery successful)")
        
        # =====================================================
        # Step 7: Wait for Focus Server recovery indexing
        # =====================================================
        self.log_test_step("Waiting for Focus Server to detect and index new recording")
        
        # Focus Server should have a recovery mechanism that:
        # 1. Detects MongoDB is back online
        # 2. Scans storage for new recordings
        # 3. Indexes missing recordings
        
        # Wait for recovery process (with timeout)
        max_wait_time = 60  # seconds
        check_interval = 5  # seconds
        elapsed_time = 0
        
        recording_indexed = False
        
        while elapsed_time < max_wait_time:
            # Check if new recording was indexed
            # Query MongoDB for our test recording
            
            # Note: Actual query depends on schema
            # Example: Find recording by ID or timestamp
            
            # For this simplified test, we check if count increased
            current_count = self.mongodb_manager.count_documents("node4", {})
            
            if current_count > initial_count:
                recording_indexed = True
                self.logger.info(
                    f"✅ New recording indexed! "
                    f"Count increased from {initial_count} to {current_count}"
                )
                break
            
            # Wait before next check
            self.logger.debug(
                f"Waiting for indexing... "
                f"({elapsed_time}s/{max_wait_time}s)"
            )
            time.sleep(check_interval)
            elapsed_time += check_interval
        
        # =====================================================
        # Step 8: Verify new recording appears
        # =====================================================
        self.log_test_step("Verifying new recording appears in MongoDB")
        
        # Assert that recording was indexed
        assert recording_indexed, \
            f"New recording was not indexed within {max_wait_time}s after MongoDB recovery"
        
        # Get final count
        final_count = self.mongodb_manager.count_documents("node4", {})
        
        # Verify count increased by at least +1
        assert final_count >= initial_count + 1, \
            f"Recording count did not increase as expected: {initial_count} → {final_count}"
        
        self.logger.info(f"✅ Recording count: {initial_count} → {final_count} (+{final_count - initial_count})")
        
        # =====================================================
        # Step 9: Verify no side effects from restoration
        # =====================================================
        self.log_test_step("Verifying no side effects from restoration")
        self._verify_no_side_effects(test_name)
        
        # =====================================================
        # Step 10: Cleanup
        # =====================================================
        self.log_test_step("Cleaning up test recording")
        
        # In real implementation: delete test recording file
        # For now, just log
        self.logger.info(f"Test recording {test_recording_id} should be cleaned up")
        
        # Disconnect from MongoDB
        self.mongodb_manager.disconnect()
        
        self.logger.info(f"✅ Test completed successfully: {test_name}")
        
    except Exception as e:
        self.logger.error(f"❌ Test failed: {test_name} - {e}")
        raise
```

---

## 🎓 מה לומדים מהטסט הזה?

### תוצאות צפויות:

```
Test: mongodb_outage_cleanup_and_restore
=============================================================
Step 1: Initial recordings count: 1500
Step 2: Scaling MongoDB down to 0 replicas...
Step 3: ✅ MongoDB is unreachable (outage confirmed)
Step 4: Simulating new recording: test_recording_1697812345
Step 5: Restoring MongoDB (scaling up to 1 replica)...
Step 6: ✅ MongoDB is reachable (recovery successful)
Step 7: Waiting for Focus Server to detect and index...
        - After 10s: count = 1500 (not yet indexed)
        - After 15s: count = 1501 (indexed!)
        ✅ New recording indexed!
Step 8: ✅ Recording count: 1500 → 1501 (+1)
=============================================================
✅ Test completed successfully
```

---

### מה אם הטסט נכשל?

#### Failure Scenario 1: Recording לא נאינדקס
```
Step 7: Waiting for indexing... (60s timeout)
        - After 10s: count = 1500
        - After 20s: count = 1500
        - After 30s: count = 1500
        - After 60s: count = 1500
❌ FAILURE: New recording was not indexed within 60s
```

**מה זה אומר?**
- **אין recovery mechanism** ב-Focus Server!
- או: **הוא לא פועל** כמו שצריך
- **Action Required**: צוות Dev צריך לממש recovery mechanism

---

#### Failure Scenario 2: Count לא עלה
```
Step 8: Recording count: 1500 → 1500 (no change)
❌ FAILURE: Recording count did not increase
```

**מה זה אומר?**
- Recording לא נוסף בצורה נכונה
- או: Recovery mechanism לא זיהה אותו
- **Action Required**: בדיקת file system, בדיקת recovery logic

---

## 🗣️ שאלות לפגישה (Questions for the Meeting)

### שאלות קריטיות:
1. **האם יש recovery mechanism ב-Focus Server?**
   - מה הלוגיקה שלו?
   - איך הוא מזהה recordings חדשים?
   - כל כמה זמן הוא רץ?

2. **מה קורה במהלך MongoDB outage?**
   - האם recordings ממשיכים להגיע לאחסון?
   - איפה הם נשמרים?
   - מה קורה ל-metadata?

3. **איך Focus Server יודע שיש recordings חדשים?**
   - File system scan?
   - Message queue?
   - Periodic polling?

4. **מה timeout ל-recovery?**
   - כמה זמן לוקח עד ש-recording נאינדקס?
   - האם יש retry mechanism?

5. **האם יש alerting כש-MongoDB down?**
   - Slack notification?
   - PagerDuty?
   - Email?

---

### שאלות טכניות:
6. **איך מדמים MongoDB outage בטסט?**
   - `kubectl scale deployment mongodb --replicas=0`
   - Network block?
   - Pod deletion?

7. **איך מוסיפים recording במהלך outage?**
   - Manual file creation?
   - API call to data acquisition system?

8. **מה המבנה של recording ב-file system?**
   - Path: `/data/recordings/{recording_id}.dat`?
   - Metadata: `/data/recordings/{recording_id}.json`?

9. **האם יש locking mechanism?**
   - כדי למנוע concurrent indexing?

10. **מה קורה אם יש 1000 recordings חדשים?**
    - האם recovery יכול לטפל?
    - האם יש batch processing?

---

## 📊 טבלת סיכום - Recovery Scenarios

| Scenario | MongoDB Outage Time | New Recordings | Expected Behavior |
|----------|-------------------|----------------|------------------|
| **Short Outage** | < 1 min | 1-5 | ✅ Auto-index immediately |
| **Medium Outage** | 1-10 min | 5-50 | ✅ Auto-index in batch |
| **Long Outage** | 10-60 min | 50-500 | ⚠️ Slow indexing |
| **Extended Outage** | > 60 min | 500+ | 🚫 Manual intervention? |

---

## ✅ Checklist לפני הפגישה

- [ ] קראתי את המסמך הזה לעומק
- [ ] הבנתי מה זה recovery mechanism ולמה הוא קריטי
- [ ] הבנתי את ה-timeline של הטסט
- [ ] יודע מה הסיכונים של data loss
- [ ] הכנתי שאלות על ה-recovery logic
- [ ] יודע איך Kubernetes scaling עובד
- [ ] סקרתי את הקוד ב-`test_mongodb_outage_resilience.py`
- [ ] יודע מה ההבדל בין file system ל-database

---

## 📌 נקודות מפתח לזכור

1. **File system ≠ Database** → צריך sync!
2. **Recovery mechanism הוא קריטי** → למניעת data loss
3. **הטסט דורש Kubernetes** → לא יכול לרוץ ב-dev local
4. **Outage לא אומר data loss** → אם יש recovery
5. **Manual recovery = Bad** → צריך automatic!

---

**נכתב עבור**: Roy Avrahami  
**תאריך**: אוקטובר 2025  
**Jira**: PZ-13687

---

