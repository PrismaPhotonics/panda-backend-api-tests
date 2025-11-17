# 🟡 Data Quality Tests

**Category:** Data Quality (Xray-aligned)  
**Purpose:** Validate MongoDB data integrity, schema, and metadata quality

---

## 📋 What Belongs Here?

Tests that validate:
- ✅ MongoDB collection existence and structure
- ✅ Document schema validation (required fields, data types)
- ✅ Data integrity (no missing metadata, orphaned records)
- ✅ Index performance and optimization
- ✅ Soft delete implementation (deleted flag)
- ✅ Historical vs Live recording classification
- ✅ Recording metadata completeness

---

## 🧪 Current Tests

### test_mongodb_data_quality.py
MongoDB data quality and schema validation tests.

**Class:** `TestMongoDBDataQuality`

**Tests:**
1. `test_required_collections_exist` - Verify base_paths + GUID-based collections exist
2. `test_recording_schema_validation` - Validate recording documents schema
3. `test_recordings_have_all_required_metadata` - Check metadata completeness
4. `test_mongodb_indexes_exist_and_optimal` - Verify indexes for performance
5. `test_deleted_recordings_marked_properly` - Validate soft delete (T-DATA-001)
6. `test_historical_vs_live_recordings` - Verify Historical/Live distinction (T-DATA-002)

**Related Jira:**
- PZ-13598: MongoDB Collections Exist
- PZ-13684: Recording Schema Validation
- PZ-13685: Recordings Metadata Completeness
- PZ-13686: MongoDB Indexes Validation
- PZ-13687: MongoDB Recovery
- PZ-13705: Historical vs Live

---

## 🔴 IMPORTANT: MongoDB Collections

**Critical Note:** MongoDB uses **GUID-based dynamic collection names**, NOT hardcoded names!

### ❌ WRONG (old Jira documentation):
```python
collections = ["base_paths", "node2", "node4"]
```

### ✅ CORRECT (actual implementation):
```python
collections = [
    "base_paths",                              # Fixed name
    "77e49b5d-e06a-4aae-a33e-17117418151c",   # GUID (dynamic!)
    "77e49b5d-e06a-4aae-a33e-17117418151c-unrecognized_recordings"
]
```

**Our tests correctly discover the GUID dynamically from `base_paths.guid` field.**

---

## 🚀 Running Tests

```bash
# All data quality tests
pytest tests/data_quality/ -v

# Specific test
pytest tests/data_quality/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_required_collections_exist -v

# With markers
pytest -m data_quality -v
pytest -m mongodb -v
```

---

## 📊 Coverage

| Area | Status | Notes |
|------|--------|-------|
| Collection existence | ✅ Complete | Dynamic GUID discovery |
| Schema validation | ✅ Complete | All required fields |
| Metadata completeness | ✅ Complete | Live vs Historical |
| Indexes | ✅ Complete | Performance optimization |
| Soft delete | ✅ Complete | T-DATA-001 |
| Data lifecycle | ✅ Complete | T-DATA-002 |

---

**Last Updated:** 2025-10-21  
**Maintained by:** QA Automation Team

