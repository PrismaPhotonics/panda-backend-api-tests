# 📋 תוכנית פעולה מפורטת להערות מ-Jira

**נוצר:** 2025-10-15  
**מטרה:** החלטה מדויקת לכל הערה - שינוי קיים או יצירת חדש, ללא כפילויות

---

## 🎯 עקרון מנחה:
✅ **לא ליצור טסטים כפולים**  
✅ **להשתמש במה שקיים אם אפשר**  
✅ **ליצור חדש רק אם באמת חסר**

---

## 📝 ניתוח כל הערה:

---

### 1️⃣ **PZ-13604** - MongoDB Recovery Test
**הערה:** *"need to fix the test, the test should check that in case that MongDB is off for while and then return to work, the recordings that didnt processed in this time will be indexing after that"*

#### 🔍 מצב נוכחי:
- **קובץ קיים:** `tests/integration/infrastructure/test_mongodb_outage_resilience.py`
- **מה יש:**
  - ✅ `test_mongodb_scale_down_outage_returns_503_no_orchestration` - בודק שהשרת כושל כשMongoDB למטה
  - ✅ `test_mongodb_network_block_outage_returns_503_no_orchestration` - בודק network block
  - ✅ `test_mongodb_outage_cleanup_and_restore` - בודק restore אחרי outage
  - ❌ **חסר:** בדיקה שrecordings שלא עובדו בזמן ה-outage מתעדכנים אחרי recovery

#### 💡 **החלטה: הוספת טסט חדש ל-MongoDB Resilience**

**למה לא לשנות קיים?**
- הטסטים הקיימים בודקים **fail-fast behavior** (תגובה נכונה ל-outage)
- ההערה שלך דורשת **recovery behavior** (מה קורה אחרי שחוזר)
- זה **תרחיש אחר לגמרי**

**מה ניצור:**
```python
def test_mongodb_recovery_indexes_pending_recordings(self, focus_server_api):
    """
    Test that recordings are indexed after MongoDB recovers from outage.
    
    Test Flow:
    1. Verify MongoDB is healthy and has N recordings
    2. Simulate new recordings being added to storage (mock or real)
    3. Scale down MongoDB (outage simulation)
    4. Verify POST /configure fails with 503 (expected)
    5. Restore MongoDB
    6. Wait for recovery/indexing process
    7. Verify new recordings are now indexed in MongoDB
    8. Verify POST /configure succeeds with recovered data
    
    Objective:
    Validate that the system has a recovery mechanism that indexes
    recordings that were added during MongoDB downtime.
    
    Related: PZ-13604
    """
```

**מיקום:** `tests/integration/infrastructure/test_mongodb_outage_resilience.py`  
**שם:** `test_mongodb_recovery_indexes_pending_recordings`

---

### 2️⃣ **PZ-13598** - MongoDB Indexes Validation
**הערה:** *"Add tests that check the indexes of the mongoDB collocations on all the recording that exist in the DB, check for missing recording metadata in the MongoDB"*

#### 🔍 מצב נוכחי:
- **קובץ קיים:** אין טסט ספציפי לזה
- **מה יש:**
  - ✅ `test_basic_connectivity.py` - בודק connection למונגו
  - ✅ `test_mongodb_outage_resilience.py` - בודק resilience
  - ❌ **אין בדיקה של:** indexes structure, missing metadata, data quality

#### 💡 **החלטה: יצירת טסט חדש לגמרי - Data Quality**

**למה טסט חדש?**
- זה לא connectivity ולא resilience
- זה **Data Quality & Schema Validation**
- צריך קובץ חדש עם focus ספציפי

