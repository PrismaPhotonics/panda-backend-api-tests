# טסטי Xray שעדיין לא ממומשים

**מקור:** xray_tests_list.txt (137 טסטים)  
**ממומשים:** 94  
**לא ממומשים:** 43  
**Out of Scope:** 12

---

## רשימת הטסטים שלא ממומשים (43 טסטים)

### קטגוריה: API Tests (15 טסטים)

| Xray ID | Summary |
|---------|---------|
| PZ-13897 | GET /sensors - Retrieve Available Sensors List |
| PZ-13813 | SingleChannel View Returns Correct 1:1 Mapping |
| PZ-13766 | POST /recordings_in_time_range - Returns Recording Windows |
| PZ-13765 | GET /live_metadata - Returns 404 When Unavailable |
| PZ-13764 | GET /live_metadata - Returns Metadata When Available |
| PZ-13761 | POST /config/{task_id} - Invalid Frequency Range Rejection |
| PZ-13760 | POST /config/{task_id} - Invalid Channel Range Rejection |
| PZ-13759 | POST /config/{task_id} - Invalid Time Range Rejection |
| PZ-13564 | POST /recordings_in_time_range |
| PZ-13563 | GET /metadata/{job_id} - Valid and Invalid Job ID |
| PZ-13562 | GET /live_metadata missing |
| PZ-13561 | GET /live_metadata present |
| PZ-13560 | GET /channels |
| PZ-13558 | Overlap/NFFT Escalation Edge Case |
| PZ-13557 | Waterfall view handling |
| PZ-13556 | SingleChannel view mapping |

### קטגוריה: Data Quality & MongoDB (12 טסטים)

| Xray ID | Summary |
|---------|---------|
| PZ-13812 | Verify Recordings Have Complete Metadata |
| PZ-13811 | Validate Recordings Document Schema |
| PZ-13810 | Verify Critical MongoDB Indexes Exist |
| PZ-13809 | Verify Required MongoDB Collections Exist |
| PZ-13808 | MongoDB Quick Response Time Test |
| PZ-13807 | MongoDB Connection Using Focus Server Config |
| PZ-13806 | MongoDB Direct TCP Connection |
| PZ-13705 | Historical vs Live Recordings Classification |
| PZ-13687 | MongoDB Recovery - Recordings Indexed After Outage |
| PZ-13685 | Recordings Metadata Completeness |
| PZ-13684 | node4 Schema Validation |
| PZ-13599 | Postgres connectivity and catalogs |

### קטגוריה: Integration & Orchestration (8 טסטים)

| Xray ID | Summary |
|---------|---------|
| PZ-13879 | Missing Required Fields (parent ticket) |
| PZ-13768 | RabbitMQ Outage Handling |
| PZ-13767 | MongoDB Outage Handling |
| PZ-13604 | Orchestrator error triggers rollback |
| PZ-13603 | Mongo outage on History configure |
| PZ-13601 | History with empty window returns 400 |
| PZ-13600 | Invalid configure does not launch orchestration |
| PZ-13570 | E2E - Configure → Metadata → gRPC (mock) |

### קטגוריה: Performance & Security (5 טסטים)

| Xray ID | Summary |
|---------|---------|
| PZ-13770 | /config Latency P95/P99 |
| PZ-13769 | Security - Malformed Input Handling |
| PZ-13572 | Security - Robustness to malformed inputs |
| PZ-13571 | Performance - /configure latency p95 |
| PZ-13299 | 4xx errors do not log stack traces |

### קטגוריה: API Response & Validation (3 טסטים)

| Xray ID | Summary |
|---------|---------|
| PZ-13298 | API - OpenAPI contract alignment |
| PZ-13297 | API - Error body uniformity |
| PZ-13296 | API - Waterfall behavior with optional fields |
| PZ-13295 | API - Time validation uses epoch |
| PZ-13294 | API - Stream endpoint reachability |
| PZ-13293 | API - metadata readiness |
| PZ-13292 | API - Response invariants |
| PZ-13291 | API - configure validation MULTICHANNEL |

---

## 📊 פירוט לפי עדיפות

### עדיפות גבוהה - Critical API Tests (10 טסטים):

**GET endpoints:**
- PZ-13897: GET /sensors
- PZ-13764, 13765: GET /live_metadata  
- PZ-13560: GET /channels (אולי כבר ממומש?)
- PZ-13563: GET /metadata/{job_id}

**POST endpoints:**
- PZ-13766, 13564: POST /recordings_in_time_range
- PZ-13759, 13760, 13761: Invalid range rejections

**זמן משוער:** 4-5 שעות

---

### עדיפות בינונית - Data Quality (12 טסטים):

**MongoDB:**
- PZ-13806-13812: MongoDB validation suite
- PZ-13684, 13685, 13687: Schema and recovery
- PZ-13705: Classification
- PZ-13599: Postgres

**זמן משוער:** 6-8 שעות

---

### עדיפות נמוכה - Integration & E2E (8 טסטים):

**Outage handling:**
- PZ-13767, 13768: Outage tests
- PZ-13603, 13604: Orchestration

**E2E:**
- PZ-13570: Configure → Metadata → gRPC

**זמן משוער:** 4-6 שעות

---

### עדיפות נמוכה - Performance & Security (13 טסטים):

**Performance:**
- PZ-13770, 13571: Latency tests

**Security:**
- PZ-13769, 13572: Malformed input

**API Quality:**
- PZ-13291-13299: API standards

**זמן משוער:** 6-8 שעות

---

## ✅ המלצה

### פעולה מיידית:
**ממש את ה-10 API Tests קריטיים**

תוצאה:
- כיסוי יעלה ל-82%
- כל ה-endpoints הבסיסיים מכוסים

### ארוך טווח:
ממש בהדרגה את Data Quality ו-Integration tests

---

**סה"כ נותרו: 43 טסטים**

