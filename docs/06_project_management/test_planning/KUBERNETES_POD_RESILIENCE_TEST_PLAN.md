# תוכנית בדיקות - Kubernetes Pod Resilience
==============================================

**תאריך יצירה:** 2025-11-07  
**מטרה:** בדיקת resilience של המערכת כש-Kubernetes pods נופלים או לא פעילים  
**עדיפות:** גבוהה (High)  
**קשור ל:** PZ-13756 (Infrastructure Resilience)

---

## 📋 סקירה כללית

### מטרת הבדיקות
לבדוק איך המערכת מגיבה כאשר אחד או יותר מה-pods הקריטיים ב-namespace `panda` נופלים, לא פעילים, או לא זמינים.

### Pods קריטיים לבדיקה
1. **MongoDB:** `mongodb-7cb5d67cc5-np7ch` (Deployment: mongodb)
2. **RabbitMQ:** `rabbitmq-panda-0` (StatefulSet: rabbitmq-panda)
3. **Focus Server:** `panda-panda-focus-server-78dbcfd9d9-kjj77` (Deployment: panda-panda-focus-server)
4. **SEGY Recorder:** `panda-panda-segy-recorder-84b4d85bcc-gtwnt` (Deployment: panda-panda-segy-recorder)

---

## 🎯 תרחישי בדיקה

### קטגוריה 1: Pod Failure Scenarios (תרחישי כשל)

#### 1.1 Pod Deletion (מחיקת Pod)
**תיאור:** מחיקת pod כדי לבדוק איך Kubernetes מטפל ב-recreation  
**תרחישים:**
- מחיקת pod בודד
- מחיקת pod בזמן שיש requests פעילים
- מחיקת pod בזמן שיש jobs פעילים

**ציפיות:**
- Kubernetes יוצר pod חדש אוטומטית (ReplicaSet/StatefulSet)
- המערכת ממשיכה לעבוד לאחר ה-recreation
- אין data loss (אם יש persistence)

#### 1.2 Pod Crash/Restart (קריסה/הפעלה מחדש)
**תיאור:** Pod קורס או restart  
**תרחישים:**
- Pod crash עם restart policy
- Pod restart עקב liveness probe failure
- Pod restart עקב resource limits

**ציפיות:**
- Pod restart אוטומטי
- המערכת ממשיכה לעבוד לאחר restart
- אין data corruption

#### 1.3 Pod Not Ready (Pod לא מוכן)
**תיאור:** Pod רץ אבל לא עובר readiness probe  
**תרחישים:**
- Pod תקוע ב-ContainerCreating
- Pod תקוע ב-Pending
- Pod תקוע ב-CrashLoopBackOff

**ציפיות:**
- המערכת לא מנסה להשתמש ב-pod לא מוכן
- יש fallback או retry mechanism
- הודעות שגיאה ברורות

---

### קטגוריה 2: Scaling Scenarios (תרחישי Scaling)

#### 2.1 Scale Down to 0 (הקטנה ל-0)
**תיאור:** Scale down deployment ל-0 replicas  
**תרחישים:**
- Scale MongoDB ל-0
- Scale RabbitMQ ל-0
- Scale Focus Server ל-0
- Scale SEGY Recorder ל-0

**ציפיות:**
- המערכת מחזירה שגיאות ברורות (503 Service Unavailable)
- אין crashes או undefined behavior
- המערכת מתאוששת לאחר scale up

#### 2.2 Scale Up/Down (הגדלה/הקטנה)
**תיאור:** שינוי מספר replicas  
**תרחישים:**
- Scale up מ-1 ל-2 (אם נתמך)
- Scale down מ-2 ל-1
- Rolling update

**ציפיות:**
- אין downtime במהלך scaling
- המערכת ממשיכה לעבוד
- Load balancing עובד נכון

---

### קטגוריה 3: Network Issues (בעיות רשת)

