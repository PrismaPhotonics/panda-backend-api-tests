# Gap Analysis Report - Epic PZ-14221

**Date:** 2025-11-04
**Epic:** PZ-14221 - Backend Automation - Focus Server API Tests - Drop 3

## Executive Summary

- **Epic tickets:** 99
- **CSV tests (Xray):** 151
- **Matched:** 8
- **Missing automation tasks:** 143
- **Epic tickets without tests:** 95

## Missing Automation Tasks

These 143 Xray tests need automation development tasks in Epic PZ-14221:

### PZ-14101: Integration - Historic Playback - Short Duration (Rapid Window)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14101
- **Suggested Task:** Automate: Integration - Historic Playback - Short Duration (Rapid Window)

**Description:**
h2. Summary

Integration - Historic Playback - Short Duration (Rapid Window) validates the system's ability to handle historic playback requests with very short time windows of 1 minute.

h2. Context

This test focuses on an edge case for minimal duration historic jobs. It ensures that the system ca...

---

### PZ-14100: Integration - Frequency Range Within Nyquist Limit

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14100
- **Suggested Task:** Automate: Integration - Frequency Range Within Nyquist Limit

**Description:**
*Test Summary:*  
Integration - Frequency Range Within Nyquist Limit

*Description:*  
Validates that the system correctly accepts frequency range configurations that are within the Nyquist limit (PRR/2). This is a positive test ensuring valid configurations are accepted.

*Pre-conditions:*

* Focus...

---

### PZ-14099: Integration - Configuration Missing channels Field

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14099
- **Suggested Task:** Automate: Integration - Configuration Missing channels Field

**Description:**
*Test Summary:*  
Integration - Configuration Missing channels Field

*Description:*  
Validates that the system properly handles configuration requests missing the channels field. Tests required field validation for channel selection.

*Pre-conditions:*

* Focus Server API is accessible

*Test Step...

---

### PZ-14098: Integration - Configuration Missing frequencyRange Field

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14098
- **Suggested Task:** Automate: Integration - Configuration Missing frequencyRange Field

**Description:**
*Test Summary:*  
Integration - Configuration Missing frequencyRange Field

*Description:*  
Validates that the system properly handles configuration requests missing the frequencyRange field. Tests required field validation for frequency parameters.

*Pre-conditions:*

* Focus Server API is accessi...

---

### PZ-14097: Integration - Configuration Missing nfftSelection Field

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14097
- **Suggested Task:** Automate: Integration - Configuration Missing nfftSelection Field

**Description:**
*Test Summary:*  
Integration - Configuration Missing nfftSelection Field

*Description:*  
Validates that the system properly handles configuration requests missing the nfftSelection field. Tests required field validation for FFT window size.

*Pre-conditions:*

* Focus Server API is accessible

*T...

---

### PZ-14095: Integration - Configuration Missing displayTimeAxisDuration Field

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14095
- **Suggested Task:** Automate: Integration - Configuration Missing displayTimeAxisDuration Field

**Description:**
*Test Summary:*  
Integration - Configuration Missing displayTimeAxisDuration Field

*Description:*  
Validates that the system properly handles configuration requests missing the displayTimeAxisDuration field. Tests required field validation.

*Pre-conditions:*

* Focus Server API is accessible

*T...

---

### PZ-14094: Integration - Invalid View Type - String Value

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14094
- **Suggested Task:** Automate: Integration - Invalid View Type - String Value

**Description:**
*Test Summary:*  
Integration - Invalid View Type - String Value

*Description:*  
Validates that the system properly rejects configuration requests with view_type provided as a string instead of integer. Tests Pydantic type validation.

*Pre-conditions:*

* Focus Server API is accessible

*Test Ste...

---

### PZ-14093: Integration - Invalid View Type - Out of Range

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14093
- **Suggested Task:** Automate: Integration - Invalid View Type - Out of Range

---

### PZ-14092: Performance - Configuration Endpoint P95 Latency

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14092
- **Suggested Task:** Automate: Performance - Configuration Endpoint P95 Latency

**Description:**
*Test Summary:*  
Performance - Configuration Endpoint P95 Latency

*Description:*  
Validates that 95% of configuration requests complete within acceptable time threshold (< 500ms). Measures P95 percentile latency for POST /configure endpoint.

*Pre-conditions:*

* Focus Server is running
* System ...

---

### PZ-14091: Performance - Configuration Endpoint P99 Latency

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14091
- **Suggested Task:** Automate: Performance - Configuration Endpoint P99 Latency

**Description:**
*Test Summary:*  
Performance - Configuration Endpoint P99 Latency

*Description:*  
Validates that 99% of configuration requests complete within acceptable time threshold (< 1000ms). Measures P99 percentile latency for POST /configure endpoint under normal load.

*Pre-conditions:*

* Focus Server i...

---

### PZ-14090: Performance - Job Creation Time < 2 Seconds

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14090
- **Suggested Task:** Automate: Performance - Job Creation Time < 2 Seconds

**Description:**
*Test Summary:*  
Performance - Job Creation Time < 2 Seconds

*Description:*  
Validates that job creation completes within acceptable time limits. Measures the time from POST /configure request to receiving job_id response.

*Pre-conditions:*

* Focus Server is running with normal load
* Network l...

---

### PZ-14089: Integration - Time Range Validation - Future Timestamps Rejection

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14089
- **Suggested Task:** Automate: Integration - Time Range Validation - Future Timestamps Rejection

**Description:**
*Test Summary:*  
Integration - Time Range Validation - Future Timestamps Rejection

*Description:*  
Validates that the Focus Server properly rejects historic playback requests with future timestamps. This prevents invalid configurations and ensures data integrity.

*Pre-conditions:*

* Focus Serve...

---

### PZ-14088: Load - 200 Jobs Capacity Stress Test

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14088
- **Suggested Task:** Automate: Load - 200 Jobs Capacity Stress Test

**Description:**
h2. Summary

Load - 200 Jobs Capacity Stress Test to validate the Focus Server's ability to handle 200 concurrent jobs.

h2. Context

This test is essential to ensure that the infrastructure meets the workload requirements established in the capacity planning meeting. It checks if the Focus Server c...

---

### PZ-14080: Historic – Spectrogram Dimensions Calculation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14080
- **Suggested Task:** Automate: Historic – Spectrogram Dimensions Calculation

**Description:**
h2. Summary

*Historic – Spectrogram Dimensions Calculation*

h2. Priority

Low

h2. Objective

Validate historic image dimensions: Width ≈ {{duration / lines_dt}}, Height = {{frequencies_amount}}.

h2. Steps

||#||Action||Data||Expected Result||
|1|Request historic with duration=60s|valid params|HT...

---

### PZ-14079: Performance – Memory Usage Estimation (Informational)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14079
- **Suggested Task:** Automate: Performance – Memory Usage Estimation (Informational)

**Description:**
h2. Summary

*Performance – Memory Usage Estimation (Informational)*

h2. Priority

Low

h2. Objective

Estimate memory per frame: {{channels × freq_bins × bytes_per_sample}}.

h2. Assertions

* memory_per_frame > 0 and below configured limits

h2. Automation Status

✅ *Automated* with Pytest

*Test...

---

### PZ-14078: Performance – Data Rate Calculation (Informational)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14078
- **Suggested Task:** Automate: Performance – Data Rate Calculation (Informational)

**Description:**
h2. Summary

*Performance – Data Rate Calculation (Informational)*

h2. Priority

Low

h2. Objective

Estimate data rate: {{data_rate = channels × freq_bins × output_rate × bytes_per_sample}}.

h2. Assertions

* data_rate > 0 and within reasonable bounds for config

h2. Automation Status

✅ *Automat...

---

### PZ-14073: Integration – Validation – Overlap Percentage Validation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14073
- **Suggested Task:** Automate: Integration – Validation – Overlap Percentage Validation

**Description:**
h2. Summary

*Validation – Overlap Percentage Validation*

h2. Priority

Low

h2. Objective

Validate allowed overlap values (system may fix/derive overlap).

h2. Steps

||#||Action||Data||Expected Result||
|1|POST /configure|overlap=0/25/50/75% (if supported)|Valid ranges accepted|
|2|POST /configu...

---

### PZ-14072: Integration – Validation – FFT Window Size (Power of 2) Validation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14072
- **Suggested Task:** Automate: Integration – Validation – FFT Window Size (Power of 2) Validation

**Description:**
h2. Summary

*Validation – FFT Window Size (Power of 2) Validation*

h2. Priority

High

h2. Objective

Validate that only power-of-two NFFT values are accepted.

h2. Steps

||#||Action||Data||Expected Result||
|1|POST /configure|nfft=256/512/1024|HTTP 200|
|2|POST /configure|nfft=300/500/1000|HTTP ...

