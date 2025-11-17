# פקודות להרצת טסטים מטיקט PZ-14592

## אפשרות 1: הרצה לפי קבצים (מומלץ - פשוט ומהיר)

```powershell
# הפעלת הסביבה הוירטואלית
.venv\Scripts\Activate.ps1

# הרצת כל הטסטים מהקבצים הרלוונטיים
pytest tests/integration/api/test_api_endpoints_high_priority.py tests/integration/api/test_api_endpoints_additional.py tests/infrastructure/test_external_connectivity.py -v -s
```

או בשורה אחת:
```powershell
pytest tests/integration/api/test_api_endpoints_high_priority.py tests/integration/api/test_api_endpoints_additional.py tests/infrastructure/test_external_connectivity.py -v -s
```

## אפשרות 2: הרצה לפי Xray IDs (לא עובד - pytest לא תומך בסינון לפי ערכי markers)

**הערה:** `-k` מחפש בשם הפונקציה, לא ב-Xray markers. לכן הפקודה הזו לא תעבוד.

**השתמש באפשרות 1 (לפי קבצים) - זה הפתרון הנכון!**

## אפשרות 3: הרצה עם דוח HTML

```powershell
pytest tests/integration/api/test_api_endpoints_high_priority.py tests/integration/api/test_api_endpoints_additional.py tests/infrastructure/test_external_connectivity.py -v --html=reports/PZ-14592_test_report.html --self-contained-html
```

## אפשרות 4: הרצה עם Xray integration (ריפורט ל-Jira)

```powershell
pytest --xray --xray-execution-id="PZ-14592-EXEC-$(Get-Date -Format 'yyyyMMdd-HHmmss')" tests/integration/api/test_api_endpoints_high_priority.py tests/integration/api/test_api_endpoints_additional.py tests/infrastructure/test_external_connectivity.py -v
```

## פירוט הטסטים שירוצו:

### מתוך test_api_endpoints_high_priority.py:
- PZ-13895, PZ-13762, PZ-13560 (test_get_channels_endpoint_success)
- PZ-13896 (test_get_channels_endpoint_response_time)
- PZ-13897 (test_get_channels_endpoint_multiple_calls_consistency)
- PZ-13898 (test_get_channels_endpoint_channel_ids_sequential)
- PZ-13899 (test_get_channels_endpoint_enabled_status)

### מתוך test_api_endpoints_additional.py:
- PZ-13897 (test_get_sensors_endpoint)
- PZ-13563 (test_get_metadata_by_job_id)
- PZ-13552 (test_invalid_time_range_rejection)
- PZ-13554 (test_invalid_channel_range_rejection)
- PZ-13555 (test_invalid_frequency_range_rejection)

### מתוך test_external_connectivity.py:
- PZ-13898 (test_external_api_connectivity)
- PZ-13899 (test_external_api_response_validation)

**סה"כ: 11 טסטים (כל מפתחות ה-Xray מטיקט PZ-14592)**

