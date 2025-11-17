# 🔍 Comprehensive Test Analysis Report - Focus Server

**Date:** 2025-11-09 10:11:23
**Total Tests Analyzed:** 100

---

## 📊 Executive Summary

### Test Distribution by Category

| Category | Count | Percentage |
|----------|-------|------------|
| Infrastructure | 21 | 21.0% |
| Api | 14 | 14.0% |
| Integration | 42 | 42.0% |
| Performance | 5 | 5.0% |
| Load | 2 | 2.0% |
| Data_quality | 1 | 1.0% |
| Security | 0 | 0.0% |
| Ui | 0 | 0.0% |
| Resilience | 12 | 12.0% |
| Other | 3 | 3.0% |

### Test Type Distribution

| Test Type | Count |
|-----------|-------|
| Automation | 100 |

## 📋 Detailed Analysis by Category

### Infrastructure Tests (21)

#### 1. PZ-14744: Infrastructure - Recovery Time Measurement

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, performance, recovery, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14744

**Description:** h2. Objective
Measure recovery time for each pod type.

h2. Test Type
Integration Test

h2. Priority
P2 - Medium

h2. Components/Labels
kubernetes, resilience, recovery, performance, metrics

h2. Auto...

#### 2. PZ-14743: Infrastructure - Cascading Recovery Scenarios

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, recovery, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14743

**Description:** h2. Objective
Validate cascading recovery when multiple pods are restored simultaneously.

h2. Test Type
Integration Test

h2. Priority
P2 - Medium

h2. Components/Labels
kubernetes, resilience, recov...

#### 3. PZ-14742: Infrastructure - Recovery Order Validation

- **Status:** TO DO
- **Priority:** High
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, recovery, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14742

**Description:** h2. Objective
Validate that pods recover in the correct order (MongoDB → RabbitMQ → Focus Server).

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
kubernetes, resilience...

#### 4. PZ-14741: Infrastructure - Focus Server + SEGY Recorder Down Simultaneously

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, focus-server, infrastructure_test_panda, kubernetes, resilience, segy-recorder
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14741

**Description:** h2. Objective
Validate that when both Focus Server and SEGY Recorder are down, jobs fail gracefully and recording stops.

h2. Test Type
Integration Test

h2. Priority
P2 - Medium

h2. Components/Label...

#### 5. PZ-14740: Infrastructure - RabbitMQ + Focus Server Down Simultaneously

- **Status:** TO DO
- **Priority:** High
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, focus-server, infrastructure_test_panda, kubernetes, rabbitmq, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14740

**Description:** h2. Objective
Validate that when both RabbitMQ and Focus Server are down, the system handles complete outage gracefully.

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
...

#### 6. PZ-14739: Infrastructure - MongoDB + Focus Server Down Simultaneously

- **Status:** TO DO
- **Priority:** High
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, focus-server, infrastructure_test_panda, kubernetes, mongodb, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14739

**Description:** h2. Objective
Validate that when both MongoDB and Focus Server are down, the system handles complete outage gracefully.

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
m...

#### 7. PZ-14738: Infrastructure - MongoDB + RabbitMQ Down Simultaneously

- **Status:** TO DO
- **Priority:** High
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, mongodb, rabbitmq, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14738

**Description:** h2. Objective
Validate that when both MongoDB and RabbitMQ are down, the system handles complete outage gracefully.

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
mongo...

#### 8. PZ-14737: Infrastructure - SEGY Recorder Recovery After Outage

- **Status:** TO DO
- **Priority:** High
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, resilience, segy-recorder
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14737

**Description:** h2. Objective
Validate that after SEGY Recorder outage, the system recovers automatically.

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
segy-recorder, kubernetes, res...

#### 9. PZ-14736: Infrastructure - SEGY Recorder Outage Behavior

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, resilience, segy-recorder
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14736

**Description:** h2. Objective
Validate that when SEGY Recorder is down, recording stops gracefully.

h2. Test Type
Integration Test

h2. Priority
P2 - Medium

h2. Components/Labels
segy-recorder, kubernetes, resilien...

#### 10. PZ-14734: Infrastructure - SEGY Recorder Scale Down to 0 Replicas

- **Status:** TO DO
- **Priority:** High
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, resilience, segy-recorder
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14734

**Description:** h2. Objective
Validate that when SEGY Recorder is scaled down to 0, recording stops gracefully.

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
segy-recorder, kubernetes...

#### 11. PZ-14731: Infrastructure - Focus Server Recovery After Outage