---

### PZ-14070: Integration – Calculation Validation – MultiChannel Mapping Validation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14070
- **Suggested Task:** Automate: Integration – Calculation Validation – MultiChannel Mapping Validation

**Description:**
h2. Summary

*Calculation Validation – MultiChannel Mapping Validation*

h2. Priority

High

h2. Objective

For MultiChannel (view_type=0), expected traditional 1:1 mapping (document discrepancies).

h2. Steps

||#||Action||Data||Expected Result||
|1|POST /configure|channels {min:1,max:8}|HTTP 200|
...

---

### PZ-14069: Integration – Calculation Validation – Channel Count Calculation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14069
- **Suggested Task:** Automate: Integration – Calculation Validation – Channel Count Calculation

**Description:**
h2. Summary

*Calculation Validation – Channel Count Calculation*

h2. Test Type

Integration Test

h2. Priority

High

h2. Components/Labels

{{focus-server}}, {{api}}, {{calculations}}, {{channels}}

h2. Requirements

* FOCUS-CALC-CHAN (Channel Calculation Requirements)

h2. Objective

Validate th...

---

### PZ-14068: Integration –  Calculation Validation – Time Window Duration Calculation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14068
- **Suggested Task:** Automate: Integration –  Calculation Validation – Time Window Duration Calculation

**Description:**
h2. Summary

*Calculation Validation – Time Window Duration Calculation*

h2. Test Type

Integration Test

h2. Priority

Low

h2. Components/Labels

{{focus-server}}, {{api}}, {{calculations}}, {{time}}

h2. Requirements

* FOCUS-CALC-TIME (Time Calculation Requirements)

h2. Objective

Validate tha...

---

### PZ-14067: Integration – Calculation Validation – Output Rate Calculation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14067
- **Suggested Task:** Automate: Integration – Calculation Validation – Output Rate Calculation

**Description:**
h2. Summary

*Calculation Validation – Output Rate Calculation*

h2. Test Type

Integration Test

h2. Priority

Medium

h2. Components/Labels

{{focus-server}}, {{api}}, {{calculations}}, {{time}}, {{performance}}, {{output-rate}}

h2. Requirements

* FOCUS-CALC-TIME (Time Calculation Requirements)
...

---

### PZ-14066: Integration – Calculation Validation – Time Resolution (lines_dt) Calculation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14066
- **Suggested Task:** Automate: Integration – Calculation Validation – Time Resolution (lines_dt) Calculation

**Description:**
h2. Summary

*Calculation Validation – Time Resolution (lines_dt) Calculation*

h2. Test Type

Integration Test

h2. Priority

High

h2. Components/Labels

{{focus-server}}, {{api}}, {{calculations}}, {{time}}, {{lines_dt}}, {{resolution}}

h2. Requirements

