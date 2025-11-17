# Recommended Additional Tests for Focus Server Backend
**Date:** October 16, 2025  
**Author:** QA Automation Architect  
**Based on:** Investigation and debugging sessions

---

## 📊 Current Test Coverage Summary

### ✅ What You Already Have (Excellent!)

#### MongoDB & Data Quality
- ✅ `test_required_collections_exist` - Collection structure
- ✅ `test_recording_schema_validation` - Schema validation
- ✅ `test_recordings_have_all_required_metadata` - Metadata completeness
- ✅ `test_mongodb_indexes_exist_and_optimal` - Index validation
- ✅ `test_deleted_recordings_marked_properly` - Soft delete validation
- ✅ `test_historical_vs_live_recordings` - Recording classification

#### API Tests
- ✅ **Dynamic ROI Adjustment** (4 test classes, ~30 tests)
- ✅ **Historic Playback Flow** (3 test classes, ~25 tests)
- ✅ **Live Monitoring Flow** (3 test classes, ~30 tests)
- ✅ **Spectrogram Pipeline** (5 test classes, ~40 tests)
- ✅ **Single Channel View** (4 test classes, ~30 tests)

#### Infrastructure
- ✅ **MongoDB Outage Resilience** (scale-down tests)
- ✅ **External Services Connectivity**

---

## 🚀 Recommended Additional Tests

### Category 1: RabbitMQ & Message Queue (High Priority) 🔥

**Based on:** RabbitMQ integration, Baby Analyzer communication, exchange "prisma"

#### `tests/integration/messaging/test_rabbitmq_baby_analyzer.py`

```python
class TestBabyAnalyzerRabbitMQIntegration:
    """
    Test RabbitMQ communication with Baby Analyzer.
    Validates message routing, queue creation, and command delivery.
    """
    
    def test_rabbitmq_connection_established(self):
        """Verify RabbitMQ connection can be established"""
        # Test: Connect to RabbitMQ
        # Expected: Connection successful with credentials
        
    def test_prisma_exchange_exists(self):
        """Verify 'prisma' exchange exists and is configured correctly"""
        # Test: Check exchange 'prisma' type and durability
        # Expected: Exchange exists, type=topic/fanout, durable=True
        
    def test_roi_command_sent_to_baby_analyzer(self):
        """Verify ROI change command is sent via RabbitMQ"""
        # Test: Send ROI command [50, 150]
        # Expected: Message published to correct queue
        
    def test_command_message_format_validation(self):
        """Verify message format matches Baby Analyzer expectations"""
        # Test: Send command and validate JSON structure
        # Expected: Message has required fields (command, params, timestamp)
        
    def test_queue_creation_for_baby_analyzer_job(self):
        """Verify queue is created when Baby Analyzer job starts"""
        # Test: Start job, check queue existence
        # Expected: Queue created with naming pattern: baby_analyzer_{job_id}
        
    def test_message_acknowledgment_and_delivery(self):
        """Verify messages are acknowledged and not lost"""
        # Test: Send command, verify ack received
        # Expected: Message delivered and acknowledged
        
    def test_rabbitmq_connection_recovery(self):
        """Verify connection recovers after RabbitMQ restart"""
        # Test: Restart RabbitMQ pod, retry connection
        # Expected: Connection re-established within timeout
        
    def test_message_persistence_during_outage(self):
        """Verify messages persist during brief RabbitMQ outage"""
        # Test: Send command during outage, verify delivery after recovery
        # Expected: Message not lost, delivered after recovery
```

#### `tests/integration/messaging/test_rabbitmq_resilience.py`

```python
class TestRabbitMQResilience:
    """
    Test RabbitMQ resilience and failover scenarios.
    """
    
    def test_rabbitmq_pod_restart_no_message_loss(self):
        """Verify no message loss during RabbitMQ pod restart"""
        
    def test_rabbitmq_connection_timeout_handling(self):
        """Verify proper timeout handling for RabbitMQ connections"""
        
    def test_rabbitmq_queue_overflow_handling(self):
        """Verify queue overflow is handled gracefully"""
        
    def test_dead_letter_queue_for_failed_messages(self):
        """Verify failed messages go to dead-letter queue"""
```

