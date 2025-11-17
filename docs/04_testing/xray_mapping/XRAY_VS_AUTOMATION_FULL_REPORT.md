# Xray vs Automation - Complete Analysis
**Generated:** C:\Projects\focus_server_automation

## Summary

- Tests in xray_tests_list.txt: **126**
- Tests in automation: **114**
- Common tests: **98**
- In Xray but NOT in automation: **28**
- In automation but NOT in Xray: **16**

## ⚠️ Tests in xray_tests_list.txt but NOT in Automation

**Total: 28 tests**

These tests need automation implementation:

| Test ID | Description |
|---------|-------------|
| PZ-13903 | Integration - Frequency Range Nyquist Limit Enforcement |
| PZ-13873 | integration - Valid Configuration - All Parameters |
| PZ-13865 | Integration – Historic Playback - Short Duration (1 Minute) |
| PZ-13863 | Integration – Historic Playback - Standard 5-Minute Range |
| PZ-13857 | Integration - SingleChannel NFFT Validation |
| PZ-13855 | Integration - SingleChannel Canvas Height Validation |
| PZ-13854 | Integration - SingleChannel Frequency Range Validation |
| PZ-13852 | Integration - SingleChannel with Min > Max (Validation Error) |
| PZ-13837 | Integration - SingleChannel with Invalid Channel (Negative) |
| PZ-13836 | Integration - SingleChannel with Invalid Channel (Negative) |
| PZ-13833 | Integration - SingleChannel Edge Case - Maximum Channel (Last Available) |
| PZ-13832 | Integration - SingleChannel Edge Case - Minimum Channel (Channel 0) |
| PZ-13822 | API – SingleChannel Rejects Invalid NFFT Value |
| PZ-13769 | Security – Malformed Input Handling |
| PZ-13766 | API – POST /recordings_in_time_range – Returns Recording Windows |
| PZ-13762 | API – GET /channels – Returns System Channel Bounds |
| PZ-13685 | Data Quality – Recordings Metadata Completenessאיפה הם מקיימים? |
| PZ-13684 | Data Quality – node4 Schema Validation |
| PZ-13604 | Integration – Orchestrator error triggers rollback |
| PZ-13603 | Integration – Mongo outage on History configure |
| PZ-13601 | Integration – History with empty window returns 400 and no side effects |
| PZ-13600 | Integration – Invalid configure does not launch orchestration |
| PZ-13562 | API – GET /live_metadata missing |
| PZ-13561 | API – GET /live_metadata present |
| PZ-13560 | API – GET /channels |
| PZ-13555 | API – Invalid frequency range (negative) |
| PZ-13554 | API – Invalid channels (negative) |
| PZ-13552 | API – Invalid time range (negative) |

## ⚠️ Tests in Automation but NOT in xray_tests_list.txt

**Total: 16 tests**

These tests exist in automation but are missing from Xray list:

| Test ID | Status |
|---------|--------|
| PZ-1234 | ⚠️ Missing from Xray list |
| PZ-13864 | ⚠️ Missing from Xray list |
| PZ-13902 | ⚠️ Missing from Xray list |
| PZ-13908 | ⚠️ Missing from Xray list |
| PZ-13910 | ⚠️ Missing from Xray list |
| PZ-13911 | ⚠️ Missing from Xray list |
| PZ-13912 | ⚠️ Missing from Xray list |
| PZ-13913 | ⚠️ Missing from Xray list |
| PZ-13914 | ⚠️ Missing from Xray list |
| PZ-13920 | ⚠️ Missing from Xray list |
| PZ-13921 | ⚠️ Missing from Xray list |
| PZ-13922 | ⚠️ Missing from Xray list |
| PZ-13984 | ⚠️ Missing from Xray list |
| PZ-13986 | ⚠️ Missing from Xray list |
| PZ-14033 | ⚠️ Missing from Xray list |
| PZ-2001 | ⚠️ Missing from Xray list |

**Recommendation:** Add these to xray_tests_list.txt or remove from automation

## ✅ Common Tests

**Total: 98 tests that are in both**