* FOCUS-CALC-TIME (Time Calculation Requi...

---

### PZ-14062: Integration – Calculation Validation – Nyquist Frequency Limit Validation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14062
- **Suggested Task:** Automate: Integration – Calculation Validation – Nyquist Frequency Limit Validation

**Description:**
h2. Summary

*Calculation Validation – Nyquist Frequency Limit Validation*

h2. Test Type

Integration Test

h2. Priority

Medium

h2. Components/Labels

{{focus-server}}, {{api}}, {{calculations}}, {{frequency}}, {{validation}}, {{nyquist}}

h2. Requirements

* FOCUS-CALC-FREQ (Frequency Calculatio...

---

### PZ-14061: Integration – Calculation Validation – Frequency Bins Count Calculation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14061
- **Suggested Task:** Automate: Integration – Calculation Validation – Frequency Bins Count Calculation

**Description:**
h2. Summary

*Calculation Validation – Frequency Bins Count Calculation*

h2. Test Type

Integration Test

h2. Priority

High

h2. Components/Labels

{{focus-server}}, {{api}}, {{calculations}}, {{frequency}}, {{nfft}}

h2. Requirements

* FOCUS-CALC-FREQ (Frequency Calculation Requirements)

h2. Ob...

---

### PZ-14060: Integration – Calculation Validation – Frequency Resolution Calculation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14060
- **Suggested Task:** Automate: Integration – Calculation Validation – Frequency Resolution Calculation

**Description:**
h2. Summary

*Calculation Validation – Frequency Resolution Calculation*

h2. Test Type

Integration Test

h2. Priority

High

h2. Components/Labels

{{focus-server}}, {{api}}, {{calculations}}, {{frequency}}, {{validation}}

h2. Requirements

* FOCUS-CALC-FREQ (Frequency Calculation Requirements)

...

---

### PZ-14033: API - Health Check Load Testing

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14033
- **Suggested Task:** Automate: API - Health Check Load Testing

**Description:**
h3. Summary

Health check maintains acceptable response times under sustained load

h3. Component

Focus Server API

h3. Labels

* {{health-check}}
* {{api}}
* {{performance}}
* {{load}}
* {{stress}}

h3. Test Type

Performance/Stress Test

h3. Priority

Medium

h3. Objective

Verify that /ack endpo...

---

### PZ-14032: API - Health Check with SSL/TLS

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14032
- **Suggested Task:** Automate: API - Health Check with SSL/TLS

**Description:**
h3. Summary

Health check works correctly with SSL/TLS enabled and self-signed certificates

h3. Component

Focus Server API

h3. Labels

* {{health-check}}
* {{api}}
* {{ssl}}
* {{tls}}
* {{edge-case}}

h3. Test Type

API Test (Edge Case)

h3. Priority

Medium

h3. Objective

Verify that /ack endpo...

---

### PZ-14031: API - Health Check Response Structure Validation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14031
- **Suggested Task:** Automate: API - Health Check Response Structure Validation

**Description:**
h3. Summary

Health check returns valid response structure with correct JSON format

h3. Component

Focus Server API

h3. Labels

* {{health-check}}
* {{api}}
* {{validation}}
* {{positive-test}}

h3. Test Type

API Test (Validation)

h3. Priority

Medium

h3. Objective

Verify that /ack endpoint re...

---

### PZ-14030: API - Health Check Security Headers Validation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14030
- **Suggested Task:** Automate: API - Health Check Security Headers Validation

**Description:**
h3. Summary

Health check handles malicious headers without crashing or exposing vulnerabilities

h3. Component

Focus Server API

h3. Labels

* {{health-check}}
* {{api}}
* {{security}}
* {{fuzzing}}
* {{penetration}}

h3. Test Type

Security Test

h3. Priority

High

h3. Objective

Verify that /ac...

---

### PZ-14029: API - Health Check with Various Headers

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14029
- **Suggested Task:** Automate: API - Health Check with Various Headers

**Description:**
h3. Summary

Health check handles requests with various HTTP headers correctly

h3. Component

Focus Server API

h3. Labels

* {{health-check}}
* {{api}}
* {{edge-case}}
* {{headers}}

h3. Test Type

API Test (Edge Case)

h3. Priority

Low

h3. Objective

Verify that /ack endpoint handles various HT...

---

### PZ-14028: API - Health Check Handles Concurrent Requests

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14028
- **Suggested Task:** Automate: API - Health Check Handles Concurrent Requests

**Description:**
h3. Summary

Health check handles multiple concurrent requests without errors or timeouts

h3. Component

Focus Server API

h3. Labels

* {{health-check}}
* {{api}}
* {{performance}}
* {{load}}
* {{concurrency}}

h3. Test Type

Performance Test

h3. Priority

High

h3. Objective

Verify that /ack en...

---

### PZ-14027: API - Health Check Rejects Invalid HTTP Methods

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14027
- **Suggested Task:** Automate: API - Health Check Rejects Invalid HTTP Methods

**Description:**
h3. Summary

Health check rejects invalid HTTP methods (POST, PUT, DELETE, PATCH)

h3. Component

Focus Server API

h3. Labels

* {{health-check}}
* {{api}}
* {{negative-test}}
* {{validation}}
* {{security}}

h3. Test Type

API Test (Negative)

h3. Priority

Medium

h3. Objective

Verify that /ack ...

---

### PZ-14026: API - Health Check Returns Valid Response (200 OK)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14026
- **Suggested Task:** Automate: API - Health Check Returns Valid Response (200 OK)

**Description:**
h3. Summary

Health check returns valid response with acceptable response time

h3. Component

Focus Server API

h3. Labels

* {{health-check}}
* {{api}}
* {{positive-test}}
* {{smoke}}
* {{critical}}

h3. Test Type

API Test (Positive)

h3. Priority

High

h3. Objective

Verify that GET /ack endpoi...

---

### PZ-14019: History with Empty Time Window Returns 400

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14019
- **Suggested Task:** Automate: History with Empty Time Window Returns 400

**Description:**
h3. Summary

History with Empty Time Window Returns 400 and No Side Effects

h3. Component

Focus Server Backend API

h3. Labels

* {{historic-playback}}
* {{data-availability}}
* {{validation}}
* {{safety}}
* {{negative-test}}

h3. Test Type

Integration Test (Negative / Safety)

----

h3. Objectiv...

---

### PZ-14018: Invalid Configuration Does Not Launch Orchestration

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14018
- **Suggested Task:** Automate: Invalid Configuration Does Not Launch Orchestration

**Description:**
h3. Summary

Invalid Configuration Does Not Launch Orchestration

h3. Component

Focus Server Backend API

h3. Labels

* {{config-validation}}
* {{orchestration}}
* {{safety}}
* {{negative-test}}
* {{critical}}

h3. Test Type

Integration Test (Negative / Safety)

----

h3. Objective

Verify that wh...

---

### PZ-13909: Integration - Historic Configuration Missing end_time Field

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13909
- **Suggested Task:** Automate: Integration - Historic Configuration Missing end_time Field

**Description:**
h2. Summary

Integration - Historic Configuration Missing end_time Field

h2. Context

This issue validates that the Focus Server properly rejects historic playback configurations that lack the required {{end_time}} field. It is a complementary test to NEW-010, ensuring both time boundaries are vali...

---

### PZ-13907: Integration - Historic Configuration Missing start_time Field

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13907
- **Suggested Task:** Automate: Integration - Historic Configuration Missing start_time Field

**Description:**
## Summary
Integration - Historic Configuration Missing start_time Field

## Objective
Validates that Focus Server properly **rejects** historic playback configurations that are missing the **required** `start_time` field. Historic mode requires both `start_time` and `end_time` to define the pla...

---

### PZ-13906: Integration - Low Throughput Configuration Edge Case

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13906
- **Suggested Task:** Automate: Integration - Low Throughput Configuration Edge Case

**Description:**
h2. Summary

Integration - Low Throughput Configuration Edge Case

h2. Objective

Tests configuration with *very low data throughput* (< 1 Mbps) to verify system behavior at the lower performance boundary. Low throughput occurs with: few sensors, large NFFT (fewer rows/sec), narrow frequency range. ...

---

### PZ-13905: Performance - High Throughput Configuration Stress Test

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13905
- **Suggested Task:** Automate: Performance - High Throughput Configuration Stress Test

**Description:**
h2. Summary

Performance - High Throughput Configuration Stress Test

h2. Objective

Tests configuration with *very high data throughput* (> 50 Mbps) to verify system behavior under heavy load. High throughput occurs with: many sensors, small NFFT (more rows/sec), wide frequency range. This test ide...

---

### PZ-13904: Integration - Configuration Resource Usage Estimation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13904
- **Suggested Task:** Automate: Integration - Configuration Resource Usage Estimation

**Description:**
h2. Summary

Integration - Configuration Resource Usage Estimation

h2. Objective

Calculates and validates estimated resource usage (CPU, Memory, Network Bandwidth) for a given configuration before task creation. This allows capacity planning and prevents configurations that would exhaust system re...

---

### PZ-13903: Integration - Frequency Range Nyquist Limit Enforcement

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13903
- **Suggested Task:** Automate: Integration - Frequency Range Nyquist Limit Enforcement

**Description:**
h2. Summary

Integration - Frequency Range Nyquist Limit Enforcement

h2. Objective

Validates that Focus Server *enforces the Nyquist-Shannon sampling theorem* and rejects frequency ranges that exceed the Nyquist frequency (PRR/2). This is the *most critical data quality test* because violating Nyq...

---

### PZ-13901: Integration - NFFT Values Validation - All Supported Values

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13901
- **Suggested Task:** Automate: Integration - NFFT Values Validation - All Supported Values

**Description:**
h2. Summary

Integration - NFFT Values Validation - All Supported Values

h2. Objective

Validates that Focus Server accepts and processes all valid NFFT values (128, 256, 512, 1024, 2048, 4096). NFFT (FFT size) determines frequency resolution in spectral analysis. Different NFFT values provide diff...

---

### PZ-13900: Infrastructure - SSH Access to Production Servers

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13900
- **Suggested Task:** Automate: Infrastructure - SSH Access to Production Servers

**Description:**
h2. Summary

Infrastructure - SSH Access to Production Servers

h2. Objective

Validates SSH connectivity to production servers through jump host for troubleshooting and maintenance operations. SSH access is critical for accessing logs, executing commands, running k9s, and performing manual interven...

---

### PZ-13898: Infrastructure - MongoDB Direct Connection and Health Check

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13898
- **Suggested Task:** Automate: Infrastructure - MongoDB Direct Connection and Health Check

**Description:**
h2. Summary

Infrastructure - MongoDB Direct Connection and Health Check

h2. Objective

Validates direct TCP connection to MongoDB database server and verifies basic operations (authentication, ping, database listing). This is a critical infrastructure test that isolates MongoDB health from Focus S...

---

### PZ-13897: Integration - GET /sensors - Retrieve Available Sensors List

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13897
- **Suggested Task:** Automate: Integration - GET /sensors - Retrieve Available Sensors List

**Description:**
h2. Summary

Integration - GET /sensors - Retrieve Available Sensors List

h2. Objective

Validates that the {{GET /sensors}} endpoint returns a complete list of all available sensors/channels in the system. This endpoint is a prerequisite for any configuration operation, as clients need to know whi...

---

### PZ-13896: Performance – Concurrent Task Limit

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13896
- **Suggested Task:** Automate: Performance – Concurrent Task Limit

**Description:**
h2. Objective

Determines the *maximum number of concurrent tasks* the system can handle reliably. This test validates system capacity under parallel load and identifies breaking points. Understanding concurrent task limits is critical for capacity planning and preventing system overload in producti...

---

### PZ-13895: Integration – GET /channels - Enabled Channels List

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13895
- **Suggested Task:** Automate: Integration – GET /channels - Enabled Channels List

**Description:**
h2. Summary

GET /channels - Enabled Channels List

h2. Objective

Validates that the {{GET /channels}} endpoint returns a list of all enabled/available channels in the system. This is a critical smoke test that verifies basic API functionality and channel discovery mechanism. The endpoint is used b...

---

### PZ-13880: Stress - Configuration with Extreme Values 

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13880
- **Suggested Task:** Automate: Stress - Configuration with Extreme Values 

**Description:**
h3. Summary

Validates that Focus Server can handle configuration requests with extreme (but technically valid) parameter values, such as very large channel ranges, very high NFFT, or very large canvas heights.

h3. Objective

Verify that the server can accept and process configurations with boundar...

---

### PZ-13879: Integration – Missing Required Fields

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13879
- **Suggested Task:** Automate: Integration – Missing Required Fields

**Description:**
h2. Summary

Integration – Missing Required Fields

h2. Objective

Validates that Focus Server properly rejects configuration requests that are missing required fields (e.g., missing {{channels}}, {{frequencyRange}}, or {{nfftSelection}}). This ensures proper input validation and prevents incomplete...

---

### PZ-13878: Integration – Invalid View Type - Out of Range

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13878
- **Suggested Task:** Automate: Integration – Invalid View Type - Out of Range

**Description:**
h2. Summary

Integration – Invalid View Type - Out of Range

h2. Objective

Validates that Focus Server properly rejects configuration requests with invalid {{view_type}} values (outside the defined enum range). Valid values are 0 (MULTICHANNEL) or 1 (SINGLECHANNEL). Any other value should be reject...

---

### PZ-13877: Integration – Invalid Frequency Range - Min > Max

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13877
- **Suggested Task:** Automate: Integration – Invalid Frequency Range - Min > Max

**Description:**
h3. Summary

Validates that Focus Server properly rejects configuration requests where {{frequencyRange.min > frequencyRange.max}}.

h2. Objective

Validates that Focus Server properly rejects configuration requests where {{frequencyRange.min > frequencyRange.max}}, which represents an invalid/impos...

---

### PZ-13876: Integration – Invalid Channel Range - Min > Max

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13876
- **Suggested Task:** Automate: Integration – Invalid Channel Range - Min > Max

**Description:**
h3. Summary

Validates that Focus Server properly rejects configuration requests where {{channels.min > channels.max}}, which is an invalid range.

h2. Objective

Validates that Focus Server properly rejects configuration requests where {{channels.min > channels.max}}, which represents an invalid se...

---

### PZ-13875: Integration – Invalid NFFT - Negative Value

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13875
- **Suggested Task:** Automate: Integration – Invalid NFFT - Negative Value

**Description:**
h3. Summary

Validates that Focus Server properly rejects configuration requests with negative {{nfftSelection}} values.

h3. Objective

Verify proper validation and error handling when attempting to configure a task with a negative NFFT value.

h3. Priority

*High*

h3. Components/Labels

* *Compon...

---

### PZ-13874: Integration – Invalid NFFT - Zero Value

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13874
- **Suggested Task:** Automate: Integration – Invalid NFFT - Zero Value

**Description:**
h3. Summary

Validates that Focus Server properly rejects configuration requests with {{nfftSelection = 0}}, which is invalid for FFT processing.

h3. Objective

Verify proper validation and error handling when attempting to configure a task with zero NFFT value.

h3. Priority

*High*

h3. Component...

---

### PZ-13873: integration - Valid Configuration - All Parameters

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13873
- **Suggested Task:** Automate: integration - Valid Configuration - All Parameters

**Description:**
h3. Summary

Validates that Focus Server correctly accepts and processes a fully valid configuration request with all parameters properly set.

h2. Objective

Validates that Focus Server correctly *accepts* and processes a fully valid configuration request with all parameters properly set. This is t...

---

### PZ-13872: Integration – Historic Playback Complete End-to-End Flow

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13872
- **Suggested Task:** Automate: Integration – Historic Playback Complete End-to-End Flow

**Description:**
h3. Summary

Comprehensive end-to-end test for historic playback, covering configuration, polling, data collection, metadata retrieval, and completion verification.

h3. Objective

Verify that a complete historic playback session works correctly from start (configuration) to finish (status 208), dem...

---

### PZ-13871: Integration – Historic Playback - Timestamp Ordering Validation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13871
- **Suggested Task:** Automate: Integration – Historic Playback - Timestamp Ordering Validation

**Description:**
h3. Summary

Validates that all timestamps in historic playback data are strictly ordered, with no out-of-sequence or overlapping time ranges.

h2. Objective

Validates that timestamps in historic playback data are *monotonically increasing* (each timestamp >= previous timestamp). This is critical f...

---

### PZ-13870: Integration – Historic Playback - Future Timestamps

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13870
- **Suggested Task:** Automate: Integration – Historic Playback - Future Timestamps

**Description:**
h3. Summary

Validates that Focus Server properly handles historic playback requests with future timestamps, either rejecting them or gracefully completing with no data.

h3. Objective

Verify error handling or graceful behavior when requesting historic data for a time range in the future (which can...

---

### PZ-13869: Integration – Historic Playback - Invalid Time Range (End Before Start)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13869
- **Suggested Task:** Automate: Integration – Historic Playback - Invalid Time Range (End Before Start)

**Description:**
h3. Summary

Validates that Focus Server properly rejects historic playback requests where {{end_time}} is before {{start_time}}, returning an appropriate error.

h3. Objective

Verify proper validation and error handling when attempting to configure a historic playback with an invalid time range (e...

---

### PZ-13868: Integration – Historic Playback - Status 208 Completion

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13868
- **Suggested Task:** Automate: Integration – Historic Playback - Status 208 Completion

**Description:**
h3. Summary

Validates that historic playback tasks correctly reach status 208 (baby analyzer exited) upon completion, signaling end-of-data.

h2. Objective

Validates that historic playback properly completes with HTTP status code 208 ("Already Reported") when all historical data has been delivered...

---

### PZ-13866: Integration – Historic Playback - Very Old Timestamps (No Data)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13866
- **Suggested Task:** Automate: Integration – Historic Playback - Very Old Timestamps (No Data)

**Description:**
h3. Summary

Validates that Focus Server correctly handles historic playback requests for time ranges where no data exists (e.g., 1 year ago), returning appropriate status and messages.

h3. Objective

Verify error handling or graceful completion when requesting historic data from a time period with...

---

### PZ-13865: Integration – Historic Playback - Short Duration (1 Minute)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13865
- **Suggested Task:** Automate: Integration – Historic Playback - Short Duration (1 Minute)

**Description:**
h3. Summary

Validates that Focus Server can handle a very short historic playback request (1 minute), completing quickly and efficiently.

h3. Objective

Verify that historic playback works correctly for minimal time ranges (1 minute), demonstrating that the system can handle short-duration queries...

---

### PZ-13863: Integration – Historic Playback - Standard 5-Minute Range

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13863
- **Suggested Task:** Automate: Integration – Historic Playback - Standard 5-Minute Range

**Description:**
h3. Summary

Validates that Focus Server correctly handles a standard historic playback request for a 5-minute time range, returning data from the specified historical period and completing with status 208.

h3. Objective

Verify that Focus Server can process a historic playback configuration with {...

---

### PZ-13862: Integration - SingleChannel Complete Flow End-to-End

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13862
- **Suggested Task:** Automate: Integration - SingleChannel Complete Flow End-to-End

**Description:**
h3. Summary

Comprehensive end-to-end test for SingleChannel view, covering configuration, data polling, metadata retrieval, reconfiguration, and cleanup, validating the complete lifecycle of a SingleChannel task.

h3. Objective

Verify that a SingleChannel task can be configured, polled for data, q...

---

### PZ-13861: Integration - SingleChannel Stream Mapping Verification

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13861
- **Suggested Task:** Automate: Integration - SingleChannel Stream Mapping Verification

**Description:**
h3. Summary

Validates the {{channel_to_stream_index}} mapping returned in the configuration response for various SingleChannel configurations, ensuring correct 1:1 mapping in all cases.

h3. Objective

Verify that for any valid SingleChannel configuration (any channel ID), the {{channel_to_stream_i...

---

### PZ-13860: Integration - SingleChannel Metadata Consistency

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13860
- **Suggested Task:** Automate: Integration - SingleChannel Metadata Consistency

**Description:**
h3. Summary

Validates that metadata returned for a SingleChannel task (via GET /metadata/{task_id}) is consistent with the configuration and reflects the single-channel setup.

h3. Objective

Verify that GET /metadata returns consistent and accurate metadata for a SingleChannel task, including chan...

---

### PZ-13859: Integration - SingleChannel Polling Stability

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13859
- **Suggested Task:** Automate: Integration - SingleChannel Polling Stability

**Description:**
h3. Summary

Validates that prolonged polling of a SingleChannel task remains stable, with consistent response times and no degradation over time.

h3. Objective

Verify that continuous polling of a SingleChannel task for an extended period (e.g., 100 polls) does not result in performance degradatio...

---

### PZ-13858: Integration - SingleChannel Rapid Reconfiguration

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13858
- **Suggested Task:** Automate: Integration - SingleChannel Rapid Reconfiguration

**Description:**
h3. Summary

Validates that a SingleChannel task can be rapidly reconfigured multiple times without errors, ensuring the server handles configuration updates correctly.

h3. Objective

Verify that Focus Server can handle multiple rapid reconfigurations of the same task_id, updating the channel selec...

---

### PZ-13857: Integration - SingleChannel NFFT Validation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13857
- **Suggested Task:** Automate: Integration - SingleChannel NFFT Validation

**Description:**
h3. Summary

Validates that SingleChannel view correctly accepts and applies different NFFT (FFT size) configurations.

h3. Objective

Verify that Focus Server accepts various NFFT values (e.g., 512, 1024, 2048) and configures the task successfully, affecting the frequency resolution of the returned...

---

### PZ-13855: Integration - SingleChannel Canvas Height Validation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13855
- **Suggested Task:** Automate: Integration - SingleChannel Canvas Height Validation

**Description:**
h3. Summary

Validates that SingleChannel view correctly accepts and applies different canvas height configurations.

h3. Objective

Verify that Focus Server accepts various canvas height values (e.g., 500, 1000, 1500, 2000) and configures the task successfully.

h3. Priority

*Low*

h3. Components/...

---

### PZ-13854: Integration - SingleChannel Frequency Range Validation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13854
- **Suggested Task:** Automate: Integration - SingleChannel Frequency Range Validation

**Description:**
h3. Summary

Validates that SingleChannel view correctly applies and respects the specified frequency range configuration.

h3. Objective

Verify that when a SingleChannel task is configured with a specific frequency range (e.g., 100-300 Hz), the returned data reflects this configuration and the ser...

---

### PZ-13853: Integration - SingleChannel Data Consistency Check

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13853
- **Suggested Task:** Automate: Integration - SingleChannel Data Consistency Check

**Description:**
h2. Objective

Validates that SingleChannel view returns *consistent data* across multiple requests for the same channel. Data consistency is critical for ensuring that the same channel configuration produces reproducible results. This test verifies that sensor mapping, data structure, and metadata ...

---

### PZ-13852: Integration - SingleChannel with Min > Max (Validation Error)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13852
- **Suggested Task:** Automate: Integration - SingleChannel with Min > Max (Validation Error)

**Description:**
h3. Summary

Validates that Focus Server properly rejects SingleChannel configuration requests when {{channels.min > channels.max}}, which violates the valid range definition for SingleChannel (min must equal max).

h2. Objective

Validates proper error handling when configuring SingleChannel with *...

---

### PZ-13837: Integration - SingleChannel with Invalid Channel (Negative)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13837
- **Suggested Task:** Automate: Integration - SingleChannel with Invalid Channel (Negative)

**Description:**
h3. Summary

Validates that Focus Server properly rejects SingleChannel configuration requests when the specified channel is a negative value.

h3. Objective

Verify proper error handling when attempting to configure a SingleChannel view with a negative channel ID.

h3. Priority

*High*

h3. Compone...

---

### PZ-13836: Integration - SingleChannel with Invalid Channel (Negative)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13836
- **Suggested Task:** Automate: Integration - SingleChannel with Invalid Channel (Negative)

**Description:**
h3. Summary

Validates that Focus Server properly rejects SingleChannel configuration requests when the specified channel is a negative value.

h3. Objective

Verify proper error handling when attempting to configure a SingleChannel view with a negative channel ID.

h3. Priority

*High*

h3. Compone...

---

### PZ-13835: Integration - SingleChannel with Invalid Channel (Out of Range High)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13835
- **Suggested Task:** Automate: Integration - SingleChannel with Invalid Channel (Out of Range High)

**Description:**
h3. Summary

Validates that Focus Server properly rejects SingleChannel configuration requests when the specified channel exceeds the maximum available sensor index.

h3. Objective

Verify proper error handling when attempting to configure a SingleChannel view with a channel ID that is higher than t...

---

### PZ-13834:  Integration - SingleChannel Edge Case - Middle Channel

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13834
- **Suggested Task:** Automate:  Integration - SingleChannel Edge Case - Middle Channel

**Description:**
h3. Summary

Validates SingleChannel view behavior when configuring a middle-range channel, ensuring correct 1:1 mapping and data delivery for a non-boundary sensor.

h3. Objective

Verify that Focus Server correctly handles SingleChannel view for any arbitrary channel in the middle of the sensor ra...

---

### PZ-13833: Integration - SingleChannel Edge Case - Maximum Channel (Last Available)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13833
- **Suggested Task:** Automate: Integration - SingleChannel Edge Case - Maximum Channel (Last Available)

**Description:**
h3. Summary

Validates SingleChannel view behavior when configuring the maximum available channel (last sensor), ensuring correct 1:1 mapping and data delivery for the edge case of the last sensor.

h3. Objective

Verify that Focus Server correctly handles SingleChannel view for the maximum availabl...

---

### PZ-13832: Integration - SingleChannel Edge Case - Minimum Channel (Channel 0)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13832
- **Suggested Task:** Automate: Integration - SingleChannel Edge Case - Minimum Channel (Channel 0)

**Description:**
h3. Summary

Validates SingleChannel view behavior when configuring the minimum available channel (channel 0), ensuring correct 1:1 mapping and data delivery for the edge case of the first sensor.

h3. Objective

Verify that Focus Server correctly handles SingleChannel view for channel 0, returning ...

---

### PZ-13824: API – SingleChannel Rejects Channel Zero

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13824
- **Suggested Task:** Automate: API – SingleChannel Rejects Channel Zero

**Description:**
*Summary:* API – SingleChannel Rejects Channel Zero

*Objective:* Verify that channel 0 is rejected (if channels start from 1).

*Priority:* Low

*Components/Labels:* focus-server, singlechannel, validation, boundary

*Requirements:* FOCUS-CHANNEL-VALIDATION

*Pre-Conditions:*

* PC-001: Channel num...

---

### PZ-13823: API – SingleChannel Rejects When min ≠ max

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13823
- **Suggested Task:** Automate: API – SingleChannel Rejects When min ≠ max

**Description:**
*Summary:* API – SingleChannel Rejects When min ≠ max

*Objective:* Verify that view_type=SINGLECHANNEL requires min=max in channels, and rejects min≠max.

*Priority:* Critical

*Components/Labels:* focus-server, singlechannel, validation, negative-test

*Requirements:* FOCUS-SINGLECHANNEL-VALIDATIO...

---

### PZ-13822: API – SingleChannel Rejects Invalid NFFT Value

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13822
- **Suggested Task:** Automate: API – SingleChannel Rejects Invalid NFFT Value

**Description:**
*Summary:* API – SingleChannel Rejects Invalid NFFT Value

*Objective:* Verify SingleChannel rejects NFFT that is not power of 2.

*Priority:* Medium

*Components/Labels:* focus-server, singlechannel, validation, nfft

*Requirements:* FOCUS-NFFT-VALIDATION

*Pre-Conditions:*

* PC-001: NFFT validati...

---

### PZ-13821: API – SingleChannel Rejects Invalid Display Height

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13821
- **Suggested Task:** Automate: API – SingleChannel Rejects Invalid Display Height

**Description:**
*Summary:* API – SingleChannel Rejects Invalid Display Height

*Objective:* Verify SingleChannel rejects invalid display height (zero or negative).

*Priority:* Medium

*Components/Labels:* focus-server, singlechannel, validation, negative-test

*Requirements:* FOCUS-SINGLECHANNEL-VALIDATION

*Pre-C...

---

### PZ-13820: API – SingleChannel Rejects Invalid Frequency Range

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13820
- **Suggested Task:** Automate: API – SingleChannel Rejects Invalid Frequency Range

**Description:**
*Summary:* API – SingleChannel Rejects Invalid Frequency Range

*Objective:* Verify SingleChannel view rejects configurations with invalid frequency ranges (min > max).

*Priority:* Medium

*Components/Labels:* focus-server, singlechannel, validation, negative-test

*Requirements:* FOCUS-SINGLECHANN...

---

### PZ-13819: API – SingleChannel View with Various Frequency Ranges

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13819
- **Suggested Task:** Automate: API – SingleChannel View with Various Frequency Ranges

**Description:**
*Summary:* API – SingleChannel View with Various Frequency Ranges

*Objective:* Verify SingleChannel works with different frequency configurations.

*Priority:* Low

*Components/Labels:* focus-server, singlechannel, frequency

*Requirements:* FOCUS-SINGLECHANNEL-FREQUENCY

*Pre-Conditions:*

* PC-00...

---

### PZ-13818: API – Compare SingleChannel vs MultiChannel View Types

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13818
- **Suggested Task:** Automate: API – Compare SingleChannel vs MultiChannel View Types

**Description:**
*Summary:* API – Compare SingleChannel vs MultiChannel View Types

*Objective:* Verify distinct behavior between view_type=SINGLECHANNEL (1) and view_type=MULTICHANNEL (0).

*Priority:* Medium

*Components/Labels:* focus-server, view-type, comparison

*Requirements:* FOCUS-VIEWTYPE-COMPARISON

*Pre-...

---

### PZ-13817: API – Same SingleChannel Returns Consistent Mapping Across Multiple Requests

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13817
- **Suggested Task:** Automate: API – Same SingleChannel Returns Consistent Mapping Across Multiple Requests

**Description:**
*Summary:* API – Same SingleChannel Returns Consistent Mapping Across Multiple Requests

*Objective:* Verify that requesting the same single channel multiple times returns consistent mapping.

*Priority:* High

*Components/Labels:* focus-server, singlechannel, consistency, idempotency

*Requirements...

---

### PZ-13816: API – Different SingleChannels Return Different Mappings

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13816
- **Suggested Task:** Automate: API – Different SingleChannels Return Different Mappings

**Description:**
*Summary:* API – Different SingleChannels Return Different Mappings

*Objective:* Verify that requesting different single channels returns distinct channel_to_stream_index entries.

*Priority:* High

*Components/Labels:* focus-server, singlechannel, mapping-consistency

*Requirements:* FOCUS-SINGLEC...

---

### PZ-13815: API – SingleChannel View for Channel 100 (Upper Boundary Test)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13815
- **Suggested Task:** Automate: API – SingleChannel View for Channel 100 (Upper Boundary Test)

**Description:**
*Summary:* API – SingleChannel View for Channel 100 (Upper Boundary Test)

*Objective:* Verify SingleChannel view works correctly for channel 100 (upper boundary or high channel number).

*Priority:* Medium

*Components/Labels:* focus-server, singlechannel, boundary-test

*Requirements:* FOCUS-SINGL...

---

### PZ-13814: API – SingleChannel View for Channel 1 (First Channel)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13814
- **Suggested Task:** Automate: API – SingleChannel View for Channel 1 (First Channel)

**Description:**
*Summary:* API – SingleChannel View for Channel 1 (First Channel)

*Objective:* Verify SingleChannel view works correctly for channel 1 (lower boundary test).

*Priority:* Medium

*Components/Labels:* focus-server, singlechannel, boundary-test

*Requirements:* FOCUS-SINGLECHANNEL-BOUNDARY

*Pre-Cond...

---

### PZ-13812: Data Quality – Verify Recordings Have Complete Metadata

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13812
- **Suggested Task:** Automate: Data Quality – Verify Recordings Have Complete Metadata

**Description:**
*Summary:* Data Quality – Verify Recordings Have Complete Metadata

*Objective:* Confirm recordings have all required metadata fields populated (not null/empty).

*Priority:* Medium

*Components/Labels:* mongodb, data-quality, metadata

*Requirements:* FOCUS-MONGO-METADATA

*Pre-Conditions:*

* PC-0...

---

### PZ-13810: Data Quality – Verify Critical MongoDB Indexes Exist

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13810
- **Suggested Task:** Automate: Data Quality – Verify Critical MongoDB Indexes Exist

**Description:**
*Summary:* Data Quality – Verify Critical MongoDB Indexes Exist

*Objective:* Confirm performance-critical indexes exist on recordings collection.

*Priority:* High

*Components/Labels:* mongodb, indexes, performance

*Requirements:* FOCUS-MONGO-INDEXES

*Pre-Conditions:*

* PC-001: recordings colle...

---

### PZ-13809: Data Quality – Verify Required MongoDB Collections Exist

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13809
- **Suggested Task:** Automate: Data Quality – Verify Required MongoDB Collections Exist

**Description:**
*Summary:* Data Quality – Verify Required MongoDB Collections Exist

*Objective:* Confirm all required MongoDB collections exist for Focus Server operation.

*Priority:* Critical

*Components/Labels:* mongodb, data-quality, collections

*Requirements:* FOCUS-MONGO-SCHEMA

*Pre-Conditions:*

* PC-001...

---

### PZ-13808: Infrastructure – MongoDB Quick Response Time Test (Performance)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13808
- **Suggested Task:** Automate: Infrastructure – MongoDB Quick Response Time Test (Performance)

**Description:**
*Summary:* Infrastructure – MongoDB Quick Response Time Test

*Objective:* Verify MongoDB responds to ping within acceptable time limit (<100ms).

*Priority:* Medium

*Components/Labels:* mongodb, performance, latency

*Requirements:* FOCUS-MONGO-PERFORMANCE

*Pre-Conditions:*

* PC-001: MongoDB acc...

---

### PZ-13806: Infrastructure – MongoDB Direct TCP Connection and Authentication

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13806
- **Suggested Task:** Automate: Infrastructure – MongoDB Direct TCP Connection and Authentication

**Description:**
*Summary:* Infrastructure – MongoDB Direct TCP Connection and Authentication

*Objective:* Verify Focus Server can establish direct TCP connection to MongoDB server, authenticate successfully, and execute basic ping command.

*Priority:* Critical

*Components/Labels:* focus-server, mongodb, infrastr...

---

### PZ-13800: Integration – Safe ROI Change (Within Limits)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13800
- **Suggested Task:** Automate: Integration – Safe ROI Change (Within Limits)

**Description:**
*Summary:* Dynamic ROI – Validate Safe ROI Change

*Objective:* Confirm safe ROI changes pass validation.

*Priority:* High

*Components/Labels:* focus-server, roi, safety, validation

*Requirements:* FOCUS-ROI-SAFETY

*Pre-Conditions:*

* PC-001: Safety rules configured

*Test Data:*

{code:json}Cu...

---

### PZ-13799: Integration – Unsafe ROI Shift (Large Position Change)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13799
- **Suggested Task:** Automate: Integration – Unsafe ROI Shift (Large Position Change)

**Description:**
*Summary:* Dynamic ROI – Detect Unsafe Position Shift

*Objective:* Verify detection when ROI shifts position dramatically.

*Priority:* Medium

*Components/Labels:* focus-server, roi, safety, validation

*Requirements:* FOCUS-ROI-SAFETY

*Pre-Conditions:*

* PC-001: Safety rules for position shifts...

---

### PZ-13798: Integration - Unsafe ROI Range Change (Size Change > 50%)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13798
- **Suggested Task:** Automate: Integration - Unsafe ROI Range Change (Size Change > 50%)

**Description:**
*Summary:* Dynamic ROI – Detect Unsafe Size Change

*Objective:* Verify detection of unsafe size changes (e.g., doubling or halving ROI).

*Priority:* High

*Components/Labels:* focus-server, roi, safety, validation

*Requirements:* FOCUS-ROI-SAFETY

*Pre-Conditions:*

* PC-001: Safety rules configu...

---

### PZ-13797: Integration - Unsafe ROI Change (Large Jump)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13797
- **Suggested Task:** Automate: Integration - Unsafe ROI Change (Large Jump)

**Description:**
*Summary:* Dynamic ROI – Detect Unsafe ROI Change (Large Jump)

*Objective:* Verify safety validation detects unsafe ROI changes (e.g., >50% change).

*Priority:* Critical

*Components/Labels:* focus-server, roi, safety, validation

*Requirements:* FOCUS-ROI-SAFETY

*Pre-Conditions:*

* PC-001: Safe...

---

### PZ-13796: Integration - ROI Starting at Zero

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13796
- **Suggested Task:** Automate: Integration - ROI Starting at Zero

**Description:**
*Summary:* Dynamic ROI – ROI Starting at Sensor Index 0

*Objective:* Verify ROI can start at sensor 0 (boundary).

*Priority:* Medium

*Components/Labels:* focus-server, roi, boundary

*Requirements:* FOCUS-ROI-BOUNDARY

*Pre-Conditions:*

* PC-001: RabbitMQ accessible

*Test Data:*

{code:json}ROI...

---

### PZ-13795: Integration - ROI with Large Range (Edge Case)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13795
- **Suggested Task:** Automate: Integration - ROI with Large Range (Edge Case)

**Description:**
*Summary:* Dynamic ROI – Very Large ROI Range (e.g., all sensors)

*Objective:* Test edge case where ROI covers maximum sensor range.

*Priority:* Medium

*Components/Labels:* focus-server, roi, edge-case, performance

*Requirements:* FOCUS-ROI-EDGE

*Pre-Conditions:*

* PC-001: System max sensors k...

---

### PZ-13794: Integration - ROI with Small Range (Edge Case)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13794
- **Suggested Task:** Automate: Integration - ROI with Small Range (Edge Case)

**Description:**
*Summary:* Dynamic ROI – Very Small ROI Range (e.g., 2 sensors)

*Objective:* Test edge case where ROI is very small but valid.

*Priority:* Medium

*Components/Labels:* focus-server, roi, edge-case

*Requirements:* FOCUS-ROI-EDGE

*Pre-Conditions:*

* PC-001: RabbitMQ accessible

*Test Data:*

{cod...

---

### PZ-13793: Integration - Dynamic ROI – Reject ROI with Negative End Value

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13793
- **Suggested Task:** Automate: Integration - Dynamic ROI – Reject ROI with Negative End Value

**Description:**
*Summary:* Dynamic ROI – Reject ROI with Negative End Value

*Objective:* Verify system rejects ROI with negative end sensor index.

*Priority:* High

*Components/Labels:* focus-server, roi, validation, negative-test

*Requirements:* FOCUS-ROI-VALIDATION

*Pre-Conditions:*

* PC-001: Validation enab...

---

### PZ-13792: Integration - ROI with Negative Start

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13792
- **Suggested Task:** Automate: Integration - ROI with Negative Start

**Description:**
*Summary:* Dynamic ROI – Reject ROI with Negative Start Value

*Objective:* Verify system rejects ROI with negative start sensor index.

*Priority:* High

*Components/Labels:* focus-server, roi, validation, negative-test

*Requirements:* FOCUS-ROI-VALIDATION

*Pre-Conditions:*

* PC-001: Validation ...

---

### PZ-13791: Integration - ROI with Reversed Range (Start > End)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13791
- **Suggested Task:** Automate: Integration - ROI with Reversed Range (Start > End)

**Description:**
*Summary:* Dynamic ROI – Reject Reversed ROI Range

*Objective:* Ensure system rejects ROI where start > end (reversed range).

*Priority:* Critical

*Components/Labels:* focus-server, roi, validation, negative-test

*Requirements:* FOCUS-ROI-VALIDATION

*Pre-Conditions:*

* PC-001: Safety validatio...

---

### PZ-13790: Integration - ROI with Equal Start and End (Zero Size)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13790
- **Suggested Task:** Automate: Integration - ROI with Equal Start and End (Zero Size)

**Description:**
*Summary:* Dynamic ROI – Reject ROI with Start Equal to End

*Objective:* Verify that the system rejects an ROI change where start equals end (zero-size ROI) as this is invalid.

*Priority:* High

*Components/Labels:* focus-server, roi, validation, negative-test

*Requirements:* FOCUS-ROI-VALIDATION...

---

### PZ-13789: Integration - ROI Shift (Move Range)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13789
- **Suggested Task:** Automate: Integration - ROI Shift (Move Range)

**Description:**
*Summary:* Dynamic ROI – Shift ROI Range Without Changing Size

*Objective:* Verify that shifting ROI (moving the window while keeping size constant) works correctly.

*Priority:* Medium

*Components/Labels:* focus-server, roi, shift, pan

*Requirements:* FOCUS-ROI-SHIFT

*Pre-Conditions:*

* PC-001...

---

### PZ-13788: Integration - ROI Shrinking (Decrease Range)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13788
- **Suggested Task:** Automate: Integration - ROI Shrinking (Decrease Range)

**Description:**
*Summary:* Dynamic ROI – Shrink ROI Range (Reduce Sensor Coverage)

*Objective:* Validate that shrinking the ROI range (making it smaller) works correctly for focusing on specific area.

*Priority:* Medium

*Components/Labels:* focus-server, roi, shrink, focus

*Requirements:* FOCUS-ROI-SHRINK

*Pre...

---

### PZ-13787: Integration -  ROI Expansion (Increase Range)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13787
- **Suggested Task:** Automate: Integration -  ROI Expansion (Increase Range)

**Description:**
*Summary:* Dynamic ROI – Expand ROI Range (Increase Sensor Coverage)

*Objective:* Validate that expanding the ROI range (making it larger) works correctly and system adapts to monitor more sensors.

*Priority:* Medium

*Components/Labels:* focus-server, roi, expansion

*Requirements:* FOCUS-ROI-EXP...

---

### PZ-13786: Integration - Multiple ROI Changes in Sequence

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13786
- **Suggested Task:** Automate: Integration - Multiple ROI Changes in Sequence

**Description:**
*Summary:* Dynamic ROI – Sequential ROI Changes Without System Restart

*Objective:* Verify that multiple ROI change commands can be sent in sequence without requiring system restart or causing state corruption.

*Priority:* High

*Components/Labels:* focus-server, roi, sequence, stability

*Require...

---

### PZ-13785: Integration - ROI Change with Safety Validation

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13785
- **Suggested Task:** Automate: Integration - ROI Change with Safety Validation

**Description:**
*Summary:* Dynamic ROI Change – Validate Safety Before Sending Command

*Objective:* Ensure ROI change requests undergo safety validation to prevent unsafe or destructive changes that could impact system stability.

*Priority:* Critical

*Components/Labels:* focus-server, roi, safety-validation, rab...

---

### PZ-13784: Integration - Send ROI Change Command via RabbitMQ

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13784
- **Suggested Task:** Automate: Integration - Send ROI Change Command via RabbitMQ

**Description:**
*Summary:* Dynamic ROI Change – Send RegionOfInterestCommand via RabbitMQ

*Objective:* Verify that a RegionOfInterestCommand can be successfully published to RabbitMQ Baby Analyzer exchange and accepted by the system without errors.

*Priority:* High

*Components/Labels:* focus-server, rabbitmq, ro...

---

### PZ-13769: Security – Malformed Input Handling

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13769
- **Suggested Task:** Automate: Security – Malformed Input Handling

**Description:**
*Summary:* Security – Malformed Input Handling

*Objective:* Validate input hardening against malformed/injection attempts.

*Priority:* Critical

*Components/Labels:* focus-server, security, input-validation

*Requirements:* FOCUS-SEC-ROBUSTNESS

*Pre-Conditions:*

* PC-001: Security logging enable...

---

### PZ-13767: Integration – MongoDB Outage Handling

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13767
- **Suggested Task:** Automate: Integration – MongoDB Outage Handling

**Description:**
*Summary:* Integration – MongoDB Outage Handling

*Objective:* Ensure MongoDB outage fails gracefully without launching jobs.

*Priority:* Critical

*Components/Labels:* focus-server, resilience, mongodb, outage

*Requirements:* FOCUS-RESILIENCE-MONGO

*Pre-Conditions:*

* PC-010: MongoDB can be dis...

---

### PZ-13766:  API – POST /recordings_in_time_range – Returns Recording Windows

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13766
- **Suggested Task:** Automate:  API – POST /recordings_in_time_range – Returns Recording Windows

**Description:**
*Summary:* API – POST /recordings_in_time_range – Returns Recording Windows

*Objective:* Validate endpoint returns recordings that intersect time range.

*Priority:* High

*Components/Labels:* focus-server, api, history, recordings

*Requirements:* FOCUS-API-RECORDINGS

*Pre-Conditions:*

* PC-010:...

---

### PZ-13765: API – GET /live_metadata – Returns 404 When Unavailable

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13765
- **Suggested Task:** Automate: API – GET /live_metadata – Returns 404 When Unavailable

**Description:**
*Summary:* API – GET /live_metadata – Returns 404 When Unavailable

*Objective:* Validate proper 404 when metadata not available.

*Priority:* Medium

*Components/Labels:* focus-server, api, metadata, negative-test

*Requirements:* FOCUS-API-METADATA

*Pre-Conditions:*

* PC-001: fiber_metadata NOT ...

---

### PZ-13764:  API – GET /live_metadata – Returns Metadata When Available

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13764
- **Suggested Task:** Automate:  API – GET /live_metadata – Returns Metadata When Available

**Description:**
*Summary:* API – GET /live_metadata – Returns Metadata When Available

*Objective:* Validate live metadata endpoint returns complete fiber metadata.

*Priority:* Medium

*Components/Labels:* focus-server, api, metadata, live

*Requirements:* FOCUS-API-METADATA

*Pre-Conditions:*

* PC-001: fiber_met...

---

### PZ-13762: API – GET /channels – Returns System Channel Bounds

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13762
- **Suggested Task:** Automate: API – GET /channels – Returns System Channel Bounds

**Description:**
*Summary:* API – GET /channels – Returns System Channel Bounds

*Objective:* Validate channel range endpoint returns authoritative bounds.

*Priority:* High

*Components/Labels:* focus-server, api, channels, info

*Requirements:* FOCUS-API-CHANNELS

*Pre-Conditions:*

* PC-001: API reachable
* PC-00...

---

### PZ-13761: API – POST /config/{task_id} – Invalid Frequency Range Rejection

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13761
- **Suggested Task:** Automate: API – POST /config/{task_id} – Invalid Frequency Range Rejection

**Description:**
*Summary:* API – POST /config/{task_id} – Invalid Frequency Range Rejection

*Objective:* Validate rejection of malformed frequency ranges.

*Priority:* High

*Components/Labels:* focus-server, api, validation, negative-test

*Requirements:* FOCUS-API-VALIDATION

*Pre-Conditions:*

* PC-001: API rea...

---

### PZ-13760: API – POST /config/{task_id} – Invalid Channel Range Rejection

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13760
- **Suggested Task:** Automate: API – POST /config/{task_id} – Invalid Channel Range Rejection

**Description:**
*Summary:* API – POST /config/{task_id} – Invalid Channel Range Rejection

*Objective:* Confirm server blocks illegal channel windows (min > max, negative, out of bounds).

*Priority:* High

*Components/Labels:* focus-server, api, validation, negative-test

*Requirements:* FOCUS-API-VALIDATION

*Pre...

---

### PZ-13759: API – POST /config/{task_id} – Invalid Time Range Rejection

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13759
- **Suggested Task:** Automate: API – POST /config/{task_id} – Invalid Time Range Rejection

**Description:**
*Summary:* API – POST /config/{task_id} – Invalid Time Range Rejection

*Objective:* Ensure invalid time ranges (start >= end) are rejected with proper 400 error.

*Priority:* High

*Components/Labels:* focus-server, api, validation, negative-test

*Requirements:* FOCUS-API-VALIDATION

*Pre-Conditio...

---

### PZ-13705: Data Lifecycle – Historical vs Live Recordings Classification

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13705
- **Suggested Task:** Automate: Data Lifecycle – Historical vs Live Recordings Classification

**Description:**
h2. Summary

This issue focuses on validating the classification of recordings in MongoDB, ensuring that Historical, Live, and Deleted recordings are accurately distinguished and managed. It aims to verify the functionality of the recording lifecycle and the cleanup services.

h2. Context

The objec...

---

### PZ-13687: MongoDB Recovery – Recordings Indexed After Outage

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13687
- **Suggested Task:** Automate: MongoDB Recovery – Recordings Indexed After Outage

**Description:**
Test Summary:
Validates that recordings added to storage during a MongoDB outage are automatically indexed once MongoDB recovers.

Summary: Focus Server – MongoDB Recovery and Indexing

Objective: Confirm that new recordings are indexed post-outage without manual intervention.

Priority: Crit...

---

### PZ-13685: Data Quality – Recordings Metadata Completeness

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13685
- **Suggested Task:** Automate: Data Quality – Recordings Metadata Completeness

**Description:**
Test Summary:
Verifies that all recordings in node4 have complete metadata. Missing metadata indicates data corruption and impacts history playback.

Summary: Focus Server – Recordings Metadata Completeness

Objective: Validate metadata completeness for all recordings in node4.

Priority: Cri...

---

### PZ-13683: Data Quality – MongoDB Collections Exist

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13683
- **Suggested Task:** Automate: Data Quality – MongoDB Collections Exist

**Description:**
Test Summary:
Validates that all required MongoDB collections exist. Missing collections cause Focus Server to fail during metadata queries or history playback.

Summary: Focus Server – Data Quality – MongoDB Collections Exist

Objective: Verify that base_paths, node2, and node4 collections exi...

---

### PZ-13604: Integration – Orchestrator error triggers rollback

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13604
- **Suggested Task:** Automate: Integration – Orchestrator error triggers rollback

**Description:**
- Summary: Focus Server – History configure – Mongo unavailable → 503, no orchestration
- Objective: Ensure dependency outage fails fast and clean without launching processing.
- Priority: High
- Components/Labels: focus-server, integration, history, mongo, resilience
- Requirements: FOCUS-API-C...

---

### PZ-13603: Integration – Mongo outage on History configure

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13603
- **Suggested Task:** Automate: Integration – Mongo outage on History configure

**Description:**
Summary: Focus Server – History configure – Mongo unavailable → 503, no orchestration
- Objective: Ensure dependency outage fails fast and clean without launching processing.
- Priority: High
- Components/Labels: focus-server, integration, history, mongo, resilience
- Requirements: FOCUS-API-CON...

---

### PZ-13602: Integration – RabbitMQ outage on Live configure

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13602
- **Suggested Task:** Automate: Integration – RabbitMQ outage on Live configure

**Description:**
h2. Summary

RabbitMQ is unavailable on the Live configure server, causing a fail fast situation without launching downstream resources.

h2. Context

The focus is on validating graceful upstream failure (AMQP) when RabbitMQ is blocked or credentials are invalid. This is a high-priority issue affect...

---

### PZ-13572: Security – Robustness to malformed inputs

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13572
- **Suggested Task:** Automate: Security – Robustness to malformed inputs

**Description:**
*Test Summary:*
Stress-tests input validation and basic hardening: missing/extra fields, extreme values, type violations, and simple injection attempts. Expects precise {{4xx}} responses, no server crashes, no sensitive data leakage, and correct CORS headers where applicable.

* Summary: Focus Serve...

---

### PZ-13570: E2E – Configure → Metadata → gRPC (mock)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13570
- **Suggested Task:** Automate: E2E – Configure → Metadata → gRPC (mock)

**Description:**
h2. Summary

This test flow focuses on running an end-to-end integration test for the {{/configure}} endpoint. It involves connecting to a gRPC stream and validating the data received. The test checks the time-to-first-message SLO, the integrity of the data frames, and ensures stable streaming witho...

---

### PZ-13564: API – POST /recordings_in_time_range

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13564
- **Suggested Task:** Automate: API – POST /recordings_in_time_range

**Description:**
*Test Summary:*
Checks that the endpoint returns *precise* recording windows (epoch tuples) that intersect a requested time range. Ensures ordering, non-overlap (if guaranteed), valid timestamp types, and alignment with stored recordings.

Summary: Focus Server – Recordings in time range – Returns i...

---

### PZ-13563: API - GET /metadata/{job_id} - Valid and Invalid Job ID

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13563
- **Suggested Task:** Automate: API - GET /metadata/{job_id} - Valid and Invalid Job ID

**Description:**
*Summary:* API – GET /metadata/{task_id} – Valid Task Metadata Retrieval

*Objective:* Add test for valid metadata retrieval (currently only invalid case exists).

*Priority:* High

*Components/Labels:* focus-server, api, metadata, tasks

*Requirements:* FOCUS-API-METADATA

*Pre-Conditions:*

* PC-0...

---

### PZ-13562: API – GET /live_metadata missing

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13562
- **Suggested Task:** Automate: API – GET /live_metadata missing

**Description:**
*Test Summary:*
If live fiber metadata is not available, the server returns a *clean* {{404}} with a clear message. Ensures no ambiguous {{200}} with empty payload, and no server errors.

* Summary: Focus Server – Live metadata missing – Returns 404 with clear error
* Objective: Validate clean error...

---

### PZ-13561: API – GET /live_metadata present

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13561
- **Suggested Task:** Automate: API – GET /live_metadata present

**Description:**
*Test Summary:*
When live fiber metadata exists, the endpoint returns a *complete* and well-typed structure. Confirms mandatory fields are present and values are in valid ranges (no nulls for required attributes).

* Summary: Focus Server – Live metadata present – Returns full metadata
* Objective: ...

---

### PZ-13560: API – GET /channels

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13560
- **Suggested Task:** Automate: API – GET /channels

**Description:**
*Test Summary:*
Ensures the endpoint returns the *authoritative* channel bounds (e.g., {{lowest_channel}}, {{highest_channel}}) for the deployment. Validates response schema, value ranges, and stability across calls.

* Summary: Focus Server – Channels endpoint – Returns authoritative channel bounds...

---

### PZ-13558: API - Overlap/NFFT Escalation Edge Case

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13558
- **Suggested Task:** Automate: API - Overlap/NFFT Escalation Edge Case

**Description:**
*Test Summary:*
Verifies the internal rule that when {{window_overlap}} is below a threshold, the server escalates {{internal_nfft}} up to a documented maximum and applies padding policy if needed. Ensures these derived values are reflected in metadata and remain within safe limits.

* Summary: Focu...

---

### PZ-13557: API – Waterfall view handling

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13557
- **Suggested Task:** Automate: API – Waterfall view handling

**Description:**
*Test Summary:*
Checks {{view_type=WATERFALL}} specifics: response includes Waterfall-specific parameters (e.g., display height and any view-specific derived fields) with internally consistent values. Confirms the configuration produces a stream suitable for Waterfall rendering (no schema drift vs. ...

---

### PZ-13555: API – Invalid frequency range (negative)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13555
- **Suggested Task:** Automate: API – Invalid frequency range (negative)

**Description:**
*Test Summary:*
Checks that malformed frequency ranges (negative values, {{min > max}}, unsupported units) are rejected with a {{400}} and an actionable error. Confirms the system does not continue into orchestration on bad input.

* Summary: Focus Server – Configure – Invalid frequency range reject...

---

### PZ-13554: API – Invalid channels (negative)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13554
- **Suggested Task:** Automate: API – Invalid channels (negative)

**Description:**
*Test Summary:*
Confirms the server blocks illegal channel windows (e.g., {{channels.min > channels.max}} or out-of-bounds). Verifies a {{400}} with clear error details and no partial creation of jobs or streams.

* Summary: Focus Server – Configure – channels.min > channels.max rejected
* Objective...

---

### PZ-13552: API – Invalid time range (negative)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13552
- **Suggested Task:** Automate: API – Invalid time range (negative)

**Description:**
*Test Summary:*
Ensures invalid time ranges (e.g., {{start_time >= end_time}}) are rejected. Expects a precise {{400 Bad Request}} with a helpful validation message and *no* resource allocation (no gRPC server, no job created).

* Summary: Focus Server – Configure – Invalid time range is rejected wi...

---

### PZ-13548: API – Historical configure (happy path)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13548
- **Suggested Task:** Automate: API – Historical configure (happy path)

**Description:**
*Summary:* API – POST /config/{task_id} – Historical Mode Configuration (Happy Path)

*Objective:* Validate historical configuration using /config/{task_id} endpoint with time range successfully creates a task for historical playback.

*Priority:* Critical

*Components/Labels:* focus-server, api, hi...

---

### PZ-13547: API – POST /config/{task_id} – Live Mode Configuration (Happy Path)

- **Status:** TO DO
- **Type:** Test
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13547
- **Suggested Task:** Automate: API – POST /config/{task_id} – Live Mode Configuration (Happy Path)

**Description:**
*Objective:* Validate that a valid live configuration using the /config/{task_id} endpoint successfully creates a task and returns proper confirmation.

*Priority:* Critical

*Components/Labels:* focus-server, api, live, config, task-management

*Requirements:* FOCUS-API-CONFIG

*Pre-Conditions:*

*...

---