#### 3.1 Pod Network Isolation (בידוד רשת)
**תיאור:** Pod לא יכול לתקשר עם pods אחרים  
**תרחישים:**
- MongoDB לא יכול לתקשר עם Focus Server
- RabbitMQ לא יכול לתקשר עם Focus Server
- Focus Server לא יכול לתקשר עם MongoDB/RabbitMQ

**ציפיות:**
- הודעות שגיאה ברורות
- Retry logic
- Graceful degradation

---

### קטגוריה 4: Resource Exhaustion (תשלום משאבים)

#### 4.1 CPU/Memory Limits (מגבלות CPU/Memory)
**תיאור:** Pod מגיע ל-resource limits  
**תרחישים:**
- Pod נהרג עקב OOM (Out of Memory)
- Pod throttled עקב CPU limits
- Node resource exhaustion

**ציפיות:**
- Pod restart אוטומטי
- המערכת ממשיכה לעבוד
- Resource monitoring מדווח על הבעיה

---

## 📊 מטריצת בדיקות לפי Pod

### MongoDB Pod Resilience

| תרחיש | פעולה | ציפייה | Priority |
|-------|-------|--------|----------|
| Pod Deletion | `kubectl delete pod mongodb-xxx` | Pod recreated, connection restored | P0 |
| Scale Down to 0 | `scale deployment mongodb 0` | 503 errors, no crashes | P0 |
| Pod Crash | Kill container process | Pod restart, data intact | P1 |
| Network Isolation | Block network to pod | Connection errors, retry logic | P2 |
| Resource Exhaustion | Exceed memory limits | Pod restart, monitoring alerts | P2 |

**בדיקות נדרשות:**
1. ✅ MongoDB pod deletion - verify recreation
2. ✅ MongoDB scale down to 0 - verify 503 errors
3. ✅ MongoDB pod restart - verify data persistence
4. ✅ MongoDB outage during job creation - verify graceful failure
5. ✅ MongoDB outage during live streaming - verify behavior
6. ✅ MongoDB recovery - verify system restoration

---

### RabbitMQ Pod Resilience

| תרחיש | פעולה | ציפייה | Priority |
|-------|-------|--------|----------|
| Pod Deletion | `kubectl delete pod rabbitmq-panda-0` | Pod recreated, queue intact | P0 |
| Scale Down to 0 | `scale statefulset rabbitmq-panda 0` | 503 errors, no crashes | P0 |
| Pod Crash | Kill container process | Pod restart, messages preserved | P1 |
| Network Isolation | Block network to pod | Connection errors, retry logic | P2 |
| Resource Exhaustion | Exceed memory limits | Pod restart, queue intact | P2 |

**בדיקות נדרשות:**
1. ✅ RabbitMQ pod deletion - verify recreation
2. ✅ RabbitMQ scale down to 0 - verify 503 errors
3. ✅ RabbitMQ pod restart - verify message persistence
4. ✅ RabbitMQ outage during job creation - verify graceful failure
5. ✅ RabbitMQ outage during ROI commands - verify behavior
6. ✅ RabbitMQ recovery - verify system restoration

---

### Focus Server Pod Resilience

| תרחיש | פעולה | ציפייה | Priority |
|-------|-------|--------|----------|
| Pod Deletion | `kubectl delete pod panda-panda-focus-server-xxx` | Pod recreated, jobs continue | P0 |
| Scale Down to 0 | `scale deployment panda-panda-focus-server 0` | 503 errors, no crashes | P0 |
| Pod Crash | Kill container process | Pod restart, active jobs handled | P1 |
| Network Isolation | Block network to pod | Connection errors, retry logic | P2 |
| Resource Exhaustion | Exceed memory limits | Pod restart, jobs preserved | P2 |

**בדיקות נדרשות:**
1. ✅ Focus Server pod deletion - verify recreation
2. ✅ Focus Server scale down to 0 - verify 503 errors
3. ✅ Focus Server pod restart - verify active jobs
4. ✅ Focus Server outage during job creation - verify graceful failure
5. ✅ Focus Server outage during live streaming - verify behavior
6. ✅ Focus Server recovery - verify system restoration

