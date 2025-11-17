# New Production Environment - API Endpoints

## Overview
Complete API endpoint documentation for the new production environment (panda namespace).

---

## 🌐 **API Addresses**

### **1. Swagger Documentation (API Docs)**
```
https://10.10.100.100/api/swagger/#/
```
**Usage:**
- Interactive API documentation
- Test endpoints directly from browser
- View request/response schemas
- Authentication: May require login

---

### **2. Focus Server Backend API**
```
Base URL: https://10.10.100.100/focus-server/
```

**Common Endpoints:**
```bash
# Get channels
GET https://10.10.100.100/focus-server/channels

# Configure streaming job
POST https://10.10.100.100/focus-server/configure

# Get sensors list
GET https://10.10.100.100/focus-server/sensors

# Get task metadata
GET https://10.10.100.100/focus-server/metadata/task/{task_id}

# Get waterfall data
GET https://10.10.100.100/focus-server/waterfall/{task_id}

# Health check
GET https://10.10.100.100/focus-server/health
```

---

### **3. General API Base**
```
Base URL: https://10.10.100.100/api/
```
**Note:** Swagger is mounted here (`/api/swagger/`)

---

### **4. Frontend (UI)**
```
https://10.10.10.100/liveView?siteId=prisma-210-1000
```

---

## 🔐 **Authentication**

### **Swagger Access**
- URL: `https://10.10.100.100/api/swagger/#/Auth/AuthController_login`
- May require username/password
- Check with team for credentials

### **API Requests**
```python
# If authentication is required
headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}

response = requests.post(
    "https://10.10.100.100/focus-server/configure",
    json=payload,
    headers=headers,
    verify=False  # Self-signed cert
)
```

---

## 📊 **Comparison: Old vs New Environment**

| Component | Old Environment | New Environment |
|-----------|----------------|-----------------|
| **Swagger** | `https://10.10.10.150:30443/api/swagger/#/` | `https://10.10.100.100/api/swagger/#/` |
| **Backend** | `https://10.10.10.150:30443/focus-server/` | `https://10.10.100.100/focus-server/` |
| **Frontend** | `https://10.10.10.150:30443/liveView` | `https://10.10.10.100/liveView` |
| **MongoDB** | `10.10.10.103:27017` | `10.10.100.108:27017` |
| **RabbitMQ** | `10.10.10.103:5672` | `10.10.100.107:5672` |

---

## 🔧 **Testing with curl**

### Test Swagger Access
```bash
curl -k https://10.10.100.100/api/swagger/
```

### Test Focus Server Health
```bash
curl -k https://10.10.100.100/focus-server/health
```

### Test Channels Endpoint
```bash
curl -k https://10.10.100.100/focus-server/channels
```

---

## 🐍 **Testing with Python**

```python
import requests
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Test Swagger
response = requests.get(
    "https://10.10.100.100/api/swagger/",
    verify=False,
    timeout=10
)
print(f"Swagger: {response.status_code}")

# Test Focus Server
response = requests.get(
    "https://10.10.100.100/focus-server/channels",
    verify=False,
    timeout=10
)
print(f"Channels: {response.status_code}")
```

---

## 📝 **Important Notes**

### **SSL Certificates**
- All endpoints use **self-signed SSL certificates**
- Must use `verify=False` in code
- Must use `-k` / `--insecure` in curl
- Browser will show security warning (safe to proceed in dev/staging)

### **Network Access**
- Ensure you're on the correct network/VPN
- Test connectivity: `Test-NetConnection -ComputerName 10.10.100.100 -Port 443`

### **Site ID**
- Current site: `prisma-210-1000`
- Used in frontend URL and some API calls

---

## 🚀 **Quick Access Links**

Open in browser (accept security warning):
- **Swagger UI**: https://10.10.100.100/api/swagger/#/
- **Frontend**: https://10.10.10.100/liveView?siteId=prisma-210-1000
- **RabbitMQ Management**: http://10.10.100.107:15672

---

## 📞 **Support**

- Infrastructure issues → DevOps team
- API functionality issues → Development team
- Authentication issues → Check with team lead

---

**Last Updated:** 2025-10-19  
**Environment:** new_production (panda namespace)  
**Status:** ✅ Active and tested