- **Status:** TO DO
- **Priority:** Highest
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, focus-server, infrastructure_test_panda, kubernetes, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14731

**Description:** h2. Objective
Validate that after Focus Server outage, the system recovers automatically.

h2. Test Type
Integration Test

h2. Priority
P0 - Critical

h2. Components/Labels
focus-server, kubernetes, r...

#### 12. PZ-14730: Infrastructure - Focus Server Outage Graceful Degradation

- **Status:** TO DO
- **Priority:** Highest
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, focus-server, infrastructure_test_panda, kubernetes, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14730

**Description:** h2. Objective
Validate that when Focus Server is down, the system handles outage gracefully.

h2. Test Type
Integration Test

h2. Priority
P0 - Critical

h2. Components/Labels
focus-server, kubernetes...

#### 13. PZ-14728: Infrastructure - Focus Server Scale Down to 0 Replicas

- **Status:** TO DO
- **Priority:** Highest
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, focus-server, infrastructure_test_panda, kubernetes, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14728

**Description:** h2. Objective
Validate that when Focus Server is scaled down to 0, the system handles the outage gracefully.

h2. Test Type
Integration Test

h2. Priority
P0 - Critical

h2. Components/Labels
focus-se...

#### 14. PZ-14725: Infrastructure - RabbitMQ Recovery After Outage

- **Status:** TO DO
- **Priority:** Highest
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, rabbitmq, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14725

**Description:** h2. Objective
Validate that after RabbitMQ outage, the system recovers automatically.

h2. Test Type
Integration Test

h2. Priority
P0 - Critical

h2. Components/Labels
rabbitmq, kubernetes, resilienc...

#### 15. PZ-14724: Infrastructure - RabbitMQ Outage Graceful Degradation

- **Status:** TO DO
- **Priority:** Highest
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, rabbitmq, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14724

**Description:** h2. Objective
Validate that when RabbitMQ is down, the system handles outage gracefully.

h2. Test Type
Integration Test

h2. Priority
P0 - Critical

h2. Components/Labels
rabbitmq, kubernetes, resili...

#### 16. PZ-14722: Infrastructure - RabbitMQ Scale Down to 0 Replicas

- **Status:** TO DO
- **Priority:** Highest
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, rabbitmq, resilience, scaling
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14722

**Description:** h2. Objective
Validate that when RabbitMQ is scaled down to 0, the system handles the outage gracefully.

h2. Test Type
Integration Test

h2. Priority
P0 - Critical

h2. Components/Labels
rabbitmq, ku...

#### 17. PZ-14719: Infrastructure - MongoDB Recovery After Outage

- **Status:** TO DO
- **Priority:** Highest
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, mongodb, recovery, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14719

**Description:** h2. Objective
Validate that after MongoDB outage, the system recovers automatically.

h2. Test Type
Integration Test

h2. Priority
P0 - Critical

h2. Components/Labels
mongodb, kubernetes, resilience,...

#### 18. PZ-14718: Infrastructure - MongoDB Outage Graceful Degradation

- **Status:** TO DO
- **Priority:** Highest
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, graceful-degradation, infrastructure_test_panda, kubernetes, mongodb, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14718

**Description:** h2. Objective
Validate that when MongoDB is down, the system handles outage gracefully with appropriate errors.

h2. Test Type
Integration Test

h2. Priority
P0 - Critical

h2. Components/Labels
mongo...

#### 19. PZ-14716: Infrastructure - MongoDB Scale Down to 0 Replicas

- **Status:** TO DO
- **Priority:** Highest
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure, infrastructure_test_panda, kubernetes, mongodb, resilience, scaling
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14716

**Description:** h2. Objective
Validate that when MongoDB is scaled down to 0, the system handles the outage gracefully and recovers after scale up.

h2. Test Type
Integration Test

h2. Priority
P0 - Critical

h2. Com...

#### 20. PZ-13900: Infrastructure - SSH Access to Production Servers

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, infrastructure_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13900

**Description:** h2. Summary

Infrastructure - SSH Access to Production Servers

h2. Objective

Validates SSH connectivity to production servers through jump host for troubleshooting and maintenance operations. SSH ac...

#### 21. PZ-13898: Infrastructure - MongoDB Direct Connection and Health Check

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, infrastructure_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13898

**Description:** h2. Summary

Infrastructure - MongoDB Direct Connection and Health Check

h2. Objective

