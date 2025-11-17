# 🚀 פקודה פשוטה להרצת טסטי K8s Job Lifecycle

## מתוך תיקיית הפרויקט:

```bash
pytest be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py -v --skip-health-check --log-cli-level=INFO
```

או עם Python:

```bash
python -m pytest be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py -v --skip-health-check --log-cli-level=INFO
```

---

## לבדוק תוצאות:

```bash
# לראות כמה עברו
pytest be_focus_server_tests/infrastructure/test_k8s_job_lifecycle.py -v --skip-health-check --tb=line | grep -E "passed|failed|skipped"

# לראות לוגים
tail -100 logs/test_runs/*.log
```

