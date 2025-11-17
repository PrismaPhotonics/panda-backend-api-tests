# Missing Tests in Automation - Detailed Breakdown

**Total Missing:** 44 tests

---

## API Tests (22 tests)

| # | Test ID | Summary | Status | Priority | Test Type |
|---|---------|---------|--------|----------|-----------|
| 1 | PZ-13762 | API – GET /channels – Returns System Channel Bounds | TO DO | Medium | Automation |
| 2 | PZ-13552 | API – Invalid time range (negative) | TO DO | Medium | Automation |
| 3 | PZ-13561 | API – GET /live_metadata present | TO DO | Medium | Automation |
| 4 | PZ-14101 | Integration - Historic Playback - Short Duration (Rapid Wind | TO DO | Medium | Automation |
| 5 | PZ-13761 | API – POST /config/{task_id} – Invalid Frequency Range Rejec | TO DO | Medium | Automation |
| 6 | PZ-13821 | API – SingleChannel Rejects Invalid Display Height | TO DO | Medium | Automation |
| 7 | PZ-13766 |  API – POST /recordings_in_time_range – Returns Recording Wi | TO DO | Medium | Automation |
| 8 | PZ-13764 |  API – GET /live_metadata – Returns Metadata When Available | TO DO | Medium | Automation |
| 9 | PZ-13815 | API – SingleChannel View for Channel 100 (Upper Boundary Tes | TO DO | Medium | Automation |
| 10 | PZ-13759 | API – POST /config/{task_id} – Invalid Time Range Rejection | TO DO | Medium | Automation |
| 11 | PZ-13895 | Integration – GET /channels - Enabled Channels List | TO DO | Medium | Automation |
| 12 | PZ-13560 | API – GET /channels | TO DO | Medium | Automation |
| 13 | PZ-13823 | API – SingleChannel Rejects When min ≠ max | TO DO | Medium | Automation |
| 14 | PZ-13819 | API – SingleChannel View with Various Frequency Ranges | TO DO | Medium | Automation |
| 15 | PZ-13548 | API – Historical configure (happy path) | TO DO | Medium | Automation |
| 16 | PZ-13765 | API – GET /live_metadata – Returns 404 When Unavailable | TO DO | Medium | Automation |
| 17 | PZ-13554 | API – Invalid channels (negative) | TO DO | Medium | Automation |
| 18 | PZ-13814 | API – SingleChannel View for Channel 1 (First Channel) | TO DO | Medium | Automation |
| 19 | PZ-13562 | API – GET /live_metadata missing | TO DO | Medium | Automation |
| 20 | PZ-13555 | API – Invalid frequency range (negative) | TO DO | Medium | Automation |
| 21 | PZ-13760 | API – POST /config/{task_id} – Invalid Channel Range Rejecti | TO DO | Medium | Automation |
| 22 | PZ-13564 | API – POST /recordings_in_time_range | TO DO | Medium | Automation |

## Data Quality Tests (4 tests)

| # | Test ID | Summary | Status | Priority | Test Type |
|---|---------|---------|--------|----------|-----------|
| 1 | PZ-13684 | Data Quality – node4 Schema Validation | TO DO | Medium | Automation |
| 2 | PZ-13811 | Data Quality – Validate Recordings Document Schema | TO DO | Medium | Automation |
| 3 | PZ-13812 | Data Quality – Verify Recordings Have Complete Metadata | TO DO | Medium | Automation |
| 4 | PZ-13685 | Data Quality – Recordings Metadata Completeness | TO DO | Medium | Automation |

## Integration Tests (16 tests)

| # | Test ID | Summary | Status | Priority | Test Type |
|---|---------|---------|--------|----------|-----------|
| 1 | PZ-13832 | Integration - SingleChannel Edge Case - Minimum Channel (Cha | TO DO | Medium | Automation |
| 2 | PZ-13603 | Integration – Mongo outage on History configure | TO DO | Medium | Automation |
| 3 | PZ-13863 | Integration – Historic Playback - Standard 5-Minute Range | TO DO | Medium | Automation |
| 4 | PZ-13865 | Integration – Historic Playback - Short Duration (1 Minute) | TO DO | Medium | Automation |
| 5 | PZ-13767 | Integration – MongoDB Outage Handling | TO DO | Medium | Automation |
| 6 | PZ-13877 | Integration – Invalid Frequency Range - Min > Max | TO DO | Medium | Automation |
| 7 | PZ-13836 | Integration - SingleChannel with Invalid Channel (Negative) | TO DO | Medium | Automation |
| 8 | PZ-13833 | Integration - SingleChannel Edge Case - Maximum Channel (Las | TO DO | Medium | Automation |
| 9 | PZ-13854 | Integration - SingleChannel Frequency Range Validation | TO DO | Medium | Automation |
| 10 | PZ-13604 | Integration – Orchestrator error triggers rollback | TO DO | Medium | Automation |
| 11 | PZ-13852 | Integration - SingleChannel with Min > Max (Validation Error | TO DO | Medium | Automation |
| 12 | PZ-13837 | Integration - SingleChannel with Invalid Channel (Negative) | TO DO | Medium | Automation |
| 13 | PZ-13855 | Integration - SingleChannel Canvas Height Validation | TO DO | Medium | Automation |
| 14 | PZ-13835 | Integration - SingleChannel with Invalid Channel (Out of Ran | TO DO | Medium | Automation |
| 15 | PZ-13873 | integration - Valid Configuration - All Parameters | TO DO | Medium | Automation |
| 16 | PZ-13903 | Integration - Frequency Range Nyquist Limit Enforcement | TO DO | Medium | Automation |

## Security Tests (2 tests)

| # | Test ID | Summary | Status | Priority | Test Type |
|---|---------|---------|--------|----------|-----------|
| 1 | PZ-13769 | Security – Malformed Input Handling | TO DO | Medium | Automation |
| 2 | PZ-13572 | Security – Robustness to malformed inputs | TO DO | Medium | Automation |

