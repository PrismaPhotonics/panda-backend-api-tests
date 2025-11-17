# 🔴 Performance Tests

**Category:** Performance (Xray-aligned)  
**Purpose:** Performance, latency, and load testing

**Current Tests:** 1  
**Test Functions:** 5

---

## ✅ Existing Tests

- `test_mongodb_outage_resilience.py` - MongoDB outage with SLA validation (5 tests)

---

## 📋 What Belongs Here?

Tests that validate:
- ✅ API response latency (P95, P99 percentiles)
- ✅ Load testing scenarios (ramp, steady, spike)
- ✅ Throughput under load
- ✅ Concurrent user simulation
- ✅ Query performance (MongoDB, API)
- ✅ Resource utilization under stress

---

## 🧪 Planned Tests

### Latency Tests
- POST /config/{task_id} latency (P95 < 200ms)
- POST /configure latency (P95 < 200ms)
- GET /metadata latency
- GET /channels latency

### Load Tests
- Ramp-up profile (gradual increase)
- Steady-state profile (constant load)
- Spike profile (sudden burst)

### Query Performance
- MongoDB query latency (<100ms ping)
- Time-range query performance
- Large dataset queries

---

## 🚀 Running Tests

```bash
# All performance tests
pytest tests/performance/ -v

# With markers
pytest -m performance -v
pytest -m load -v
pytest -m latency -v

# Locust load tests (if applicable)
locust -f tests/performance/locustfile.py
```

---

## 📊 Current Status

| Test Type | Status | Priority |
|-----------|--------|----------|
| **Latency (P95/P99)** | ⏳ Planned | Critical |
| **Load Tests** | ⏳ Planned | High |
| **Query Performance** | ✅ Partial | High |
| **Concurrent Users** | ⏳ Planned | Medium |

---

## 🎯 Priority Tests to Add

**Critical (from Xray analysis):**

1. **PZ-13770:** POST /config/{task_id} - P95 latency < 200ms
2. **PZ-13808:** MongoDB ping - latency < 100ms
3. **PZ-13920:** P95 latency < 500ms (implemented)
4. **PZ-13921:** P99 latency < 1000ms (implemented)
4. **PZ-13431:** Load test - Ramp profile
5. **PZ-13432:** Load test - Steady profile
6. **PZ-13433:** Load test - Spike profile

---

## ⚡ Performance Targets

| Metric | Target | Critical |
|--------|--------|----------|
| API P95 latency | < 200ms | < 500ms |
| API P99 latency | < 500ms | < 1000ms |
| MongoDB ping | < 100ms | < 200ms |
| Throughput | > 100 req/s | > 50 req/s |
| Error rate | < 1% | < 5% |

---

## 📚 Tools

- **pytest-benchmark** - For microbenchmarks
- **Locust** - For load testing
- **pytest-timeout** - For timeout enforcement
- **py-spy** - For profiling (if needed)

---

**Last Updated:** 2025-10-21  
**Status:** ⏳ Placeholder - Critical tests to be implemented  
**Maintained by:** QA Automation Team