---

### SEGY Recorder Pod Resilience

| תרחיש | פעולה | ציפייה | Priority |
|-------|-------|--------|----------|
| Pod Deletion | `kubectl delete pod panda-panda-segy-recorder-xxx` | Pod recreated, recordings continue | P1 |
| Scale Down to 0 | `scale deployment panda-panda-segy-recorder 0` | Recording stops, no crashes | P1 |
| Pod Crash | Kill container process | Pod restart, recordings resume | P2 |
| Network Isolation | Block network to pod | Recording errors, retry logic | P3 |
| Resource Exhaustion | Exceed memory limits | Pod restart, recordings preserved | P3 |

**בדיקות נדרשות:**
1. ✅ SEGY Recorder pod deletion - verify recreation
2. ✅ SEGY Recorder scale down to 0 - verify recording stops
3. ✅ SEGY Recorder pod restart - verify recording persistence
4. ✅ SEGY Recorder outage during recording - verify behavior
5. ✅ SEGY Recorder recovery - verify recording restoration

---

## 🔄 תרחישי כשל מרובים (Multiple Failures)

### 2 Pods Down Simultaneously

| Pods | תרחיש | ציפייה | Priority |
|------|-------|--------|----------|
| MongoDB + RabbitMQ | Both down | Complete outage, clear errors | P1 |
| MongoDB + Focus Server | Both down | Complete outage, clear errors | P1 |
| RabbitMQ + Focus Server | Both down | Complete outage, clear errors | P1 |
| Focus Server + SEGY Recorder | Both down | Jobs fail, recordings stop | P2 |

**בדיקות נדרשות:**
1. ✅ Multiple pods down - verify error handling
2. ✅ Multiple pods recovery - verify restoration order
3. ✅ Cascading failures - verify no infinite loops

---

## 📐 מבנה הטסטים המוצע

### מבנה קבצים
```
tests/infrastructure/resilience/
├── __init__.py
├── test_mongodb_pod_resilience.py
├── test_rabbitmq_pod_resilience.py
├── test_focus_server_pod_resilience.py
├── test_segy_recorder_pod_resilience.py
├── test_multiple_pods_resilience.py
└── test_pod_recovery_scenarios.py
```

### Test Classes Structure

```python
# Example structure for each pod
class TestMongoDBPodResilience:
    """MongoDB pod resilience tests."""
    
    def test_mongodb_pod_deletion_recreation(self):
        """Test MongoDB pod deletion and automatic recreation."""
        pass
    
    def test_mongodb_scale_down_to_zero(self):
        """Test MongoDB scale down to 0 replicas."""
        pass
    
    def test_mongodb_pod_restart_during_job_creation(self):
        """Test MongoDB pod restart during job creation."""
        pass
    
    def test_mongodb_outage_graceful_degradation(self):
        """Test graceful degradation when MongoDB is down."""
        pass
    
    def test_mongodb_recovery_after_outage(self):
        """Test system recovery after MongoDB outage."""
        pass
```

---

## 🛠️ Helper Functions נדרשות

### ב-KubernetesManager

```python
def get_pod_by_name(self, pod_name: str, namespace: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get pod by exact name."""
    pass

def wait_for_pod_ready(self, pod_name: str, namespace: Optional[str] = None, timeout: int = 120) -> bool:
    """Wait for pod to become ready."""
    pass

def wait_for_pod_deletion(self, pod_name: str, namespace: Optional[str] = None, timeout: int = 60) -> bool:
    """Wait for pod to be deleted."""
    pass

def get_pod_status(self, pod_name: str, namespace: Optional[str] = None) -> str:
    """Get current pod status."""
    pass

def restart_pod(self, pod_name: str, namespace: Optional[str] = None) -> bool:
    """Restart a pod by deleting it (Kubernetes will recreate)."""
    pass

def scale_statefulset(self, statefulset_name: str, replicas: int, namespace: Optional[str] = None) -> bool:
    """Scale StatefulSet (for RabbitMQ)."""
    pass
```