---

### Category 2: Performance & SLA (High Priority) 🔥

**Based on:** MongoDB outage 15s vs 5s SLA, gRPC timeout 180s

#### `tests/integration/performance/test_response_time_sla.py`

```python
class TestResponseTimeSLA:
    """
    Test API response times meet SLA requirements.
    """
    
    def test_configure_endpoint_response_time_under_2s(self):
        """Verify POST /configure responds within 2 seconds (happy path)"""
        # Test: Send valid configure request
        # Expected: Response < 2000ms
        # SLA: 2s for normal operation
        
    def test_configure_endpoint_mongodb_outage_under_10s(self):
        """Verify POST /configure responds within 10s during MongoDB outage"""
        # Test: Scale MongoDB to 0, send request
        # Expected: Response < 10000ms (503 error)
        # SLA: 10s for degraded operation
        # Note: Current implementation takes 15s - this is a known issue
        
    def test_sensors_list_endpoint_response_time_under_1s(self):
        """Verify GET /sensors responds within 1 second"""
        # Test: Request sensors list
        # Expected: Response < 1000ms
        
    def test_waterfall_data_response_time_under_3s(self):
        """Verify GET /waterfall responds within 3 seconds"""
        # Test: Request waterfall data (100 rows)
        # Expected: Response < 3000ms
        
    def test_metadata_collection_time_under_5s(self):
        """Verify metadata collection completes within 5 seconds"""
        # Test: Start job, measure metadata collection time
        # Expected: Metadata ready < 5000ms
        # SLA: Based on team feedback - "supposed to be quick"
        
    def test_grpc_connection_timeout_180s(self):
        """Verify gRPC connections timeout at 180 seconds"""
        # Test: Establish gRPC connection, wait for timeout
        # Expected: Timeout after 180s ± 5s
        # SLA: Based on team feedback - "180 seconds for live and history"
```

#### `tests/integration/performance/test_throughput_limits.py`

```python
class TestThroughputLimits:
    """
    Test system throughput and rate limiting.
    """
    
    def test_high_throughput_configuration_6_4_mbps(self):
        """Verify system handles 6.4 Mbps high throughput"""
        # Already exists in test_spectrogram_pipeline.py
        # Consider adding: measure actual throughput vs expected
        
    def test_concurrent_requests_handling(self):
        """Verify system handles 10 concurrent /configure requests"""
        # Test: Send 10 parallel requests
        # Expected: All succeed, no rate limiting
        
    def test_rapid_roi_changes_no_message_loss(self):
        """Verify rapid ROI changes don't lose messages"""
        # Test: Send 100 ROI changes in 10 seconds
        # Expected: All messages delivered to Baby Analyzer
        
    def test_waterfall_polling_rate_limit(self):
        """Verify waterfall polling rate is limited to prevent overload"""
        # Test: Poll /waterfall 100 times in 1 second
        # Expected: Rate limit kicks in, 429 Too Many Requests
```

---

### Category 3: Data Integrity & Validation (Medium Priority) ⚠️

**Based on:** MongoDB schema validation, Historical vs Live classification

#### `tests/integration/data/test_recording_lifecycle.py`

