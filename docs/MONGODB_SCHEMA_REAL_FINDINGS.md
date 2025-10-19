# MongoDB Schema - Real Findings from Production

## Discovery Date
**October 15, 2025** - Direct exploration of staging environment (10.10.10.103)

---

## 🎯 Key Findings

### ❌ **Previous Assumptions Were WRONG!**

Our tests were looking for collections named:
- `node2`
- `node4`

**Reality:** These don't exist!

---

## 📊 Actual Collections

### 1. `77e49b5d-e06a-4aae-a33e-17117418151c` (Main Recording Collection)

**Document Count:** 3,432  
**Purpose:** Recording metadata

**Schema:**
```json
{
  "_id": "6880d2eafab9b9f35aa5dd9c",
  "uuid": "38e432b0-7c87-468c-9b85-fd48462d8901",
  "start_time": "2025-03-07 07:31:34.453000",
  "end_time": "2025-03-07 09:29:34.217000",
  "deleted": false
}
```

**Fields:**
- `_id` (str): MongoDB internal ID
- `uuid` (str): Recording unique identifier
- `start_time` (datetime): Recording start timestamp
- `end_time` (datetime): Recording end timestamp
- `deleted` (bool): Soft delete flag

**Indexes:**
- `_id_`: Default MongoDB index (NON-UNIQUE - needs investigation!)

---

### 2. `77e49b5d-e06a-4aae-a33e-17117418151c-unrecognized_recordings`

**Document Count:** 2,171  
**Purpose:** Recordings that couldn't be processed/recognized

**Schema:**
```json
{
  "_id": "6880d2ecfab9b9f35aa5ddb4",
  "folder_name": "dc022cb7-ae34-4b1e-9e0e-0bfeb60a3714",
  "file_count": 1,
  "update_time": "2025-07-23 12:17:48.518000"
}
```

**Fields:**
- `_id` (str): MongoDB internal ID
- `folder_name` (str): Folder name containing unrecognized data
- `file_count` (int): Number of files in folder
- `update_time` (datetime): Last update timestamp

---

### 3. `base_paths`

**Document Count:** 1  
**Purpose:** Base storage path for recordings

**Schema:**
```json
{
  "_id": "6880d2d6a3b9812d7ecb0ebf",
  "base_path": "/prisma/root/recordings/prisma-210-1057",
  "guid": "77e49b5d-e06a-4aae-a33e-17117418151c"
}
```

**Fields:**
- `_id` (str): MongoDB internal ID
- `base_path` (str): File system path to recordings
- `guid` (str): Links to the recording collection name

---

## 🔍 Critical Insights

### 1. **Dynamic Collection Names**
- Recording collections are named by GUID
- The GUID comes from `base_paths.guid`
- **Implication:** Tests must DISCOVER collection names, not hardcode them!

### 2. **Missing Critical Indexes**
- ⚠️ No index on `uuid` (should be UNIQUE!)
- ⚠️ No indexes on `start_time` / `end_time` (performance issue!)
- ⚠️ No index on `deleted` flag

**This is a PERFORMANCE BUG!** Time range queries will be SLOW.

### 3. **High Unrecognized Recording Rate**
- 3,432 recognized recordings
- 2,171 unrecognized recordings  
- **~63% recognition rate** ← This seems problematic!

---

## 🚨 Test Implications

### Tests That Need Fixing:

#### ❌ `test_required_collections_exist()`
Current code:
```python
REQUIRED_COLLECTIONS = ["base_paths", "node2", "node4"]
```

**Fixed approach:**
```python
def test_required_collections_exist(self):
    # Step 1: Verify base_paths exists
    collections = db.list_collection_names()
    assert "base_paths" in collections
    
    # Step 2: Get GUID from base_paths
    base_path_doc = db["base_paths"].find_one()
    guid = base_path_doc["guid"]
    
    # Step 3: Verify recording collection exists (named by GUID)
    assert guid in collections
    assert f"{guid}-unrecognized_recordings" in collections
```

#### ❌ `test_node4_schema_validation()`
Should be renamed to:
```python
def test_recording_schema_validation(self):
    # Get dynamic collection name
    guid = self._get_recording_collection_guid()
    collection = db[guid]
    
    # Validate schema
    required_fields = ["uuid", "start_time", "end_time", "deleted"]
    ...
```

#### ✅ NEW TEST NEEDED: `test_recording_collection_indexes()`
```python
def test_recording_collection_indexes(self):
    """Verify critical indexes exist for performance."""
    guid = self._get_recording_collection_guid()
    collection = db[guid]
    
    indexes = collection.list_indexes()
    index_names = [idx["name"] for idx in indexes]
    
    # Critical indexes for performance
    assert any("uuid" in idx for idx in index_names), "Missing uuid index!"
    assert any("start_time" in idx for idx in index_names), "Missing start_time index!"
    assert any("end_time" in idx for idx in index_names), "Missing end_time index!"
```

#### ✅ NEW TEST NEEDED: `test_unrecognized_recording_rate()`
```python
def test_unrecognized_recording_rate(self):
    """Verify unrecognized recording rate is acceptable."""
    guid = self._get_recording_collection_guid()
    
    recognized_count = db[guid].count_documents({})
    unrecognized_count = db[f"{guid}-unrecognized_recordings"].count_documents({})
    
    total = recognized_count + unrecognized_count
    recognition_rate = recognized_count / total if total > 0 else 0
    
    # Alert if recognition rate drops below 80%
    assert recognition_rate >= 0.80, \
        f"Recognition rate too low: {recognition_rate:.1%} (expected >= 80%)"
```

---

## 📝 Action Items

1. ✅ **Update `test_mongodb_data_quality.py`**
   - Remove hardcoded collection names
   - Implement dynamic collection discovery
   - Add helper method: `_get_recording_collection_guid()`

2. 🐛 **File Performance Bug**
   - Title: "MongoDB Recording Collection Missing Critical Indexes"
   - Impact: Slow time-range queries on 3,000+ documents
   - Recommendation: Add indexes on uuid (unique), start_time, end_time, deleted

3. 🐛 **File Data Quality Bug**
   - Title: "High Unrecognized Recording Rate (37%)"
   - Impact: 2,171 out of 5,603 recordings unrecognized
   - Recommendation: Investigate why recognition fails

4. 📚 **Update Documentation**
   - Replace all references to "node4" with "recording collection (GUID-based)"
   - Document the dynamic collection naming pattern
   - Update schema diagrams

---

## 🎓 Lesson Learned

> **"Never assume the schema - always discover it first!"**

This is exactly why we built the schema discovery tool. Our initial assumptions (based on other projects or guesses) were completely wrong. The **real schema** is different!

**Tools Used:**
- `scripts/quick_mongo_explore.py` ← This saved us!
- Direct MongoDB connection to staging

**Time Saved:** Hours of debugging failing tests!

---

## 📚 Next Steps

Run the full schema discovery for detailed analysis:

```bash
py scripts/explore_mongodb_schema.py --env staging --output reports/mongodb_schema_full.json
```

Then update tests based on REAL findings, not assumptions.