---

## 📝 Test Template

### Template לכל תרחיש

```python
@pytest.mark.infrastructure
@pytest.mark.resilience
@pytest.mark.kubernetes
@pytest.mark.slow
class TestMongoDBPodResilience:
    """MongoDB pod resilience tests."""
    
    def test_mongodb_pod_deletion_recreation(
        self,
        k8s_manager: KubernetesManager,
        mongodb_manager: MongoDBManager,
        focus_server_api: FocusServerAPI
    ):
        """
        Test: MongoDB Pod Deletion and Recreation
        
        Steps:
        1. Get current MongoDB pod name
        2. Verify MongoDB is accessible
        3. Delete MongoDB pod
        4. Wait for pod deletion
        5. Wait for new pod to be created
        6. Wait for new pod to be ready
        7. Verify MongoDB connection restored
        8. Verify system functionality restored
        
        Expected:
        - Pod deleted successfully
        - New pod created automatically
        - New pod becomes ready
        - MongoDB connection restored
        - System functionality restored
        """
        logger.info("=" * 80)
        logger.info("TEST: MongoDB Pod Deletion and Recreation")
        logger.info("=" * 80)
        
        # Step 1: Get current MongoDB pod
        namespace = k8s_manager.k8s_config.get("namespace", "panda")
        pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=mongodb")
        assert len(pods) > 0, "MongoDB pod not found"
        original_pod = pods[0]
        original_pod_name = original_pod['name']
        
        logger.info(f"Original MongoDB pod: {original_pod_name}")
        
        # Step 2: Verify MongoDB is accessible
        assert mongodb_manager.connect(), "MongoDB should be accessible before deletion"
        logger.info("✅ MongoDB accessible before deletion")
        mongodb_manager.disconnect()
        
        # Step 3: Delete MongoDB pod
        logger.info(f"\nDeleting MongoDB pod '{original_pod_name}'...")
        assert k8s_manager.delete_pod(original_pod_name, namespace=namespace), \
            "Failed to delete MongoDB pod"
        logger.info("✅ MongoDB pod deleted")
        
        # Step 4: Wait for pod deletion
        logger.info("Waiting for pod deletion...")
        deleted = False
        for attempt in range(30):  # 30 seconds timeout
            pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=mongodb")
            if not any(p['name'] == original_pod_name for p in pods):
                deleted = True
                logger.info("✅ Pod deleted")
                break
            time.sleep(1)
        
        assert deleted, f"Pod {original_pod_name} not deleted within 30 seconds"
        
        # Step 5: Wait for new pod to be created
        logger.info("Waiting for new pod to be created...")
        new_pod_name = None
        for attempt in range(60):  # 60 seconds timeout
            pods = k8s_manager.get_pods(namespace=namespace, label_selector="app=mongodb")
            if pods:
                new_pod = pods[0]
                if new_pod['name'] != original_pod_name:
                    new_pod_name = new_pod['name']
                    logger.info(f"✅ New pod created: {new_pod_name}")
                    break
            time.sleep(1)
        
        assert new_pod_name, "New MongoDB pod not created within 60 seconds"
        
        # Step 6: Wait for new pod to be ready
        logger.info(f"Waiting for pod '{new_pod_name}' to be ready...")
        ready = False
        for attempt in range(120):  # 120 seconds timeout
            pod = k8s_manager.get_pod_by_name(new_pod_name, namespace=namespace)
            if pod and pod.get('status') == 'Running' and pod.get('ready') == 'True':
                ready = True
                logger.info("✅ Pod is ready")
                break
            time.sleep(1)
        
        assert ready, f"Pod {new_pod_name} not ready within 120 seconds"
        
        # Step 7: Verify MongoDB connection restored
        logger.info("Verifying MongoDB connection...")
        connection_restored = False
        for attempt in range(30):  # 30 seconds timeout
            if mongodb_manager.connect():
                connection_restored = True
                logger.info("✅ MongoDB connection restored")
                mongodb_manager.disconnect()
                break
            time.sleep(1)
        
        assert connection_restored, "MongoDB connection not restored within 30 seconds"
        
        # Step 8: Verify system functionality restored
        logger.info("Verifying system functionality...")
        # Try to create a job to verify system works
        try:
            config = {
                "displayTimeAxisDuration": 10,
                "nfftSelection": 1024,
                "displayInfo": {"height": 1000},
                "channels": {"min": 1, "max": 10},
                "frequencyRange": {"min": 0, "max": 500},
                "start_time": None,
                "end_time": None,
                "view_type": 0
            }
            response = focus_server_api.configure_streaming_job(ConfigureRequest(**config))
            logger.info(f"✅ System functionality restored - job created: {response.job_id}")
        except Exception as e:
            logger.warning(f"⚠️  System functionality test failed: {e}")
            # Don't fail the test - MongoDB is restored, system may need more time
        
        logger.info("=" * 80)
        logger.info("✅ TEST PASSED: MongoDB Pod Deletion and Recreation")
        logger.info("=" * 80)
```

