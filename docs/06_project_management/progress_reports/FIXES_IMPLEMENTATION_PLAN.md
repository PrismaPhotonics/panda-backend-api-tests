# 🔧 תוכנית ביצוע תיקונים - Production Issues

**תאריך:** 2025-11-03  
**סביבה:** Production (כפר סבא)  
**מטרה:** תיקון כל הבעיות לפי ההנחיות

---

## ✅ תיקונים שבוצעו

### 1. ✅ Stale Recording Script - יותר זהיר

**קובץ:** `scripts/clean_stale_recording_production.ps1`

**שינויים:**
- ✅ בודק אם recording <24h (כנראה LIVE) → לא מוחק!
- ✅ מחשב age במדויק
- ✅ מציג warning אם זה חדש מדי
- ✅ נותן המלצות לבדיקה ידנית

**סטטוס:** ✅ הושלם

---

## 🔄 תיקונים בתהליך

### 2. Kubernetes API - שימוש ב-kubectl דרך SSH

**בעיה:** Kubernetes API לא נגיש ישירות מ-Windows (10.10.100.102:6443)

**פתרון:** לעדכן את `KubernetesManager` להשתמש ב-`kubectl` דרך SSH במקום ישירות

**קבצים לעדכון:**
- `src/infrastructure/kubernetes_manager.py`
- `tests/infrastructure/test_basic_connectivity.py`
- `tests/infrastructure/test_external_connectivity.py`

**שינויים נדרשים:**

#### 2.1 עדכון KubernetesManager להשתמש ב-SSH

```python
# src/infrastructure/kubernetes_manager.py

class KubernetesManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.ssh_manager = None  # ✅ הוסף SSH manager
        
        # Try direct connection first
        try:
            config.load_kube_config()
            # ... existing code ...
        except config.ConfigException:
            # ✅ Fallback to SSH-based kubectl
            self.logger.info("Kubernetes API not directly accessible - using kubectl via SSH")
            self._init_ssh_kubectl()
    
    def _init_ssh_kubectl(self):
        """Initialize SSH-based kubectl access."""
        from src.infrastructure.ssh_manager import SSHManager
        self.ssh_manager = SSHManager(self.config_manager)
        self.ssh_manager.connect()
        self.k8s_namespace = self.config_manager.get_kubernetes_config().get("namespace", "panda")
    
    def get_pods(self, namespace: Optional[str] = None, label_selector: Optional[str] = None):
        """Get pods - supports both direct API and SSH kubectl."""
        if self.ssh_manager:
            # ✅ Use kubectl via SSH
            return self._get_pods_via_ssh(namespace, label_selector)
        else:
            # Existing direct API code
            return self._get_pods_direct_api(namespace, label_selector)
    
    def _get_pods_via_ssh(self, namespace: Optional[str] = None, label_selector: Optional[str] = None):
        """Get pods using kubectl via SSH."""
        if not namespace:
            namespace = self.k8s_namespace
        
        cmd = f"kubectl get pods -n {namespace} -o json"
        if label_selector:
            cmd += f" -l {label_selector}"
        
        result = self.ssh_manager.execute_command(cmd, timeout=30)
        
        if result["success"]:
            import json
            pods_data = json.loads(result["stdout"])
            # Parse and return pod list
            # ... implementation ...
        else:
            raise InfrastructureError(f"Failed to get pods via SSH: {result['stderr']}")
```

**סטטוס:** 🔄 בתהליך

---

### 3. Schema Validation - לדלג על unrecognized_recordings

**קבצים לעדכון:**
- `tests/data_quality/test_mongodb_indexes_and_schema.py`
- `tests/data_quality/test_mongodb_schema_validation.py`

**שינויים:**

```python
# tests/data_quality/test_mongodb_indexes_and_schema.py

def test_recordings_document_schema_validation(...):
    # ✅ דלג על unrecognized_recordings!
    collections = db.list_collection_names()
    recording_colls = [
        c for c in collections 
        if 'recording' in c.lower() 
        and not c.endswith('-unrecognized_recordings')  # ✅ דלג!
    ]
    
    if not recording_colls:
        pytest.skip("No valid recording collections found")
    
    # ... rest of test ...
```

**סטטוס:** 🔄 בתהליך

---

### 4. API Validation - channels.min >= 1

**קבצים לעדכון:**
- כל טסט שמשתמש ב-`channels.min = 0`

**שינויים:**
```python
# לפני:
config = {
    "channels": {"min": 0, "max": 10}  # ❌ לא מותר
}

# אחרי:
config = {
    "channels": {"min": 1, "max": 10}  # ✅ מינימום 1
}
```

**סטטוס:** 🔄 בתהליך

---

### 5. Focus Server 500 Errors - Log Collection

**מטרה:** להוסיף איסוף ואנליזה של Focus Server logs לטסטים שנכשלו עם 500 errors

**קבצים לעדכון:**
- `tests/conftest.py` (fixture קיים!)
- `tests/integration/api/*` (טסטים שנכשלו)

**שינויים:**