```python
class TestRecordingLifecycle:
    """
    Test complete recording lifecycle from creation to deletion.
    """
    
    def test_live_recording_becomes_historical(self):
        """Verify live recording transitions to historical when end_time is set"""
        # Test: Monitor recording, wait for end_time
        # Expected: Recording has end_time, classified as historical
        
    def test_stale_recordings_detected_after_24h(self):
        """Verify recordings without end_time after 24h are flagged as stale"""
        # Test: Find recordings > 24h old with no end_time
        # Expected: Flagged as potential system crashes
        
    def test_recording_uuid_uniqueness(self):
        """Verify recording UUIDs are unique across all recordings"""
        # Test: Query all recordings, check UUID uniqueness
        # Expected: No duplicate UUIDs found
        
    def test_recording_time_range_consistency(self):
        """Verify start_time < end_time for all historical recordings"""
        # Test: Query historical recordings
        # Expected: All have start_time < end_time
        
    def test_deleted_recordings_cleanup_after_retention_period(self):
        """Verify deleted recordings are cleaned up after retention period"""
        # Test: Check recordings with deleted=True and old timestamp
        # Expected: Cleaned up after 30 days (or configured retention)
```

#### `tests/integration/data/test_partial_results_handling.py`

```python
class TestPartialResultsHandling:
    """
    Test handling of partial results in historic playback.
    Based on team clarification: "Fail-fast if no recordings, gaps allowed"
    """
    
    def test_historic_playback_no_recordings_returns_400(self):
        """Verify POST /configure returns 400 if no recordings in time range"""
        # Test: Request time range with no recordings
        # Expected: 400 Bad Request (fail-fast)
        
    def test_historic_playback_with_gaps_returns_partial_data(self):
        """Verify historic playback returns partial data with gaps"""
        # Test: Request time range with gaps (missing segments)
        # Expected: 200 OK, data with holes in middle
        
    def test_partial_results_indicate_gaps_in_metadata(self):
        """Verify metadata indicates when partial results are returned"""
        # Test: Request range with gaps
        # Expected: Metadata shows gap locations and durations
        
    def test_best_effort_mode_returns_available_data(self):
        """Verify best-effort mode returns all available data despite gaps"""
        # Test: Request with best_effort=true
        # Expected: All available segments returned
```

---

### Category 4: Error Handling & Edge Cases (Medium Priority) ⚠️

**Based on:** Connection failures, validation errors discovered

#### `tests/integration/api/test_error_handling_comprehensive.py`

```python
class TestComprehensiveErrorHandling:
    """
    Comprehensive error handling tests for all API endpoints.
    """
    
    def test_malformed_json_request_returns_400(self):
        """Verify malformed JSON returns 400 Bad Request"""
        # Test: Send invalid JSON to /configure
        # Expected: 400 with error message
        
    def test_missing_required_field_returns_422(self):
        """Verify missing required field returns 422 Unprocessable Entity"""
        # Test: Send request without 'nfft' field
        # Expected: 422 with field validation error
        
    def test_invalid_nfft_value_returns_422(self):
        """Verify invalid NFFT (not power of 2) returns 422"""
        # Test: Send nfft=1000 (not power of 2)
        # Expected: 422 with validation message
        
    def test_negative_sensor_index_returns_422(self):
        """Verify negative sensor index returns 422"""
        # Test: Send start_sensor=-1
        # Expected: 422 with validation error
        
    def test_end_sensor_less_than_start_returns_422(self):
        """Verify end_sensor < start_sensor returns 422"""
        # Test: Send start=100, end=50
        # Expected: 422 with range error
        
    def test_nonexistent_task_id_returns_404(self):
        """Verify request for nonexistent task returns 404"""
        # Test: GET /waterfall/nonexistent_task_12345
        # Expected: 404 Not Found
        
    def test_mongodb_connection_error_returns_503(self):
        """Verify MongoDB connection error returns 503 Service Unavailable"""
        # Test: Scale MongoDB to 0, send request
        # Expected: 503 with retry-after header
        
    def test_rabbitmq_connection_error_returns_503(self):
        """Verify RabbitMQ connection error returns 503"""
        # Test: Stop RabbitMQ, send configure request
        # Expected: 503 with appropriate error message
        
    def test_kubernetes_api_error_returns_503(self):
        """Verify Kubernetes API error returns 503"""
        # Test: Simulate K8s API error
        # Expected: 503 indicating orchestration failure
        
    def test_concurrent_roi_changes_last_wins(self):
        """Verify concurrent ROI changes follow last-write-wins pattern"""
        # Test: Send 2 ROI changes simultaneously
        # Expected: Last one wins, no race condition
```

