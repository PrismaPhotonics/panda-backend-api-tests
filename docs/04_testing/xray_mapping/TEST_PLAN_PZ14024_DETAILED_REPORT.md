# Test Plan: PZ-14024 - Complete Test List

**Source:** Jira CSV Export
**Total Tests:** 237
**Generated:** 1762691860.9703312

---

## Test Cases

| # | Test ID | Summary | Status | Test Type | Priority |
|---|---------|---------|--------|-----------|----------|
| 1 | PZ-13547 | API – POST /config/{task_id} – Live Mode Configuration (Happy Path) | TO DO | Automation | Medium |
| 2 | PZ-13548 | API – Historical configure (happy path) | TO DO | Automation | Medium |
| 3 | PZ-13552 | API – Invalid time range (negative) | TO DO | Automation | Medium |
| 4 | PZ-13554 | API – Invalid channels (negative) | TO DO | Automation | Medium |
| 5 | PZ-13555 | API – Invalid frequency range (negative) | TO DO | Automation | Medium |
| 6 | PZ-13557 | API – Waterfall view handling | TO DO | Automation | Medium |
| 7 | PZ-13558 | API - Overlap/NFFT Escalation Edge Case | TO DO | Automation | Medium |
| 8 | PZ-13560 | API – GET /channels | TO DO | Automation | Medium |
| 9 | PZ-13561 | API – GET /live_metadata present | TO DO | Automation | Medium |
| 10 | PZ-13562 | API – GET /live_metadata missing | TO DO | Automation | Medium |
| 11 | PZ-13563 | API - GET /metadata/{job_id} - Valid and Invalid Job ID | TO DO | Automation | Medium |
| 12 | PZ-13564 | API – POST /recordings_in_time_range | TO DO | Automation | Medium |
| 13 | PZ-13570 | E2E – Configure → Metadata → gRPC (mock) | TO DO | Automation | Medium |
| 14 | PZ-13572 | Security – Robustness to malformed inputs | TO DO | Automation | Medium |
| 15 | PZ-13598 | Data Quality – Mongo collections and schema | TO DO | Automation | Medium |
| 16 | PZ-13602 | Integration – RabbitMQ outage on Live configure | TO DO | Automation | Medium |
| 17 | PZ-13603 | Integration – Mongo outage on History configure | TO DO | Automation | Medium |
| 18 | PZ-13604 | Integration – Orchestrator error triggers rollback | TO DO | Automation | Medium |
| 19 | PZ-13683 | Data Quality – MongoDB Collections Exist | TO DO | Automation | Medium |
| 20 | PZ-13684 | Data Quality – node4 Schema Validation | TO DO | Automation | Medium |
| 21 | PZ-13685 | Data Quality – Recordings Metadata Completeness | TO DO | Automation | Medium |
| 22 | PZ-13686 | Data Quality – MongoDB Indexes Validation | TO DO | Automation | Medium |
| 23 | PZ-13687 | MongoDB Recovery – Recordings Indexed After Outage | TO DO | Automation | Medium |
| 24 | PZ-13705 | Data Lifecycle – Historical vs Live Recordings Classification | TO DO | Automation | Medium |
| 25 | PZ-13759 | API – POST /config/{task_id} – Invalid Time Range Rejection | TO DO | Automation | Medium |
| 26 | PZ-13760 | API – POST /config/{task_id} – Invalid Channel Range Rejection | TO DO | Automation | Medium |
| 27 | PZ-13761 | API – POST /config/{task_id} – Invalid Frequency Range Rejection | TO DO | Automation | Medium |
| 28 | PZ-13762 | API – GET /channels – Returns System Channel Bounds | TO DO | Automation | Medium |
| 29 | PZ-13764 |  API – GET /live_metadata – Returns Metadata When Available | TO DO | Automation | Medium |
| 30 | PZ-13765 | API – GET /live_metadata – Returns 404 When Unavailable | TO DO | Automation | Medium |
| 31 | PZ-13766 |  API – POST /recordings_in_time_range – Returns Recording Windows | TO DO | Automation | Medium |
| 32 | PZ-13767 | Integration – MongoDB Outage Handling | TO DO | Automation | Medium |
| 33 | PZ-13769 | Security – Malformed Input Handling | TO DO | Automation | Medium |
| 34 | PZ-13784 | Integration - Send ROI Change Command via RabbitMQ | TO DO | Automation | Medium |
| 35 | PZ-13785 | Integration - ROI Change with Safety Validation | TO DO | Automation | Medium |
| 36 | PZ-13786 | Integration - Multiple ROI Changes in Sequence | TO DO | Automation | Medium |
| 37 | PZ-13787 | Integration -  ROI Expansion (Increase Range) | TO DO | Automation | Medium |
| 38 | PZ-13788 | Integration - ROI Shrinking (Decrease Range) | TO DO | Automation | Medium |
| 39 | PZ-13789 | Integration - ROI Shift (Move Range) | TO DO | Automation | Medium |
| 40 | PZ-13790 | Integration - ROI with Equal Start and End (Zero Size) | TO DO | Automation | Medium |
| 41 | PZ-13791 | Integration - ROI with Reversed Range (Start > End) | TO DO | Automation | Medium |
| 42 | PZ-13792 | Integration - ROI with Negative Start | TO DO | Automation | Medium |
| 43 | PZ-13793 | Integration - Dynamic ROI – Reject ROI with Negative End Value | TO DO | Automation | Medium |
| 44 | PZ-13794 | Integration - ROI with Small Range (Edge Case) | TO DO | Automation | Medium |
| 45 | PZ-13795 | Integration - ROI with Large Range (Edge Case) | TO DO | Automation | Medium |
| 46 | PZ-13796 | Integration - ROI Starting at Zero | TO DO | Automation | Medium |
| 47 | PZ-13797 | Integration - Unsafe ROI Change (Large Jump) | TO DO | Automation | Medium |
| 48 | PZ-13798 | Integration - Unsafe ROI Range Change (Size Change > 50%) | TO DO | Automation | Medium |
| 49 | PZ-13799 | Integration – Unsafe ROI Shift (Large Position Change) | TO DO | Automation | Medium |
| 50 | PZ-13800 | Integration – Safe ROI Change (Within Limits) | TO DO | Automation | Medium |
| 51 | PZ-13806 | Infrastructure - Infrastructure – MongoDB Direct TCP Connection and Authenticati | TO DO | Automation | Medium |
| 52 | PZ-13807 | Infrastructure - Infrastructure – MongoDB Connection Using Focus Server Config | TO DO | Automation | Medium |
| 53 | PZ-13808 | Infrastructure - Infrastructure – MongoDB Quick Response Time Test (Performance) | TO DO | Automation | Medium |
| 54 | PZ-13809 | Data Quality – Verify Required MongoDB Collections Exist | TO DO | Automation | Medium |
| 55 | PZ-13810 | Data Quality – Verify Critical MongoDB Indexes Exist | TO DO | Automation | Medium |
| 56 | PZ-13811 | Data Quality – Validate Recordings Document Schema | TO DO | Automation | Medium |
| 57 | PZ-13812 | Data Quality – Verify Recordings Have Complete Metadata | TO DO | Automation | Medium |
| 58 | PZ-13814 | API – SingleChannel View for Channel 1 (First Channel) | TO DO | Automation | Medium |
| 59 | PZ-13815 | API – SingleChannel View for Channel 100 (Upper Boundary Test) | TO DO | Automation | Medium |
| 60 | PZ-13816 | API – Different SingleChannels Return Different Mappings | TO DO | Automation | Medium |
| 61 | PZ-13817 | API – Same SingleChannel Returns Consistent Mapping Across Multiple Requests | TO DO | Automation | Medium |
| 62 | PZ-13818 | API – Compare SingleChannel vs MultiChannel View Types | TO DO | Automation | Medium |
| 63 | PZ-13819 | API – SingleChannel View with Various Frequency Ranges | TO DO | Automation | Medium |
| 64 | PZ-13820 | API – SingleChannel Rejects Invalid Frequency Range | TO DO | Automation | Medium |
| 65 | PZ-13821 | API – SingleChannel Rejects Invalid Display Height | TO DO | Automation | Medium |
| 66 | PZ-13822 | API – SingleChannel Rejects Invalid NFFT Value | TO DO | Automation | Medium |
| 67 | PZ-13823 | API – SingleChannel Rejects When min ≠ max | TO DO | Automation | Medium |
| 68 | PZ-13824 | API – SingleChannel Rejects Channel Zero | TO DO | Automation | Medium |
| 69 | PZ-13832 | Integration - SingleChannel Edge Case - Minimum Channel (Channel 0) | TO DO | Automation | Medium |
| 70 | PZ-13833 | Integration - SingleChannel Edge Case - Maximum Channel (Last Available) | TO DO | Automation | Medium |
| 71 | PZ-13834 |  Integration - SingleChannel Edge Case - Middle Channel | TO DO | Automation | Medium |
| 72 | PZ-13835 | Integration - SingleChannel with Invalid Channel (Out of Range High) | TO DO | Automation | Medium |
| 73 | PZ-13836 | Integration - SingleChannel with Invalid Channel (Negative) | TO DO | Automation | Medium |
| 74 | PZ-13837 | Integration - SingleChannel with Invalid Channel (Negative) | TO DO | Automation | Medium |
| 75 | PZ-13852 | Integration - SingleChannel with Min > Max (Validation Error) | TO DO | Automation | Medium |
| 76 | PZ-13853 | Integration - SingleChannel Data Consistency Check | TO DO | Automation | Medium |
| 77 | PZ-13854 | Integration - SingleChannel Frequency Range Validation | TO DO | Automation | Medium |
| 78 | PZ-13855 | Integration - SingleChannel Canvas Height Validation | TO DO | Automation | Medium |
| 79 | PZ-13857 | Integration - SingleChannel NFFT Validation | TO DO | Automation | Medium |
| 80 | PZ-13858 | Integration - SingleChannel Rapid Reconfiguration | TO DO | Automation | Medium |
| 81 | PZ-13859 | Integration - SingleChannel Polling Stability | TO DO | Automation | Medium |
| 82 | PZ-13860 | Integration - SingleChannel Metadata Consistency | TO DO | Automation | Medium |
| 83 | PZ-13861 | Integration - SingleChannel Stream Mapping Verification | TO DO | Automation | Medium |
| 84 | PZ-13862 | Integration - SingleChannel Complete Flow End-to-End | TO DO | Automation | Medium |
| 85 | PZ-13863 | Integration – Historic Playback - Standard 5-Minute Range | TO DO | Automation | Medium |
| 86 | PZ-13865 | Integration – Historic Playback - Short Duration (1 Minute) | TO DO | Automation | Medium |
| 87 | PZ-13866 | Integration – Historic Playback - Very Old Timestamps (No Data) | TO DO | Automation | Medium |
| 88 | PZ-13867 | Data Quality – Historic Playback - Data Integrity Validation | TO DO | Automation | Medium |
| 89 | PZ-13868 | Integration – Historic Playback - Status 208 Completion | TO DO | Automation | Medium |
| 90 | PZ-13869 | Integration – Historic Playback - Invalid Time Range (End Before Start) | TO DO | Automation | Medium |
| 91 | PZ-13870 | Integration – Historic Playback - Future Timestamps | TO DO | Automation | Medium |
| 92 | PZ-13871 | Integration – Historic Playback - Timestamp Ordering Validation | TO DO | Automation | Medium |
| 93 | PZ-13872 | Integration – Historic Playback Complete End-to-End Flow | TO DO | Automation | Medium |
| 94 | PZ-13873 | integration - Valid Configuration - All Parameters | TO DO | Automation | Medium |
| 95 | PZ-13874 | Integration – Invalid NFFT - Zero Value | TO DO | Automation | Medium |
| 96 | PZ-13875 | Integration – Invalid NFFT - Negative Value | TO DO | Automation | Medium |
| 97 | PZ-13876 | Integration – Invalid Channel Range - Min > Max | TO DO | Automation | Medium |
| 98 | PZ-13877 | Integration – Invalid Frequency Range - Min > Max | TO DO | Automation | Medium |
| 99 | PZ-13878 | Integration – Invalid View Type - Out of Range | TO DO | Automation | Medium |
| 100 | PZ-13879 | Integration – Missing Required Fields | TO DO | Automation | Medium |
| 101 | PZ-13880 | Stress - Configuration with Extreme Values  | TO DO | Automation | Medium |
| 102 | PZ-13895 | Integration – GET /channels - Enabled Channels List | TO DO | Automation | Medium |
| 103 | PZ-13896 | Performance – Concurrent Task Limit | TO DO | Automation | Medium |
| 104 | PZ-13897 | Integration - GET /sensors - Retrieve Available Sensors List | TO DO | Automation | Medium |
| 105 | PZ-13898 | Infrastructure - MongoDB Direct Connection and Health Check | TO DO | Automation | Medium |
| 106 | PZ-13899 | Infrastructure - Kubernetes Cluster Connection and Pod Health Check | TO DO | Automation | Medium |
| 107 | PZ-13900 | Infrastructure - SSH Access to Production Servers | TO DO | Automation | Medium |
| 108 | PZ-13901 | Integration - NFFT Values Validation - All Supported Values | TO DO | Automation | Medium |
| 109 | PZ-13903 | Integration - Frequency Range Nyquist Limit Enforcement | TO DO | Automation | Medium |
| 110 | PZ-13904 | Integration - Configuration Resource Usage Estimation | TO DO | Automation | Medium |
| 111 | PZ-13905 | Performance - High Throughput Configuration Stress Test | TO DO | Automation | Medium |
| 112 | PZ-13906 | Integration - Low Throughput Configuration Edge Case | TO DO | Automation | Medium |
| 113 | PZ-13907 | Integration - Historic Configuration Missing start_time Field | TO DO | Automation | Medium |
| 114 | PZ-13909 | Integration - Historic Configuration Missing end_time Field | TO DO | Automation | Medium |
| 115 | PZ-14018 | Invalid Configuration Does Not Launch Orchestration | TO DO | Automation | High |
| 116 | PZ-14019 | History with Empty Time Window Returns 400 | TO DO | Automation | Medium |
| 117 | PZ-14026 | API - Health Check Returns Valid Response (200 OK) | TO DO | Automation | Medium |
| 118 | PZ-14027 | API - Health Check Rejects Invalid HTTP Methods | TO DO | Automation | Medium |
| 119 | PZ-14028 | API - Health Check Handles Concurrent Requests | TO DO | Automation | Medium |
| 120 | PZ-14029 | API - Health Check with Various Headers | TO DO | Automation | Medium |
| 121 | PZ-14030 | API - Health Check Security Headers Validation | TO DO | Automation | Medium |
| 122 | PZ-14031 | API - Health Check Response Structure Validation | TO DO | Automation | Medium |
| 123 | PZ-14032 | API - Health Check with SSL/TLS | TO DO | Automation | Medium |
| 124 | PZ-14033 | API - Health Check Load Testing | TO DO | Automation | Medium |
| 125 | PZ-14060 | Integration – Calculation Validation – Frequency Resolution Calculation | TO DO | Automation | Medium |
| 126 | PZ-14061 | Integration – Calculation Validation – Frequency Bins Count Calculation | TO DO | Automation | Medium |
| 127 | PZ-14062 | Integration – Calculation Validation – Nyquist Frequency Limit Validation | TO DO | Automation | Medium |
| 128 | PZ-14066 | Integration – Calculation Validation – Time Resolution (lines_dt) Calculation | TO DO | Automation | Medium |
| 129 | PZ-14067 | Integration – Calculation Validation – Output Rate Calculation | TO DO | Automation | Medium |
| 130 | PZ-14068 | Integration –  Calculation Validation – Time Window Duration Calculation | TO DO | Automation | Medium |
| 131 | PZ-14069 | Integration – Calculation Validation – Channel Count Calculation | TO DO | Automation | Medium |
| 132 | PZ-14070 | Integration – Calculation Validation – MultiChannel Mapping Validation | TO DO | Automation | Medium |
| 133 | PZ-14071 | Integration – Calculation Validation – Stream Amount Calculation | TO DO | Automation | Medium |
| 134 | PZ-14072 | Integration – Validation – FFT Window Size (Power of 2) Validation | TO DO | Automation | Medium |
| 135 | PZ-14073 | Integration – Validation – Overlap Percentage Validation | TO DO | Automation | Medium |
| 136 | PZ-14078 | Performance – Data Rate Calculation (Informational) | TO DO | Automation | Medium |
| 137 | PZ-14079 | Performance – Memory Usage Estimation (Informational) | TO DO | Automation | Medium |
| 138 | PZ-14080 | Historic – Spectrogram Dimensions Calculation | TO DO | Automation | Medium |
| 139 | PZ-14088 | Load - 200 Jobs Capacity Stress Test | TO DO | Automation | Medium |
| 140 | PZ-14089 | Integration - Time Range Validation - Future Timestamps Rejection | TO DO | Automation | Medium |
| 141 | PZ-14090 | Performance - Job Creation Time < 2 Seconds | TO DO | Automation | Medium |
| 142 | PZ-14091 | Performance - Configuration Endpoint P99 Latency | TO DO | Automation | Medium |
| 143 | PZ-14092 | Performance - Configuration Endpoint P95 Latency | TO DO | Automation | Medium |
| 144 | PZ-14093 | Integration - Invalid View Type - Out of Range | TO DO | Automation | Medium |
| 145 | PZ-14094 | Integration - Invalid View Type - String Value | TO DO | Automation | Medium |
| 146 | PZ-14095 | Integration - Configuration Missing displayTimeAxisDuration Field | TO DO | Automation | Medium |
| 147 | PZ-14097 | Integration - Configuration Missing nfftSelection Field | TO DO | Automation | Medium |
| 148 | PZ-14098 | Integration - Configuration Missing frequencyRange Field | TO DO | Automation | Medium |
| 149 | PZ-14099 | Integration - Configuration Missing channels Field | TO DO | Automation | Medium |
| 150 | PZ-14100 | Integration - Frequency Range Within Nyquist Limit | TO DO | Automation | Medium |
| 151 | PZ-14101 | Integration - Historic Playback - Short Duration (Rapid Window) | TO DO | Automation | Medium |
| 152 | PZ-14715 | Infrastructure - MongoDB Pod Deletion and Recreation | TO DO | Automation | Highest |
| 153 | PZ-14716 | Infrastructure - MongoDB Scale Down to 0 Replicas | TO DO | Automation | Highest |
| 154 | PZ-14717 | Infrastructure - MongoDB Pod Restart During Job Creation | TO DO | Automation | High |
| 155 | PZ-14718 | Infrastructure - MongoDB Outage Graceful Degradation | TO DO | Automation | Highest |
| 156 | PZ-14719 | Infrastructure - MongoDB Recovery After Outage | TO DO | Automation | Highest |
| 157 | PZ-14720 | Infrastructure - MongoDB Pod Status Monitoring | TO DO | Automation | Medium |
| 158 | PZ-14721 | Infrastructure - RabbitMQ Pod Deletion and Recreation | TO DO | Automation | Highest |
| 159 | PZ-14722 | Infrastructure - RabbitMQ Scale Down to 0 Replicas | TO DO | Automation | Highest |
| 160 | PZ-14723 | Infrastructure - RabbitMQ Pod Restart During Operations | TO DO | Automation | High |
| 161 | PZ-14724 | Infrastructure - RabbitMQ Outage Graceful Degradation | TO DO | Automation | Highest |
| 162 | PZ-14725 | Infrastructure - RabbitMQ Recovery After Outage | TO DO | Automation | Highest |
| 163 | PZ-14726 | Infrastructure - RabbitMQ Pod Status Monitoring | TO DO | Automation | Medium |
| 164 | PZ-14727 | Infrastructure - Focus Server Pod Deletion and Recreation | TO DO | Automation | Highest |
| 165 | PZ-14728 | Infrastructure - Focus Server Scale Down to 0 Replicas | TO DO | Automation | Highest |
| 166 | PZ-14729 | Infrastructure - Focus Server Pod Restart During Job Creation | TO DO | Automation | High |
| 167 | PZ-14730 | Infrastructure - Focus Server Outage Graceful Degradation | TO DO | Automation | Highest |
| 168 | PZ-14731 | Infrastructure - Focus Server Recovery After Outage | TO DO | Automation | Highest |
| 169 | PZ-14732 | Infrastructure - Focus Server Pod Status Monitoring | TO DO | Automation | Medium |
| 170 | PZ-14733 | Infrastructure - SEGY Recorder Pod Deletion and Recreation | TO DO | Automation | High |
| 171 | PZ-14734 | Infrastructure - SEGY Recorder Scale Down to 0 Replicas | TO DO | Automation | High |
| 172 | PZ-14735 | Infrastructure - SEGY Recorder Pod Restart During Recording | TO DO | Automation | Medium |
| 173 | PZ-14736 | Infrastructure - SEGY Recorder Outage Behavior | TO DO | Automation | Medium |
| 174 | PZ-14737 | Infrastructure - SEGY Recorder Recovery After Outage | TO DO | Automation | High |
| 175 | PZ-14738 | Infrastructure - MongoDB + RabbitMQ Down Simultaneously | TO DO | Automation | High |
| 176 | PZ-14739 | Infrastructure - MongoDB + Focus Server Down Simultaneously | TO DO | Automation | High |
| 177 | PZ-14740 | Infrastructure - RabbitMQ + Focus Server Down Simultaneously | TO DO | Automation | High |
| 178 | PZ-14741 | Infrastructure - Focus Server + SEGY Recorder Down Simultaneously | TO DO | Automation | Medium |
| 179 | PZ-14742 | Infrastructure - Recovery Order Validation | TO DO | Automation | High |
| 180 | PZ-14743 | Infrastructure - Cascading Recovery Scenarios | TO DO | Automation | Medium |
| 181 | PZ-14744 | Infrastructure - Recovery Time Measurement | TO DO | Automation | Medium |
| 182 | PZ-14750 | API - POST /config/{task_id} - Valid Configuration | TO DO | Automation | High |
| 183 | PZ-14751 | API - POST /config/{task_id} - Invalid Task ID | TO DO | Automation | High |
| 184 | PZ-14752 | API - POST /config/{task_id} - Missing Required Fields | TO DO | Automation | High |
| 185 | PZ-14753 | API - POST /config/{task_id} - Invalid Sensor Range | TO DO | Automation | Medium |
| 186 | PZ-14754 | API - POST /config/{task_id} - Invalid Frequency Range | TO DO | Automation | Medium |
| 187 | PZ-14755 | API - GET /waterfall/{task_id}/{row_count} - Valid Request | TO DO | Automation | High |
| 188 | PZ-14756 | API - GET /waterfall/{task_id}/{row_count} - No Data Available | TO DO | Automation | Medium |
| 189 | PZ-14757 | API - GET /waterfall/{task_id}/{row_count} - Invalid Task ID | TO DO | Automation | High |
| 190 | PZ-14758 | API - GET /waterfall/{task_id}/{row_count} - Invalid Row Count | TO DO | Automation | Medium |
| 191 | PZ-14759 | API - GET /waterfall/{task_id}/{row_count} - Baby Analyzer Exited | TO DO | Automation | Medium |
| 192 | PZ-14760 | API - GET /metadata/{task_id} - Valid Request | TO DO | Automation | High |
| 193 | PZ-14761 | API - GET /metadata/{task_id} - Consumer Not Running | TO DO | Automation | Medium |
| 194 | PZ-14762 | API - GET /metadata/{task_id} - Invalid Task ID | TO DO | Automation | High |
| 195 | PZ-14763 | API - GET /metadata/{task_id} - Metadata Consistency | TO DO | Automation | Medium |
| 196 | PZ-14764 | API - GET /metadata/{task_id} - Response Time | TO DO | Automation | Medium |
| 197 | PZ-14771 | Infrastructure - Security - API Authentication Required | TO DO | Automation | Highest |
| 198 | PZ-14772 | Infrastructure - Security - Invalid Authentication Token | TO DO | Automation | Highest |
| 199 | PZ-14773 | Infrastructure - Security - Expired Authentication Token | TO DO | Automation | Highest |
| 200 | PZ-14774 | Infrastructure - Security - SQL Injection Prevention | TO DO | Automation | High |
| 201 | PZ-14775 | Infrastructure - Security - XSS Prevention | TO DO | Automation | High |
| 202 | PZ-14776 | Infrastructure - Security - CSRF Protection | TO DO | Automation | High |
| 203 | PZ-14777 | Infrastructure - Security - Rate Limiting | TO DO | Automation | High |
| 204 | PZ-14778 | Infrastructure - Security - HTTPS Only | TO DO | Automation | High |
| 205 | PZ-14779 | Infrastructure - Security - Sensitive Data Exposure | TO DO | Automation | High |
| 206 | PZ-14780 | Infrastructure - Error Handling - 500 Internal Server Error | TO DO | Automation | Highest |
| 207 | PZ-14781 | Infrastructure - Error Handling - 503 Service Unavailable | TO DO | Automation | Highest |
| 208 | PZ-14782 | Infrastructure - Error Handling - 504 Gateway Timeout | TO DO | Automation | High |
| 209 | PZ-14783 | Infrastructure - Error Handling - Network Timeout | TO DO | Automation | High |
| 210 | PZ-14784 | Infrastructure - Error Handling - Connection Refused | TO DO | Automation | High |
| 211 | PZ-14785 | Infrastructure - Error Handling - Invalid JSON Payload | TO DO | Automation | High |
| 212 | PZ-14786 | Infrastructure - Error Handling - Malformed Request | TO DO | Automation | High |
| 213 | PZ-14787 | Infrastructure - Error Handling - Error Message Format | TO DO | Automation | High |
| 214 | PZ-14788 | Infrastructure - Security - Input Sanitization | TO DO | Automation | High |
| 215 | PZ-14790 | Infrastructure - Performance - POST /configure Response Time | TO DO | Automation | High |
| 216 | PZ-14791 | Infrastructure - Performance - GET /waterfall Response Time | TO DO | Automation | High |
| 217 | PZ-14792 | Infrastructure - Performance - GET /metadata Response Time | TO DO | Automation | High |
| 218 | PZ-14793 | Infrastructure - Performance - Concurrent Requests Performance | TO DO | Automation | High |
| 219 | PZ-14794 | Infrastructure - Performance - Large Payload Handling | TO DO | Automation | Medium |
| 220 | PZ-14795 | Infrastructure - Performance - Memory Usage Under Load | TO DO | Automation | Medium |
| 221 | PZ-14796 | Infrastructure - Performance - CPU Usage Under Load | TO DO | Automation | Medium |
| 222 | PZ-14797 | Infrastructure - Performance - Database Query Performance | TO DO | Automation | Medium |
| 223 | PZ-14798 | Infrastructure - Performance - Network Latency Impact | TO DO | Automation | Low |
| 224 | PZ-14799 | Infrastructure - Performance - End-to-End Latency | TO DO | Automation | High |
| 225 | PZ-14800 | Infrastructure - Load - Concurrent Job Creation Load | TO DO | Automation | High |
| 226 | PZ-14801 | Infrastructure - Load - Sustained Load - 1 Hour | TO DO | Automation | High |
| 227 | PZ-14802 | Infrastructure - Load - Peak Load - High RPS | TO DO | Automation | High |
| 228 | PZ-14803 | Infrastructure - Load - Ramp-Up Load Profile | TO DO | Automation | Medium |
| 229 | PZ-14804 | Infrastructure - Load - Spike Load Profile | TO DO | Automation | Medium |
| 230 | PZ-14805 | Infrastructure - Load - Steady-State Load Profile | TO DO | Automation | Medium |
| 231 | PZ-14806 | Infrastructure - Load - Recovery After Load | TO DO | Automation | Medium |
| 232 | PZ-14807 | Infrastructure - Load - Resource Exhaustion Under Load | TO DO | Automation | Medium |
| 233 | PZ-14808 | Infrastructure - Data Quality - Waterfall Data Consistency | TO DO | Automation | Medium |
| 234 | PZ-14809 | Infrastructure - Data Quality - Metadata Consistency | TO DO | Automation | Medium |
| 235 | PZ-14810 | Infrastructure - Data Quality - Data Integrity Across Requests | TO DO | Automation | Medium |
| 236 | PZ-14811 | Infrastructure - Data Quality - Timestamp Accuracy | TO DO | Automation | Low |
| 237 | PZ-14812 | Infrastructure - Data Quality - Data Completeness | TO DO | Automation | Medium |

## Summary

- **Total Tests:** 237
- **Tests in CSV:** 237
- **Tests in Test Plan:** 237
- **Tests NOT in Test Plan:** 0