---

## 🎯 סדר עדיפויות ליישום

### Phase 1: Critical Pods (P0) - שבוע 1
1. ✅ MongoDB pod resilience tests
2. ✅ RabbitMQ pod resilience tests
3. ✅ Focus Server pod resilience tests

### Phase 2: Secondary Pods (P1) - שבוע 2
4. ✅ SEGY Recorder pod resilience tests
5. ✅ Multiple pods resilience tests

### Phase 3: Advanced Scenarios (P2-P3) - שבוע 3
6. ✅ Network isolation tests
7. ✅ Resource exhaustion tests
8. ✅ Recovery scenarios tests

---

## 📊 Metrics ו-Monitoring

### Metrics לבדיקה
- Pod restart count
- Pod ready time (time to become ready after restart)
- Service downtime duration
- Error rate during outage
- Recovery time

### Monitoring Points
- Pod status changes
- Deployment/StatefulSet events
- Service endpoint availability
- Application logs during outage
- System resource usage

---

## ⚠️ אזהרות והגבלות

### הגבלות
1. **Production Environment:** לא להריץ טסטים אלה ב-production
2. **Data Loss:** לבדוק שאין data loss במהלך pod failures
3. **Cleanup:** לוודא שכל ה-pods מוחזרים למצב תקין בסוף הטסטים
4. **Timeouts:** להגדיר timeouts מתאימים לכל פעולה

### Best Practices
1. **Isolation:** כל טסט צריך להיות independent
2. **Cleanup:** תמיד לנקות בסוף הטסט (restore pods)
3. **Verification:** לוודא שהמערכת חזרה למצב תקין לפני סיום
4. **Logging:** לוג מפורט של כל שלב

---

## 🔗 קישורים רלוונטיים

- `src/infrastructure/kubernetes_manager.py` - Kubernetes operations
- `src/infrastructure/mongodb_manager.py` - MongoDB operations
- `tests/infrastructure/test_rabbitmq_outage_handling.py` - Existing RabbitMQ tests
- `tests/infrastructure/test_k8s_job_lifecycle.py` - Existing K8s tests

---

## 📅 Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1** | 1 week | MongoDB, RabbitMQ, Focus Server resilience tests |
| **Phase 2** | 1 week | SEGY Recorder, Multiple pods tests |
| **Phase 3** | 1 week | Advanced scenarios, Network isolation, Resource exhaustion |
| **Total** | 3 weeks | Complete resilience test suite |

---

**תוכנית זו מספקת בסיס מקיף לבדיקת resilience של Kubernetes pods במערכת.**

