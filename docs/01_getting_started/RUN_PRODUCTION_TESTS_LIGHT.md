# 🚀 הרצת אוטומציה על סביבת כפר סבא (Production) - בלי טסטים כבדים

**תאריך:** 2025-11-02  
**סביבה:** Production (כפר סבא)  
**מטרה:** הרצת אוטומציה ללא טסטים כבדים (200 jobs, outage tests)

---

## ✅ הפקודה הבסיסית

```powershell
pytest --env=production -m "not capacity and not mongodb_outage and not rabbitmq_outage" -v
```

**מה זה עושה:**
- ✅ מריץ על סביבת **production** (כפר סבא)
- ❌ **לא** מריץ טסטים עם marker `capacity` (200 jobs)
- ❌ **לא** מריץ טסטים עם marker `mongodb_outage`
- ❌ **לא** מריץ טסטים עם marker `rabbitmq_outage`

---

## 🎯 פקודות נוספות

### פקודה מפורטת (עם output)

```powershell
pytest --env=production -m "not capacity and not mongodb_outage and not rabbitmq_outage" -v -s --tb=short
```

### פקודה עם log level

```powershell
pytest --env=production -m "not capacity and not mongodb_outage and not rabbitmq_outage" -v --log-cli-level=INFO
```

### פקודה רק עם טסטים מהירים (ללא slow tests)

```powershell
pytest --env=production -m "not capacity and not mongodb_outage and not rabbitmq_outage and not slow" -v
```

### פקודה רק עם טסטי API

```powershell
pytest --env=production -m "api and not capacity and not mongodb_outage and not rabbitmq_outage" -v
```

---

## 📝 מה מוציא מההרצה?

### ❌ טסטים שהוצאו:

1. **200 Jobs Capacity Test:**
   - File: `tests/load/test_job_capacity_limits.py::Test200ConcurrentJobsCapacity`
   - Marker: `@pytest.mark.capacity`

2. **MongoDB Outage Tests:**
   - File: `tests/performance/test_mongodb_outage_resilience.py`
   - Marker: `@pytest.mark.mongodb_outage`

3. **RabbitMQ Outage Tests:**
   - File: `tests/infrastructure/test_rabbitmq_outage_handling.py`
   - Marker: `@pytest.mark.rabbitmq_outage`

---

## 🔍 איך לוודא שהפקודה נכונה?

### Dry Run (ללא הרצה):

```powershell
pytest --env=production -m "not capacity and not mongodb_outage and not rabbitmq_outage" --collect-only
```

זה יציג לך איזה טסטים יורץ **בלי להריץ** אותם.

---

## ⚠️ הערות חשובות

1. **סביבת Production:**
   - הקונפיגורציה מכבה אוטומטית טסטי outage ב-production
   - אבל עדיף להיות מפורש בפקודה

2. **200 Jobs Test:**
   - הטסט הזה יוצר 200 concurrent jobs
   - לא רצוי לרוץ על production!

3. **Outage Tests:**
   - טסטים אלה יכולים לגרום לבעיות ב-production
   - תמיד להוציא מההרצה!

---

## 📊 דוגמה להרצה מלאה:

```powershell
# הרץ אוטומציה על production ללא טסטים כבדים
pytest --env=production `
       -m "not capacity and not mongodb_outage and not rabbitmq_outage" `
       -v `
       -s `
       --tb=short `
       --log-cli-level=INFO
```

---

## 🔗 קבצים קשורים:

- `config/environments.yaml` - קונפיגורציית סביבות
- `pytest.ini` - הגדרות pytest
- `tests/conftest.py` - Fixtures ו-configuration

---

**סיכום:** הפקודה תהריץ את כל הטסטים על production **חוץ מ**:
- ❌ 200 Jobs Capacity Test
- ❌ MongoDB Outage Tests  
- ❌ RabbitMQ Outage Tests

✅ כל שאר הטסטים ירוצו כרגיל!