---

### Category 5: Smart Recorder Integration (Low-Medium Priority) 📼

**Based on:** Team clarification - "Smart Recorder connects via AMQP to interrogator"

#### `tests/integration/recorder/test_smart_recorder_integration.py`

```python
class TestSmartRecorderIntegration:
    """
    Test Smart Recorder integration with the system.
    Based on team feedback: "AMQP connection to interrogator"
    """
    
    def test_smart_recorder_connects_via_amqp(self):
        """Verify Smart Recorder connects to interrogator via AMQP"""
        # Test: Monitor AMQP connections during recording
        # Expected: Connection from Smart Recorder to interrogator
        
    def test_smart_recorder_listens_to_fiber_data(self):
        """Verify Smart Recorder receives data from fiber (interrogator)"""
        # Test: Start recording, monitor data flow
        # Expected: Data flows from interrogator to Smart Recorder
        
    def test_smart_recorder_creates_recording_in_mongodb(self):
        """Verify Smart Recorder creates recording entry in MongoDB"""
        # Test: Start recording, check MongoDB
        # Expected: New recording with start_time, no end_time (live)
        
    def test_smart_recorder_sets_end_time_on_stop(self):
        """Verify Smart Recorder sets end_time when recording stops"""
        # Test: Stop recording, check MongoDB
        # Expected: Recording now has end_time (historical)
        
    def test_smart_recorder_handles_interrogator_disconnect(self):
        """Verify Smart Recorder handles interrogator disconnect gracefully"""
        # Test: Disconnect interrogator during recording
        # Expected: Recording marked as failed, no data loss
```

---

### Category 6: API Self-Healing Integration (Low Priority - Nice to Have) 🔧

**Based on:** API Healing Framework we built

#### `tests/api_healed/test_focus_server_with_healing.py`

```python
class TestFocusServerAPIWithHealing:
    """
    Test Focus Server API with self-healing capabilities.
    Validates that API changes are automatically detected and handled.
    """
    
    def test_configure_endpoint_healing_alternative_route(self):
        """Verify API healer finds alternative endpoint if /configure changes"""
        # Test: Use healer to call /config (old endpoint)
        # Expected: Healer finds /configure (new endpoint) automatically
        
    def test_parameter_name_change_healing(self):
        """Verify parameter name changes are automatically mapped"""
        # Test: Use healer with old param name 'nfft'
        # Expected: Healer maps to new name 'nfftSelection' if API changed
        
    def test_api_version_change_healing(self):
        """Verify API version changes are handled automatically"""
        # Test: Request /config (v1)
        # Expected: Healer tries /api/v2/config if v1 deprecated
        
    def test_healing_cache_performance_improvement(self):
        """Verify healing cache improves performance"""
        # Test: Make 100 requests with caching
        # Expected: First request slow (discovery), subsequent fast (cached)
```

---

### Category 7: UI Automation (Low Priority - Future) 🎭

**Based on:** Playwright AI Framework we built

#### `tests/ui/test_focus_server_ui_automated.py`

```python
class TestFocusServerUIAutomated:
    """
    Automated UI tests using Playwright with AI self-healing.
    """
    
    def test_login_form_submission(self):
        """Verify login form submission works"""
        
    def test_dashboard_loads_key_elements(self):
        """Verify dashboard loads with expected elements"""
        
    def test_configure_job_via_ui(self):
        """Verify job configuration through UI"""
        
    def test_view_waterfall_visualization(self):
        """Verify waterfall visualization renders correctly"""
        
    def test_ui_selector_self_healing(self):
        """Verify UI selectors auto-heal when DOM changes"""
```

---

## 📊 Prioritized Implementation Order