Validates direct TCP connection to MongoDB database server and verifies basic operations (authentication, ping,...

---

### Api Tests (14)

#### 1. PZ-14101: Integration - Historic Playback - Short Duration (Rapid Window)

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14101

**Description:** h2. Summary

Integration - Historic Playback - Short Duration (Rapid Window) validates the system's ability to handle historic playback requests with very short time windows of 1 minute.

h2. Context
...

#### 2. PZ-14099: Integration - Configuration Missing channels Field

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14099

**Description:** *Test Summary:*  
Integration - Configuration Missing channels Field

*Description:*  
Validates that the system properly handles configuration requests missing the channels field. Tests required fiel...

#### 3. PZ-14092: Performance - Configuration Endpoint P95 Latency

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, performance_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14092

**Description:** *Test Summary:*  
Performance - Configuration Endpoint P95 Latency

*Description:*  
Validates that 95% of configuration requests complete within acceptable time threshold (< 500ms). Measures P95 perc...

#### 4. PZ-14091: Performance - Configuration Endpoint P99 Latency

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, performance_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14091

**Description:** *Test Summary:*  
Performance - Configuration Endpoint P99 Latency

*Description:*  
Validates that 99% of configuration requests complete within acceptable time threshold (< 1000ms). Measures P99 per...

#### 5. PZ-14033: API - Health Check Load Testing

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, api_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14033

**Description:** h3. Summary

Health check maintains acceptable response times under sustained load

h3. Component

Focus Server API

h3. Labels

* {{health-check}}
* {{api}}
* {{performance}}
* {{load}}
* {{stress}}
...

#### 6. PZ-14032: API - Health Check with SSL/TLS

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, api_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14032

**Description:** h3. Summary

Health check works correctly with SSL/TLS enabled and self-signed certificates

h3. Component

Focus Server API

h3. Labels

* {{health-check}}
* {{api}}
* {{ssl}}
* {{tls}}
* {{edge-case...

#### 7. PZ-14031: API - Health Check Response Structure Validation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, api_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14031

**Description:** h3. Summary

Health check returns valid response structure with correct JSON format

h3. Component

Focus Server API

h3. Labels

* {{health-check}}
* {{api}}
* {{validation}}
* {{positive-test}}

h3....

#### 8. PZ-14030: API - Health Check Security Headers Validation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, api_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14030

**Description:** h3. Summary

Health check handles malicious headers without crashing or exposing vulnerabilities

h3. Component

Focus Server API

h3. Labels

* {{health-check}}
* {{api}}
* {{security}}
* {{fuzzing}}...

#### 9. PZ-14029: API - Health Check with Various Headers

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, api_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14029

**Description:** h3. Summary

Health check handles requests with various HTTP headers correctly

h3. Component

Focus Server API

h3. Labels

* {{health-check}}
* {{api}}
* {{edge-case}}
* {{headers}}

h3. Test Type

...

#### 10. PZ-14028: API - Health Check Handles Concurrent Requests

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, api_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14028

**Description:** h3. Summary

Health check handles multiple concurrent requests without errors or timeouts

h3. Component

Focus Server API

h3. Labels

* {{health-check}}
* {{api}}
* {{performance}}
* {{load}}
* {{co...

#### 11. PZ-14027: API - Health Check Rejects Invalid HTTP Methods

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, api_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14027

**Description:** h3. Summary

Health check rejects invalid HTTP methods (POST, PUT, DELETE, PATCH)

h3. Component

Focus Server API

h3. Labels

* {{health-check}}
* {{api}}
* {{negative-test}}
* {{validation}}
* {{se...

#### 12. PZ-14026: API - Health Check Returns Valid Response (200 OK)

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, api_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14026

**Description:** h3. Summary

Health check returns valid response with acceptable response time

h3. Component

Focus Server API

h3. Labels

* {{health-check}}
* {{api}}
* {{positive-test}}
* {{smoke}}
* {{critical}}...

#### 13. PZ-13895: Integration – GET /channels - Enabled Channels List

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13895

**Description:** h2. Summary

GET /channels - Enabled Channels List

h2. Objective

Validates that the {{GET /channels}} endpoint returns a list of all enabled/available channels in the system. This is a critical smok...

#### 14. PZ-13860: Integration - SingleChannel Metadata Consistency

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13860

**Description:** h3. Summary

Validates that metadata returned for a SingleChannel task (via GET /metadata/{task_id}) is consistent with the configuration and reflects the single-channel setup.

h3. Objective

Verify ...

---

### Integration Tests (42)

#### 1. PZ-14100: Integration - Frequency Range Within Nyquist Limit

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14100

**Description:** *Test Summary:*  
Integration - Frequency Range Within Nyquist Limit

*Description:*  
Validates that the system correctly accepts frequency range configurations that are within the Nyquist limit (PRR...

#### 2. PZ-14098: Integration - Configuration Missing frequencyRange Field

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14098

**Description:** *Test Summary:*  
Integration - Configuration Missing frequencyRange Field

*Description:*  
Validates that the system properly handles configuration requests missing the frequencyRange field. Tests r...

#### 3. PZ-14097: Integration - Configuration Missing nfftSelection Field

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14097

**Description:** *Test Summary:*  
Integration - Configuration Missing nfftSelection Field

*Description:*  
Validates that the system properly handles configuration requests missing the nfftSelection field. Tests req...

#### 4. PZ-14095: Integration - Configuration Missing displayTimeAxisDuration Field

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14095

**Description:** *Test Summary:*  
Integration - Configuration Missing displayTimeAxisDuration Field

*Description:*  
Validates that the system properly handles configuration requests missing the displayTimeAxisDurat...

#### 5. PZ-14094: Integration - Invalid View Type - String Value

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14094

**Description:** *Test Summary:*  
Integration - Invalid View Type - String Value

*Description:*  
Validates that the system properly rejects configuration requests with view_type provided as a string instead of inte...

#### 6. PZ-14093: Integration - Invalid View Type - Out of Range

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14093

#### 7. PZ-14089: Integration - Time Range Validation - Future Timestamps Rejection

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14089

**Description:** *Test Summary:*  
Integration - Time Range Validation - Future Timestamps Rejection

*Description:*  
Validates that the Focus Server properly rejects historic playback requests with future timestamps...

#### 8. PZ-14073: Integration – Validation – Overlap Percentage Validation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024, validation
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14073

**Description:** h2. Summary

*Validation – Overlap Percentage Validation*

h2. Priority

Low

h2. Objective

Validate allowed overlap values (system may fix/derive overlap).

h2. Steps

||#||Action||Data||Expected Re...

#### 9. PZ-14072: Integration – Validation – FFT Window Size (Power of 2) Validation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024, validation
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14072

**Description:** h2. Summary

*Validation – FFT Window Size (Power of 2) Validation*

h2. Priority

High

h2. Objective

Validate that only power-of-two NFFT values are accepted.

h2. Steps

||#||Action||Data||Expecte...

#### 10. PZ-14071: Integration – Calculation Validation – Stream Amount Calculation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14071

**Description:** h2. Summary

*Calculation Validation – Stream Amount Calculation*

h2. Priority

Medium

h2. Objective

Validate relationship {{stream_amount == channel_amount}} (document deviations).

h2. Steps

||#...

#### 11. PZ-14070: Integration – Calculation Validation – MultiChannel Mapping Validation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024, validation
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14070

**Description:** h2. Summary

*Calculation Validation – MultiChannel Mapping Validation*

h2. Priority

High

h2. Objective

For MultiChannel (view_type=0), expected traditional 1:1 mapping (document discrepancies).

...

#### 12. PZ-14069: Integration – Calculation Validation – Channel Count Calculation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024, validation
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14069

**Description:** h2. Summary

*Calculation Validation – Channel Count Calculation*

h2. Test Type

Integration Test

h2. Priority

High

h2. Components/Labels

{{focus-server}}, {{api}}, {{calculations}}, {{channels}}...

#### 13. PZ-14068: Integration –  Calculation Validation – Time Window Duration Calculation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14068

**Description:** h2. Summary

*Calculation Validation – Time Window Duration Calculation*

h2. Test Type

Integration Test

h2. Priority

Low

h2. Components/Labels

{{focus-server}}, {{api}}, {{calculations}}, {{time...

#### 14. PZ-14067: Integration – Calculation Validation – Output Rate Calculation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14067

**Description:** h2. Summary

*Calculation Validation – Output Rate Calculation*

h2. Test Type

Integration Test

h2. Priority

Medium

h2. Components/Labels

{{focus-server}}, {{api}}, {{calculations}}, {{time}}, {{...

#### 15. PZ-14066: Integration – Calculation Validation – Time Resolution (lines_dt) Calculation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14066

**Description:** h2. Summary

*Calculation Validation – Time Resolution (lines_dt) Calculation*

h2. Test Type

Integration Test

h2. Priority

High

h2. Components/Labels

{{focus-server}}, {{api}}, {{calculations}},...

#### 16. PZ-14062: Integration – Calculation Validation – Nyquist Frequency Limit Validation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14062

**Description:** h2. Summary

*Calculation Validation – Nyquist Frequency Limit Validation*

h2. Test Type

Integration Test

h2. Priority

Medium

h2. Components/Labels

{{focus-server}}, {{api}}, {{calculations}}, {...

#### 17. PZ-14061: Integration – Calculation Validation – Frequency Bins Count Calculation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14061

**Description:** h2. Summary

*Calculation Validation – Frequency Bins Count Calculation*

h2. Test Type

Integration Test

h2. Priority

High

h2. Components/Labels

{{focus-server}}, {{api}}, {{calculations}}, {{fre...

#### 18. PZ-14060: Integration – Calculation Validation – Frequency Resolution Calculation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14060

**Description:** h2. Summary

*Calculation Validation – Frequency Resolution Calculation*

h2. Test Type

Integration Test

h2. Priority

High

h2. Components/Labels

{{focus-server}}, {{api}}, {{calculations}}, {{fre...

#### 19. PZ-13909: Integration - Historic Configuration Missing end_time Field

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13909

**Description:** h2. Summary

Integration - Historic Configuration Missing end_time Field

h2. Context

This issue validates that the Focus Server properly rejects historic playback configurations that lack the requir...

#### 20. PZ-13907: Integration - Historic Configuration Missing start_time Field

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13907

**Description:** ## Summary
Integration - Historic Configuration Missing start_time Field

## Objective
Validates that Focus Server properly **rejects** historic playback configurations that are missing the **requ...

#### 21. PZ-13906: Integration - Low Throughput Configuration Edge Case

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13906

**Description:** h2. Summary

Integration - Low Throughput Configuration Edge Case

h2. Objective

Tests configuration with *very low data throughput* (< 1 Mbps) to verify system behavior at the lower performance boun...

#### 22. PZ-13904: Integration - Configuration Resource Usage Estimation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13904

**Description:** h2. Summary

Integration - Configuration Resource Usage Estimation

h2. Objective

Calculates and validates estimated resource usage (CPU, Memory, Network Bandwidth) for a given configuration before t...

#### 23. PZ-13903: Integration - Frequency Range Nyquist Limit Enforcement

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13903

**Description:** h2. Summary

Integration - Frequency Range Nyquist Limit Enforcement

h2. Objective

Validates that Focus Server *enforces the Nyquist-Shannon sampling theorem* and rejects frequency ranges that excee...

#### 24. PZ-13901: Integration - NFFT Values Validation - All Supported Values

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13901

**Description:** h2. Summary

Integration - NFFT Values Validation - All Supported Values

h2. Objective

Validates that Focus Server accepts and processes all valid NFFT values (128, 256, 512, 1024, 2048, 4096). NFFT...

#### 25. PZ-13897: Integration - GET /sensors - Retrieve Available Sensors List

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13897

**Description:** h2. Summary

Integration - GET /sensors - Retrieve Available Sensors List

h2. Objective

Validates that the {{GET /sensors}} endpoint returns a complete list of all available sensors/channels in the ...

#### 26. PZ-13879: Integration – Missing Required Fields

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** For_Automation, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13879

**Description:** h2. Summary

Integration – Missing Required Fields

h2. Objective

Validates that Focus Server properly rejects configuration requests that are missing required fields (e.g., missing {{channels}}, {{f...

#### 27. PZ-13878: Integration – Invalid View Type - Out of Range

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13878

**Description:** h2. Summary

Integration – Invalid View Type - Out of Range

h2. Objective

Validates that Focus Server properly rejects configuration requests with invalid {{view_type}} values (outside the defined e...

#### 28. PZ-13877: Integration – Invalid Frequency Range - Min > Max

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13877

**Description:** h3. Summary

Validates that Focus Server properly rejects configuration requests where {{frequencyRange.min > frequencyRange.max}}.

h2. Objective

Validates that Focus Server properly rejects configu...

#### 29. PZ-13876: Integration – Invalid Channel Range - Min > Max

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13876

**Description:** h3. Summary

Validates that Focus Server properly rejects configuration requests where {{channels.min > channels.max}}, which is an invalid range.

h2. Objective

Validates that Focus Server properly ...

#### 30. PZ-13875: Integration – Invalid NFFT - Negative Value

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13875

**Description:** h3. Summary

Validates that Focus Server properly rejects configuration requests with negative {{nfftSelection}} values.

h3. Objective

Verify proper validation and error handling when attempting to ...

#### 31. PZ-13874: Integration – Invalid NFFT - Zero Value

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13874

**Description:** h3. Summary

Validates that Focus Server properly rejects configuration requests with {{nfftSelection = 0}}, which is invalid for FFT processing.

h3. Objective

Verify proper validation and error han...

#### 32. PZ-13873: integration - Valid Configuration - All Parameters

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13873

**Description:** h3. Summary

Validates that Focus Server correctly accepts and processes a fully valid configuration request with all parameters properly set.

h2. Objective

Validates that Focus Server correctly *ac...

#### 33. PZ-13872: Integration – Historic Playback Complete End-to-End Flow

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13872

**Description:** h3. Summary

Comprehensive end-to-end test for historic playback, covering configuration, polling, data collection, metadata retrieval, and completion verification.

h3. Objective

Verify that a compl...

#### 34. PZ-13871: Integration – Historic Playback - Timestamp Ordering Validation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13871

**Description:** h3. Summary

Validates that all timestamps in historic playback data are strictly ordered, with no out-of-sequence or overlapping time ranges.

h2. Objective

Validates that timestamps in historic pla...

#### 35. PZ-13870: Integration – Historic Playback - Future Timestamps

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13870

**Description:** h3. Summary

Validates that Focus Server properly handles historic playback requests with future timestamps, either rejecting them or gracefully completing with no data.

h3. Objective

Verify error h...

#### 36. PZ-13869: Integration – Historic Playback - Invalid Time Range (End Before Start)

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13869

**Description:** h3. Summary

Validates that Focus Server properly rejects historic playback requests where {{end_time}} is before {{start_time}}, returning an appropriate error.

h3. Objective

Verify proper validati...

#### 37. PZ-13868: Integration – Historic Playback - Status 208 Completion

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13868

**Description:** h3. Summary

Validates that historic playback tasks correctly reach status 208 (baby analyzer exited) upon completion, signaling end-of-data.

h2. Objective

Validates that historic playback properly ...

#### 38. PZ-13866: Integration – Historic Playback - Very Old Timestamps (No Data)

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13866

**Description:** h3. Summary

Validates that Focus Server correctly handles historic playback requests for time ranges where no data exists (e.g., 1 year ago), returning appropriate status and messages.

h3. Objective...

#### 39. PZ-13865: Integration – Historic Playback - Short Duration (1 Minute)

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13865

**Description:** h3. Summary

Validates that Focus Server can handle a very short historic playback request (1 minute), completing quickly and efficiently.

h3. Objective

Verify that historic playback works correctly...

#### 40. PZ-13863: Integration – Historic Playback - Standard 5-Minute Range

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13863

**Description:** h3. Summary

Validates that Focus Server correctly handles a standard historic playback request for a 5-minute time range, returning data from the specified historical period and completing with statu...

#### 41. PZ-13862: Integration - SingleChannel Complete Flow End-to-End

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13862

**Description:** h3. Summary

Comprehensive end-to-end test for SingleChannel view, covering configuration, data polling, metadata retrieval, reconfiguration, and cleanup, validating the complete lifecycle of a Single...

#### 42. PZ-13861: Integration - SingleChannel Stream Mapping Verification

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Integration_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13861

**Description:** h3. Summary

Validates the {{channel_to_stream_index}} mapping returned in the configuration response for various SingleChannel configurations, ensuring correct 1:1 mapping in all cases.

h3. Objectiv...

---

### Performance Tests (5)

#### 1. PZ-14090: Performance - Job Creation Time < 2 Seconds

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, performance_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14090

**Description:** *Test Summary:*  
Performance - Job Creation Time < 2 Seconds

*Description:*  
Validates that job creation completes within acceptable time limits. Measures the time from POST /configure request to r...

#### 2. PZ-14079: Performance – Memory Usage Estimation (Informational)

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, performance_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14079

**Description:** h2. Summary

*Performance – Memory Usage Estimation (Informational)*

h2. Priority

Low

h2. Objective

Estimate memory per frame: {{channels × freq_bins × bytes_per_sample}}.

h2. Assertions

* memor...

#### 3. PZ-14078: Performance – Data Rate Calculation (Informational)

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, performance_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14078

**Description:** h2. Summary

*Performance – Data Rate Calculation (Informational)*

h2. Priority

Low

h2. Objective

Estimate data rate: {{data_rate = channels × freq_bins × output_rate × bytes_per_sample}}.

h2. As...

#### 4. PZ-13905: Performance - High Throughput Configuration Stress Test

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, performance_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13905

**Description:** h2. Summary

Performance - High Throughput Configuration Stress Test

h2. Objective

Tests configuration with *very high data throughput* (> 50 Mbps) to verify system behavior under heavy load. High t...

#### 5. PZ-13896: Performance – Concurrent Task Limit

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, performance_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13896

**Description:** h2. Objective

Determines the *maximum number of concurrent tasks* the system can handle reliably. This test validates system capacity under parallel load and identifies breaking points. Understanding...

---

### Load Tests (2)

#### 1. PZ-14088: Load - 200 Jobs Capacity Stress Test

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, Load_test_panda, TS_Focus_Server_PZ-14024
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14088

**Description:** h2. Summary

Load - 200 Jobs Capacity Stress Test to validate the Focus Server's ability to handle 200 concurrent jobs.

h2. Context

This test is essential to ensure that the infrastructure meets the...

#### 2. PZ-13880: Stress - Configuration with Extreme Values 

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, stress_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13880

**Description:** h3. Summary

Validates that Focus Server can handle configuration requests with extreme (but technically valid) parameter values, such as very large channel ranges, very high NFFT, or very large canva...

---

### Data_quality Tests (1)

#### 1. PZ-13867: Data Quality – Historic Playback - Data Integrity Validation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, data_quality_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13867

**Description:** h3. Summary

Validates data integrity during historic playback by checking timestamp ordering, sensor data completeness, and absence of corrupted data.

h3. Objective

Verify that all data returned du...

---

### Resilience Tests (12)

#### 1. PZ-14735: Infrastructure - SEGY Recorder Pod Restart During Recording

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, resilience, segy-recorder
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14735

**Description:** h2. Objective
Validate that when SEGY Recorder pod restarts during recording, the system handles it gracefully.

h2. Test Type
Integration Test

h2. Priority
P2 - Medium

h2. Components/Labels
segy-re...

#### 2. PZ-14733: Infrastructure - SEGY Recorder Pod Deletion and Recreation

- **Status:** TO DO
- **Priority:** High
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, resilience, segy-recorder
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14733

**Description:** h2. Objective
Validate that when SEGY Recorder pod is deleted, Kubernetes automatically recreates it.

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
segy-recorder, kube...

#### 3. PZ-14732: Infrastructure - Focus Server Pod Status Monitoring

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, focus-server, infrastructure_test_panda, kubernetes, monitoring
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14732

**Description:** h2. Objective
Validate pod status monitoring capabilities.

h2. Test Type
Integration Test

h2. Priority
P2 - Medium

h2. Components/Labels
focus-server, kubernetes, monitoring

h2. Automation Status
...

#### 4. PZ-14729: Infrastructure - Focus Server Pod Restart During Job Creation

- **Status:** TO DO
- **Priority:** High
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, focus-server, infrastructure_test_panda, kubernetes, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14729

**Description:** h2. Objective
Validate that when Focus Server pod restarts during job creation, the operation is handled gracefully.

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
focu...

#### 5. PZ-14727: Infrastructure - Focus Server Pod Deletion and Recreation

- **Status:** TO DO
- **Priority:** Highest
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, focus-server, infrastructure, infrastructure_test_panda, kubernetes, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14727

**Description:** h2. Objective
Validate that when Focus Server pod is deleted, Kubernetes automatically recreates it.

h2. Test Type
Integration Test

h2. Priority
P0 - Critical

h2. Components/Labels
focus-server, ku...

#### 6. PZ-14726: Infrastructure - RabbitMQ Pod Status Monitoring

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, monitoring, rabbitmq
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14726

**Description:** h2. Objective
Validate pod status monitoring capabilities.

h2. Test Type
Integration Test

h2. Priority
P2 - Medium

h2. Components/Labels
rabbitmq, kubernetes, monitoring

h2. Automation Status
✅ Au...

#### 7. PZ-14723: Infrastructure - RabbitMQ Pod Restart During Operations

- **Status:** TO DO
- **Priority:** High
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, rabbitmq, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14723

**Description:** h2. Objective
Validate that when RabbitMQ pod restarts during operations, the system handles it gracefully.

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
rabbitmq, kub...

#### 8. PZ-14721: Infrastructure - RabbitMQ Pod Deletion and Recreation

- **Status:** TO DO
- **Priority:** Highest
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure, infrastructure_test_panda, kubernetes, rabbitmq, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14721

**Description:** h2. Objective
Validate that when RabbitMQ pod is deleted, Kubernetes automatically recreates it (StatefulSet).

h2. Test Type
Integration Test

h2. Priority
P0 - Critical

h2. Components/Labels
rabbit...

#### 9. PZ-14720: Infrastructure - MongoDB Pod Status Monitoring

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, mongodb, monitoring
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14720

**Description:** h2. Objective
Validate pod status monitoring capabilities.

h2. Test Type
Integration Test

h2. Priority
P2 - Medium

h2. Components/Labels
mongodb, kubernetes, monitoring

h2. Automation Status
✅ Aut...

#### 10. PZ-14717: Infrastructure - MongoDB Pod Restart During Job Creation

- **Status:** TO DO
- **Priority:** High
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure_test_panda, kubernetes, mongodb, pod-restart, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14717

**Description:** h2. Objective
Validate that when MongoDB pod restarts during job creation, the operation is handled gracefully.

h2. Test Type
Integration Test

h2. Priority
P1 - High

h2. Components/Labels
mongodb, ...

#### 11. PZ-14715: Infrastructure - MongoDB Pod Deletion and Recreation

- **Status:** TO DO
- **Priority:** Highest
- **Test Type:** Automation
- **Components:** None
- **Labels:** TS_Focus_Server_PZ-14024, infrastructure, infrastructure_test_panda, kubernetes, mongodb, pod-lifecycle, resilience
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14715

**Description:** h2. Summary

Validate the automatic recreation of a MongoDB pod in Kubernetes upon deletion and ensure system recovery.

h2. Context

This issue involves testing the resilience of the MongoDB deployme...

#### 12. PZ-13899: Infrastructure - Kubernetes Cluster Connection and Pod Health Check

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, infrastructure_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-13899

**Description:** h2. Summary

Infrastructure - Kubernetes Cluster Connection and Pod Health Check

h2. Objective

Validates connection to Kubernetes cluster API server and verifies that Focus Server pods are running a...

---

### Other Tests (3)

#### 1. PZ-14080: Historic – Spectrogram Dimensions Calculation

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, performance_test_panda
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14080

**Description:** h2. Summary

*Historic – Spectrogram Dimensions Calculation*

h2. Priority

Low

h2. Objective

Validate historic image dimensions: Width ≈ {{duration / lines_dt}}, Height = {{frequencies_amount}}.

h...

#### 2. PZ-14019: History with Empty Time Window Returns 400

- **Status:** TO DO
- **Priority:** Medium
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, historic-playback, orchestration
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14019

**Description:** h3. Summary

History with Empty Time Window Returns 400 and No Side Effects

h3. Component

Focus Server Backend API

h3. Labels

* {{historic-playback}}
* {{data-availability}}
* {{validation}}
* {{s...

#### 3. PZ-14018: Invalid Configuration Does Not Launch Orchestration

- **Status:** TO DO
- **Priority:** High
- **Test Type:** Automation
- **Components:** None
- **Labels:** Automated, TS_Focus_Server_PZ-14024, orchestration, validation
- **URL:** https://prismaphotonics.atlassian.net/browse/PZ-14018

**Description:** h3. Summary

Invalid Configuration Does Not Launch Orchestration

h3. Component

Focus Server Backend API

h3. Labels

* {{config-validation}}
* {{orchestration}}
* {{safety}}
* {{negative-test}}
* {{...

---

## ✅ Strengths

### Well-Covered Areas

1. **Infrastructure Tests** - Comprehensive coverage of MongoDB, RabbitMQ, Kubernetes
2. **API Endpoints** - Good coverage of Focus Server API endpoints
3. **Resilience Tests** - Pod resilience and recovery scenarios

## ⚠️ Weaknesses & Gaps

### Missing Test Scenarios

1. **Error Handling** - Limited coverage of error scenarios
2. **Edge Cases** - Some edge cases may be missing
3. **Performance Under Load** - More load testing scenarios needed

## 💡 Recommendations

### New Tests to Add

1. **API Error Handling Tests**
   - Test invalid request formats
   - Test missing required fields
   - Test boundary value violations

2. **Concurrency Tests**
   - Test multiple simultaneous job creations
   - Test concurrent metadata requests

3. **Data Consistency Tests**
   - Test data integrity during failures
   - Test transaction rollback scenarios

### Potentially Redundant Tests

Review tests for potential duplication:
- Similar API endpoint tests
- Overlapping infrastructure tests