**מה ניצור:**
```python
# File: tests/integration/infrastructure/test_mongodb_data_quality.py

class TestMongoDBDataQuality(InfrastructureTest):
    """
    MongoDB Data Quality Tests.
    
    Validates MongoDB schema, indexes, and data integrity.
    """
    
    def test_required_collections_exist(self):
        """Verify all required collections are present."""
        # base_paths, node2, node4, etc.
    
    def test_node4_schema_validation(self):
        """Verify node4 documents have required fields and correct types."""
        # uuid, start_time, end_time, deleted fields
    
    def test_recordings_have_all_required_metadata(self):
        """
        Scan all recordings and verify none have missing metadata.
        
        Checks:
        - Every recording has start_time, end_time
        - Every recording has uuid
        - No null/missing critical fields
        - Detects orphaned records
        
        Related: PZ-13598
        """
    
    def test_mongodb_indexes_exist_and_optimal(self):
        """
        Verify MongoDB indexes exist on critical fields.
        
        Validates:
        - Index on node4.start_time (for time range queries)
        - Index on node4.end_time
        - Index on node4.uuid
        - Index on node4.deleted (for filtering)
        - Compound indexes if needed
        
        Performance:
        - Warns if missing indexes that would improve performance
        - Measures query time with/without indexes
        
        Related: PZ-13598
        """
```

**מיקום:** `tests/integration/infrastructure/test_mongodb_data_quality.py` (**קובץ חדש**)  
**סה"כ טסטים:** 4-5 טסטים

---

### 3️⃣ **PZ-13571** - Memory Load Testing
**הערה:** *"need to add memory load tests"*

#### 🔍 מצב נוכחי:
- **קובץ רלוונטי:** אין טסט performance/load
- **מה יש:**
  - ❌ אין טסט שבודק memory usage
  - ❌ אין טסט שבודק performance תחת עומס
  - ✅ יש `test_focus_server_healed.py` עם `test_cache_improves_performance` אבל זה לא load test

#### 💡 **החלטה: יצירת טסט Performance חדש**

**למה טסט חדש?**
- אין בכלל infrastructure ל-performance/load testing
- צריך קובץ ייעודי ל-performance tests

**מה ניצור:**
```python
# File: tests/integration/performance/test_configure_performance.py

class TestConfigurePerformance:
    """
    Performance tests for /configure endpoint.
    
    Tests latency, throughput, memory usage under various loads.
    """
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_configure_latency_p95_under_load(self, focus_server_api):
        """
        Measure /configure latency under minimal load (p95 < 2.0s).
        
        Related: PZ-13571
        """
        # Send 20 requests sequentially
        # Measure p50, p95, p99
        # Assert p95 < 2.0s
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_configure_memory_usage_under_concurrent_load(self, focus_server_api):
        """
        Test memory consumption with multiple concurrent /configure requests.
        
        Test Flow:
        1. Measure baseline memory usage (before load)
        2. Send 10 concurrent /configure requests (threads/async)
        3. Monitor memory during execution:
           - RSS (Resident Set Size)
           - Heap usage
           - Memory leaks detection
        4. Wait for requests to complete
        5. Measure memory after load
        6. Verify memory is released (no significant leak)
        
        Assertions:
        - Memory increase is reasonable (<500MB per job)
        - Memory is released after jobs complete
        - No memory leak (memory returns to near-baseline)
        
        Tools: psutil, memory_profiler, or K8s metrics
        
        Related: PZ-13571
        """
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_configure_concurrent_requests_no_port_collision(self, focus_server_api):
        """
        Test that concurrent requests don't cause port collisions.
        
        Validates:
        - 10 concurrent jobs each get unique port
        - No "port already in use" errors
        - Job isolation is maintained
        
        Related: PZ-13571, PZ-13565
        """
```

**מיקום:** `tests/integration/performance/test_configure_performance.py` (**קובץ חדש**)  
**תיקייה חדשה:** `tests/integration/performance/`  
**סה"כ טסטים:** 3-4 טסטים

---

### 4️⃣ **PZ-13568** - GRPCLauncher Cleanup Test
**הערה:** *"need to add cleanup test"*

#### 🔍 מצב נוכחי:
- **קובץ רלוונטי:** אין טסט ספציפי ל-GRPCLauncher
- **מה יש:**
  - ✅ `test_mongodb_outage_resilience.py` יש `test_mongodb_outage_cleanup_and_restore`
  - ❌ **אין טסט cleanup ספציפי ל-GRPC launcher**

#### 💡 **החלטה: יצירת טסט Service-level חדש**

**למה טסט חדש?**
- אין כיסוי ל-service-level testing של GRPCLauncher
- זה לא infrastructure resilience, זה **service behavior testing**