### Phase 1 (This Week) 🔥
1. **RabbitMQ Integration Tests** (Category 1)
   - `test_rabbitmq_baby_analyzer.py` (8 tests)
   - Priority: CRITICAL - Core messaging infrastructure

2. **Performance & SLA Tests** (Category 2)
   - `test_response_time_sla.py` (6 tests)
   - Priority: HIGH - Known SLA violations exist

### Phase 2 (Next Week) ⚠️
3. **Data Integrity Tests** (Category 3)
   - `test_recording_lifecycle.py` (5 tests)
   - `test_partial_results_handling.py` (4 tests)
   - Priority: MEDIUM - Data quality issues found

4. **Error Handling Tests** (Category 4)
   - `test_error_handling_comprehensive.py` (11 tests)
   - Priority: MEDIUM - Improve robustness

### Phase 3 (Future Sprints) 📅
5. **Smart Recorder Tests** (Category 5) - 5 tests
6. **API Healing Tests** (Category 6) - 4 tests  
7. **UI Automation Tests** (Category 7) - 5 tests

---

## 📈 Estimated Coverage Increase

| Current Coverage | After Phase 1 | After Phase 2 | After Phase 3 |
|------------------|---------------|---------------|---------------|
| ~160 tests       | ~174 tests    | ~194 tests    | ~208 tests    |
| Good ✅          | Excellent ✅  | Outstanding ✅ | World-class 🏆 |

---

## 🎯 Key Recommendations

### Must-Do (Phase 1)
1. ✅ **RabbitMQ Tests** - Critical infrastructure, zero test coverage currently
2. ✅ **SLA Tests** - Known issues (15s vs 5s), need continuous monitoring

### Should-Do (Phase 2)
3. ⚠️ **Recording Lifecycle** - Data integrity is crucial for historical playback
4. ⚠️ **Partial Results** - Clarify requirements, test edge cases

### Nice-to-Have (Phase 3)
5. 📼 **Smart Recorder** - Integration testing for full system coverage
6. 🔧 **API Healing** - Future-proof tests against API changes
7. 🎭 **UI Automation** - Complete E2E coverage

---

## 🔗 Related Documentation

- **MongoDB Issues Workflow:** `MONGODB_ISSUES_WORKFLOW.md`
- **Historical vs Live Test:** `XRAY_T_DATA_002_HISTORICAL_VS_LIVE.md`
- **API Healing Guide:** `docs/API_HEALING_GUIDE.md`
- **Playwright AI Guide:** `docs/PLAYWRIGHT_AI_GUIDE.md`
- **Technical Specifications:** `docs/TECHNICAL_SPECIFICATIONS_CLARIFICATIONS.md`

---

## 📝 Notes for Implementation

### RabbitMQ Tests
- Use `src.infrastructure.rabbitmq_manager.RabbitMQManager`
- Test against `staging` environment (10.10.10.150)
- Validate exchange `prisma`, not multiple exchanges
- Test queue creation patterns: `baby_analyzer_{job_id}`

### Performance Tests
- Use `time.time()` for response time measurement
- Assert against SLA thresholds (2s, 10s, 180s)
- Log performance metrics for trend analysis
- Consider using `pytest-benchmark` for detailed metrics

### Data Integrity Tests
- Use `src.infrastructure.mongodb_manager.MongoDBManager`
- Query recording collection dynamically (GUID-based name)
- Validate against `base_paths` collection first
- Test both `prisma` database (staging) and local MongoDB

### Error Handling Tests
- Use `pytest.raises()` for expected exceptions
- Validate HTTP status codes (400, 404, 422, 503)
- Check error response format and messages
- Ensure errors don't leak sensitive information

---

**Total Recommended New Tests:** ~48 tests  
**Total Effort:** ~3-4 weeks for full implementation  
**Expected Quality Improvement:** 30% increase in backend coverage

**Status:** 📋 Ready for Implementation  
**Next Steps:** Start with Phase 1 (RabbitMQ + SLA tests)