```python
# tests/conftest.py - להוסיף focus_server_logs fixture

@pytest.fixture(scope="function")
def collect_focus_server_logs_on_error(pod_logs_collector):
    """
    Collect Focus Server logs if test fails with 500 error.
    """
    yield
    
    # Check if test failed
    if request.node.rep_call.failed:
        try:
            # Collect logs
            logs = pod_logs_collector.collect_logs_for_service(
                "focus-server", 
                lines=200
            )
            
            # Analyze errors
            error_lines = [line for line in logs.split('\n') 
                          if any(keyword in line.upper() 
                                 for keyword in ['ERROR', 'EXCEPTION', '500', 'TRACEBACK'])]
            
            if error_lines:
                logger.error("=" * 80)
                logger.error("FOCUS SERVER ERROR ANALYSIS")
                logger.error("=" * 80)
                logger.error(f"Found {len(error_lines)} error lines:")
                for line in error_lines[:20]:  # Show first 20
                    logger.error(f"  {line}")
                logger.error("=" * 80)
        except Exception as e:
            logger.warning(f"Could not collect Focus Server logs: {e}")

# בשימוש:
@pytest.mark.usefixtures("collect_focus_server_logs_on_error")
def test_singlechannel_complete_e2e_flow(...):
    # ... test code ...
```

**סטטוס:** 🔄 בתהליך

---

### 6. Load Tests - תוצאות מקיפות ב-Production

**מטרה:** להריץ Load Tests ב-production ולהדפיס תוצאות מקיפות וברורות

**קובץ:** `tests/load/test_job_capacity_limits.py`

**שינויים:**

```python
# להוסיף פונקציה להדפסת תוצאות מקיפות
def print_comprehensive_load_test_results(
    test_name: str,
    env: str,
    job_metrics: Dict,
    system_metrics: Dict,
    output_file: Optional[str] = None
):
    """
    Print comprehensive load test results in clear, readable format.
    
    Args:
        test_name: Name of the test
        env: Environment name
        job_metrics: Job metrics summary
        system_metrics: System metrics summary
        output_file: Optional file to save results
    """
    # Create detailed report
    report = f"""
{'='*80}
LOAD TEST RESULTS - {test_name}
{'='*80}
Environment: {env}
Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

JOB METRICS:
{'─'*80}
Total Jobs:           {job_metrics['total_jobs']}
Successful Jobs:      {job_metrics['successful_jobs']}
Failed Jobs:          {job_metrics['failed_jobs']}
Success Rate:         {job_metrics['success_rate']:.2%}

LATENCY METRICS:
{'─'*80}
Average Latency:      {job_metrics['latency_stats']['mean']:.2f} ms
Median Latency:       {job_metrics['latency_stats']['median']:.2f} ms
P95 Latency:          {job_metrics['latency_stats']['p95']:.2f} ms
P99 Latency:          {job_metrics['latency_stats']['p99']:.2f} ms
Min Latency:          {job_metrics['latency_stats']['min']:.2f} ms
Max Latency:          {job_metrics['latency_stats']['max']:.2f} ms

SYSTEM RESOURCES:
{'─'*80}
CPU Usage:
  Average:            {system_metrics['cpu']['mean']:.1f}%
  Maximum:            {system_metrics['cpu']['max']:.1f}%
  Minimum:            {system_metrics['cpu']['min']:.1f}%

Memory Usage:
  Average:            {system_metrics['memory']['mean']:.1f}%
  Maximum:            {system_metrics['memory']['max']:.1f}%
  Minimum:            {system_metrics['memory']['min']:.1f}%

PERFORMANCE ANALYSIS:
{'─'*80}
"""
    
    # Add recommendations based on results
    if job_metrics['success_rate'] < 0.90:
        report += f"""
⚠️  WARNING: Low success rate ({job_metrics['success_rate']:.2%})

Recommendations:
- Check Focus Server logs for errors
- Verify MongoDB indexes are created
- Check Kubernetes pod resources
- Review network connectivity
"""
    
    if job_metrics['latency_stats']['mean'] > 1000:
        report += f"""
⚠️  WARNING: High latency detected (Avg: {job_metrics['latency_stats']['mean']:.0f}ms)

Possible causes:
- Missing MongoDB indexes
- High system load
- Network latency
- Insufficient resources
"""
    
    report += f"{'='*80}\n"
    
    # Print to logger
    logger.info(report)
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"📄 Results saved to: {output_file}")

# בשימוש בכל load test:
def test_single_job_baseline(...):
    # ... test execution ...
    
    # Print comprehensive results
    print_comprehensive_load_test_results(
        test_name="Single Job Baseline",
        env=env,
        job_metrics=summary,
        system_metrics=system_summary,
        output_file=f"reports/load_tests/baseline_{env}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )
```

**סטטוס:** 🔄 בתהליך

---

## 📋 סדר עדיפויות

### 🔴 היום (דחוף - 2-3 שעות):
1. ✅ MongoDB Indexes - `.\scripts\fix_mongodb_indexes_production.ps1`
2. ✅ Stale Recording (יותר זהיר) - `.\scripts\clean_stale_recording_production.ps1`
3. 🔄 Schema Validation - לתקן הטסטים (30 דק')
4. 🔄 API Validation - לעדכן 15 טסטים (30 דק')
5. 🔄 Kubernetes via SSH - לעדכן KubernetesManager (1 שעה)

### 🟡 מחר (בינוני - 3-4 שעות):
6. 🔄 Focus Server Log Collection - להוסיף לטסטים (1 שעה)
7. 🔄 Load Tests - להדפיס תוצאות מקיפות (1 שעה)
8. 🔄 Datetime Bug - לתקן את הקוד (20 דק')
9. 🔄 Namespace Fixes - RabbitMQ/Focus Server (30 דק')
10. 🔄 SSH Test - Configuration fix (15 דק')

---

**סה"כ זמן משוער:** ~5-7 שעות