**מה ניצור:**
```python
# File: tests/integration/services/test_grpc_launcher_lifecycle.py

class TestGRPCLauncherLifecycle:
    """
    GRPCLauncher Service Lifecycle Tests.
    
    Tests start, stop, cleanup behavior of the gRPC launcher.
    """
    
    @pytest.mark.integration
    @pytest.mark.services
    def test_grpc_launcher_start_allocates_resources(self, focus_server_api):
        """
        Test that GRPCLauncher.start() allocates resources correctly.
        
        Validates:
        - K8s Job/Service is created
        - Port is allocated
        - YAML is applied
        - stream_url and stream_port are populated
        
        Related: PZ-13568
        """
    
    @pytest.mark.integration
    @pytest.mark.services
    def test_grpc_launcher_stop_cleans_all_resources(self, focus_server_api):
        """
        Test that GRPCLauncher.stop() cleans up ALL resources.
        
        Test Flow:
        1. Start a job via POST /configure
        2. Verify resources are created:
           - K8s Job exists
           - K8s Service exists
           - Port is allocated
           - YAML files exist (if applicable)
        3. Stop the job (DELETE /job/{id} or internal stop)
        4. Verify ALL resources are cleaned:
           - K8s Job is deleted
           - K8s Service is deleted
           - Port is released (can be reused)
           - YAML files are removed
           - No orphaned pods
        5. Verify next job can use same resources
        
        Objective:
        Ensure no resource leaks after GRPCLauncher.stop().
        
        Related: PZ-13568
        """
    
    @pytest.mark.integration
    @pytest.mark.services
    def test_grpc_launcher_cleanup_on_failure(self, focus_server_api):
        """
        Test cleanup when launcher fails mid-operation.
        
        Simulates:
        - Failure during YAML apply
        - Failure during K8s job creation
        - Network error during setup
        
        Validates:
        - Partial resources are cleaned up
        - System is left in consistent state
        
        Related: PZ-13568
        """
```

**מיקום:** `tests/integration/services/test_grpc_launcher_lifecycle.py` (**קובץ חדש**)  
**תיקייה חדשה:** `tests/integration/services/`  
**סה"כ טסטים:** 3 טסטים

---

### 5️⃣ **PZ-13565** - Port Cleanup Test
**הערה:** *"Need to check if the port is closed after we close the investigation/ when we close the app/ crash/ disconnect the lan or wifi ect."*

#### 🔍 מצב נוכחי:
- **קובץ רלוונטי:** אין טסט port lifecycle
- **מה יש:**
  - ❌ **אין בדיקה של port cleanup**
  - ❌ אין בדיקה של port reuse

#### 💡 **החלטה: הוספה ל-Services או Performance**

**למה לא טסט נפרד?**
- זה קשור ישירות ל-GRPCLauncher (משימה 4)
- זה גם קשור ל-performance/concurrency (משימה 3)

**מה ניצור:**

**אופציה 1: הוספה ל-GRPCLauncher tests** ✅ (מועדף)
```python
# Add to: tests/integration/services/test_grpc_launcher_lifecycle.py

def test_port_released_after_job_completion(self, focus_server_api):
    """
    Test that port is released after job completes.
    
    Related: PZ-13565
    """

def test_port_released_after_app_crash(self, focus_server_api):
    """
    Test port cleanup when app crashes.
    
    Simulates:
    - Focus Server pod killed
    - Focus Server restart
    
    Validates:
    - Port is not left occupied
    - New jobs can use same port after recovery
    
    Related: PZ-13565
    """

def test_port_released_after_network_disconnect(self, focus_server_api):
    """
    Test port cleanup on network disconnect.
    
    Related: PZ-13565
    """
```

**אופציה 2: הוספה ל-Performance tests** (אם יש concurrency test)
```python
# Already planned in test_configure_concurrent_requests_no_port_collision
```

**החלטה סופית:** 
- ✅ **נוסיף 3 טסטי port ל-GRPCLauncher lifecycle**
- ✅ הטסט concurrent ב-Performance כבר מכסה collision

**מיקום:** `tests/integration/services/test_grpc_launcher_lifecycle.py`  
**הוספה:** 3 טסטים נוספים לקובץ

---

### 6️⃣ **PZ-13556** - Backend Consistency
**הערה:** *"check in the BE if its the same channel process"*

#### ✅ **הושלם!**

