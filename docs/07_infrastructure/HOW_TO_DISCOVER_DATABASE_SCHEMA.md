# 🔍 How to Discover MongoDB Schema for Automation Testing

## The Problem

**"איך אני אמור לדעת מה המבנה של MongoDB שאני רוצה לבדוק?"**

This is THE fundamental question in database testing. Here's exactly how to figure it out.

---

## 🎯 Method 1: Direct MongoDB Exploration (BEST!)

### Step 1: Run the Schema Discovery Tool

```bash
# Discover entire database schema
python scripts/explore_mongodb_schema.py --env k9s --output reports/schema.json

# Also generate test code automatically
python scripts/explore_mongodb_schema.py --env k9s --generate-tests
```

### What You'll Get:

```json
{
  "discovery_timestamp": "2025-10-15T10:30:00",
  "database_name": "focus_server_db",
  "collections": {
    "node4": {
      "document_count": 1523,
      "field_analysis": {
        "uuid": {
          "types": {"str": 1523},
          "present_in_docs": "1523/1523",
          "is_always_present": true,
          "is_nullable": false
        },
        "start_time": {
          "types": {"datetime": 1520, "null": 3},
          "present_in_docs": "1523/1523",
          "is_always_present": true,
          "is_nullable": true
        }
      },
      "indexes": [
        {"name": "uuid_1", "keys": {"uuid": 1}, "unique": true}
      ]
    }
  }
}
```

### Step 2: Connect Directly to MongoDB

```bash
# SSH to the server
ssh prisma@10.10.10.150

# Connect to MongoDB
mongo focus_server_db

# Or with authentication
mongo -u admin -p password focus_server_db
```

### Step 3: Explore Collections

```javascript
// List all collections
show collections

// Output:
// base_paths
// node2
// node4
// recordings
// ...

// See document count
db.node4.count()

// Get sample document
db.node4.findOne()

// Get 10 samples to see patterns
db.node4.find().limit(10).pretty()

// Check field types
db.node4.findOne({}, {
    uuid: 1,
    start_time: 1,
    end_time: 1,
    deleted: 1
})

// Check indexes
db.node4.getIndexes()

// Check for null/missing fields
db.node4.find({start_time: null}).count()
db.node4.find({start_time: {$exists: false}}).count()
```

---

## 🎯 Method 2: Read the Source Code (Microservices)

### Step 1: Find the Data Models

```bash
# Search for MongoDB models in the microservice
cd /path/to/focus_server/microservice
grep -r "Collection\|Schema\|Model" --include="*.py"

# Look for pymongo usage
grep -r "db\[" --include="*.py"
grep -r "insert_one\|insert_many\|update_one" --include="*.py"
```

### Example from Focus Server Code:

```python
# File: microservices/focus_server/models/recording.py

class Recording:
    """Recording metadata model."""
    
    COLLECTION = "node4"
    
    REQUIRED_FIELDS = [
        "uuid",        # Unique recording ID
        "start_time",  # Recording start timestamp
        "end_time",    # Recording end timestamp
        "deleted"      # Soft delete flag
    ]
    
    def save(self, db):
        """Save recording to MongoDB."""
        return db[self.COLLECTION].insert_one({
            "uuid": self.uuid,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "deleted": False,
            "created_at": datetime.utcnow()
        })
```

### Step 2: Search for Database Operations

```bash
# Find where collections are used
grep -r "node4\|node2\|base_paths" microservices/focus_server/ --include="*.py"

# Find INSERT operations (reveals required fields)
grep -r "insert_one\|insert_many" microservices/focus_server/ --include="*.py" -A 10

# Find QUERY operations (reveals which fields are searched)
grep -r "find\|find_one" microservices/focus_server/ --include="*.py" -A 5
```

---

## 🎯 Method 3: Analyze API Responses (Reverse Engineering)

### Step 1: Capture API Responses

```python
# File: scripts/analyze_api_responses.py

import requests
import json

# Call API that returns data from MongoDB
response = requests.get("http://10.10.10.150:8080/api/recordings/list")
data = response.json()

# Save sample response
with open("api_response_sample.json", "w") as f:
    json.dump(data, f, indent=2)

# Analyze structure
for recording in data["recordings"]:
    print(f"Fields: {recording.keys()}")
    print(f"Sample: {recording}")
```

### Step 2: Map API Fields to Database Fields

```python
# API Response reveals database schema
{
  "recordings": [
    {
      "uuid": "rec-12345",
      "start_time": "2025-10-15T10:00:00Z",
      "end_time": "2025-10-15T11:00:00Z",
      "deleted": false
    }
  ]
}

# Conclusion: node4 collection must have these fields!
```

---

## 🎯 Method 4: Check for Schema Definitions

### Look for these files:

```bash
# Mongoose schemas (Node.js)
find . -name "*schema*.js" -o -name "*model*.js"

# Python models
find . -name "*models*.py" -o -name "*schema*.py"

# MongoDB migrations
find . -name "*migration*"

# Database initialization scripts
find . -name "*init*.sql" -o -name "*seed*.py"
```

---

## 🎯 Method 5: Ask the Development Team

### Questions to Ask:

```markdown
Hi Team,

I'm writing automation tests for Focus Server MongoDB interactions.
Can you help me understand:

1. **Which MongoDB collections are critical for recording functionality?**
   - We found: base_paths, node2, node4
   - Are there others?

2. **For each collection, what are the required fields?**
   - node4: uuid, start_time, end_time, deleted?
   - Are any fields optional?

3. **What indexes exist on these collections?**
   - We need to test index performance

4. **Are there any schema validation rules in MongoDB?**
   - Required fields?
   - Data type constraints?

5. **Where can I find the data models in the codebase?**
   - File paths?

6. **Are there existing integration tests I can reference?**

Thanks!
```

---

## 🎯 Method 6: Use MongoDB Compass (GUI)

1. Download [MongoDB Compass](https://www.mongodb.com/products/compass)
2. Connect to your MongoDB instance
3. Browse collections visually
4. See sample documents
5. Analyze schema tab (shows field types and frequencies)

---

## 🎯 Method 7: Check Existing Tests

```bash
# Search for existing MongoDB tests
find . -path "*/test*" -name "*.py" -exec grep -l "mongodb\|mongo\|db\[" {} \;

# Look at how they validate data
grep -r "assert.*in.*doc" tests/ --include="*.py"
grep -r "REQUIRED_FIELDS" tests/ --include="*.py"
```

---

## 📊 Practical Example: How We Discovered node4 Schema

### Step 1: Direct Exploration

```bash
ssh prisma@10.10.10.150
mongo focus_server_db
> db.node4.findOne()
{
  "_id": ObjectId("..."),
  "uuid": "recording-abc-123",
  "start_time": ISODate("2025-10-15T10:00:00Z"),
  "end_time": ISODate("2025-10-15T11:00:00Z"),
  "deleted": false,
  "channel_count": 4,
  "sample_rate": 1000
}
```

### Step 2: Check Multiple Documents

```bash
> db.node4.find().limit(100).forEach(doc => print(JSON.stringify(doc)))
# Analyze patterns - which fields ALWAYS appear?
```

### Step 3: Check for Nulls

```bash
> db.node4.find({start_time: null}).count()  # Result: 3
> db.node4.find({uuid: null}).count()        # Result: 0
```

**Conclusion:**
- `uuid` is ALWAYS present (required)
- `start_time` is USUALLY present (3 nulls found - test this edge case!)

### Step 4: Check Indexes

```bash
> db.node4.getIndexes()
[
  {
    "v": 2,
    "key": {"_id": 1},
    "name": "_id_"
  },
  {
    "v": 2,
    "key": {"uuid": 1},
    "name": "uuid_1",
    "unique": true
  },
  {
    "v": 2,
    "key": {"start_time": 1},
    "name": "start_time_1"
  }
]
```

**Conclusion:**
- `uuid` has UNIQUE index (test uniqueness constraint!)
- `start_time` is indexed (performance tests!)

---

## ✅ Final Schema Documentation Template

```python
# File: tests/fixtures/mongodb_schemas.py

"""
MongoDB Schema Definitions for Testing

Source: Direct exploration on 2025-10-15
Validated by: QA Team + Dev Team
Last Updated: 2025-10-15
"""

NODE4_SCHEMA = {
    "collection_name": "node4",
    "description": "Recording metadata and history",
    "required_fields": [
        "uuid",        # str, unique, primary identifier
        "start_time",  # datetime, recording start (can be null in 0.2% of docs)
        "end_time",    # datetime, recording end
        "deleted",     # bool, soft delete flag
    ],
    "optional_fields": [
        "channel_count",  # int
        "sample_rate",    # int
        "created_at",     # datetime
        "updated_at",     # datetime
    ],
    "indexes": [
        {"field": "uuid", "unique": True},
        {"field": "start_time", "unique": False},
        {"field": "end_time", "unique": False},
        {"field": "deleted", "unique": False},
    ],
    "known_issues": [
        "0.2% of documents have null start_time (test this!)",
        "Some old documents missing 'channel_count' field",
    ]
}
```

---

## 🚀 Quick Start Commands

```bash
# 1. Discover schema automatically
python scripts/explore_mongodb_schema.py --env k9s

# 2. Generate test code
python scripts/explore_mongodb_schema.py --env k9s --generate-tests

# 3. Run the generated tests
pytest tests/generated_mongodb_tests.py -v

# 4. Update your documentation
# Edit: tests/fixtures/mongodb_schemas.py
```

---

## 💡 Pro Tips

1. **Always sample 100+ documents** - edge cases hide in data!
2. **Check for NULL values** - even "required" fields can be null
3. **Look for old vs new documents** - schema changes over time
4. **Test edge cases you discover** - null fields, missing fields, wrong types
5. **Document your findings** - future you will thank you!

---

## 📚 References

- MongoDB Schema Design Best Practices: https://www.mongodb.com/docs/manual/core/data-modeling-introduction/
- PyMongo Documentation: https://pymongo.readthedocs.io/
- Our Schema Discovery Tool: `scripts/explore_mongodb_schema.py`

---

**Bottom Line:**  
**אין דרך אחת "נכונה" - תשלב מספר שיטות! התחל עם direct exploration, תמשיך לקוד, ותאשר עם הצוות.**