**מה עשינו:**
- ✅ יצרנו `test_singlechannel_view_mapping.py` (13 tests)
- ✅ יש `TestSingleChannelBackendConsistency` class
- ✅ יש `test_same_channel_multiple_requests_consistent_mapping`
- ✅ יש `test_different_channels_different_mappings`
- ✅ הטסטים רצו בהצלחה, גילו 3 bugs

**סטטוס:** ✅ **לא צריך לעשות כלום - הושלם בהצלחה!**

---

## 📊 סיכום החלטות:

| הערה | Jira ID | החלטה | מיקום | טסטים חדשים |
|------|---------|-------|-------|-------------|
| MongoDB Recovery | PZ-13604 | ✅ הוספת 1 טסט | `test_mongodb_outage_resilience.py` | 1 |
| MongoDB Indexes | PZ-13598 | ✅ קובץ חדש | `test_mongodb_data_quality.py` | 4-5 |
| Memory Load | PZ-13571 | ✅ קובץ חדש | `test_configure_performance.py` | 3-4 |
| GRPC Cleanup | PZ-13568 | ✅ קובץ חדש | `test_grpc_launcher_lifecycle.py` | 3 |
| Port Cleanup | PZ-13565 | ✅ הוספה ל-GRPC | `test_grpc_launcher_lifecycle.py` | 3 |
| Backend Consistency | PZ-13556 | ✅ **הושלם!** | `test_singlechannel_view_mapping.py` | - |
| **סה"כ** | | | **3 קבצים חדשים + 1 שינוי** | **17-19** |

---

## 🎯 קבצים חדשים שייווצרו:

```
tests/integration/
├── infrastructure/
│   ├── test_mongodb_outage_resilience.py    # קיים - נוסיף 1 טסט
│   └── test_mongodb_data_quality.py         # 🆕 חדש - 4-5 טסטים
├── services/                                # 🆕 תיקייה חדשה
│   └── test_grpc_launcher_lifecycle.py      # 🆕 חדש - 6 טסטים
└── performance/                             # 🆕 תיקייה חדשה
    └── test_configure_performance.py        # 🆕 חדש - 3-4 טסטים
```

---

## ✅ למה הפתרון הזה טוב?

### 🎯 עקרונות שעקבנו:

1. **אין כפילויות:**
   - כל טסט בודק משהו ספציפי ושונה
   - Port cleanup משולב ב-GRPC lifecycle (לא נפרד)
   - Concurrent port test ב-performance (לא נפרד)

2. **ארגון לוגי:**
   - Data Quality → Infrastructure
   - Service behavior → Services (חדש)
   - Performance → Performance (חדש)

3. **שימוש במה שקיים:**
   - MongoDB resilience כבר קיים - רק נוסיף טסט recovery
   - SingleChannel כבר מושלם - לא נוגעים

4. **תיקיות חדשות רק כשצריך:**
   - `services/` - behavior testing של services פנימיים
   - `performance/` - load, memory, latency tests

5. **כל טסט עם מטרה ברורה:**
   - Docstrings מפורטים
   - Test Flow מתועד
   - Related Jira IDs

---

## 🚀 סדר ביצוע מומלץ:

1. **קל ← קשה:**
   1. MongoDB Data Quality (פשוט, read-only)
   2. MongoDB Recovery (בינוני, צריך setup)
   3. GRPC Lifecycle (מורכב, צריך K8s)
   4. Performance (מורכב, צריך monitoring)

2. **Dependencies:**
   - MongoDB tests → אין תלות
   - GRPC tests → צריך K8s working
   - Performance → צריך monitoring tools

3. **Time estimate:**
   - MongoDB Data Quality: 2-3 שעות
   - MongoDB Recovery: 3-4 שעות
   - GRPC Lifecycle: 4-5 שעות
   - Performance: 5-6 שעות
   - **סה"כ:** 14-18 שעות עבודה

---

## 🎓 התוצאה הסופית:

**מצב נוכחי:** 93 tests  
**אחרי ביצוע:** 110-112 tests  
**כיסוי:** 
- ✅ All Jira comments addressed
- ✅ No duplicate tests
- ✅ Clear organization
- ✅ Full documentation

---

**סיכום נוצר:** 2025-10-15  
**על ידי:** QA Automation Architect

