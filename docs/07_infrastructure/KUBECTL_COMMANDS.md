# פקודות kubectl בסיסיות - Staging

## רשימת שירותים וכתובות

```bash
# כל השירותים בכל ה-namespaces
kubectl get svc --all-namespaces

# שירותים ב-namespace panda
kubectl get svc -n panda

# פרטים על שירות ספציפי
kubectl describe svc panda-panda-focus-server -n panda
```

## בדיקת Ingress (כתובות חיצוניות)

```bash
# כל ה-Ingress
kubectl get ingress --all-namespaces

# Ingress ב-namespace panda
kubectl get ingress -n panda

# פרטים על Ingress ספציפי
kubectl describe ingress <name> -n panda
```

## בדיקת Pods

```bash
# כל ה-Pods ב-panda
kubectl get pods -n panda

# Pod ספציפי
kubectl get pod panda-panda-focus-server-78dbcfd9d9-nzfj8 -n panda

# פרטים על Pod
kubectl describe pod panda-panda-focus-server-78dbcfd9d9-nzfj8 -n panda
```

## בדיקת Endpoints

```bash
# Endpoints של שירות
kubectl get endpoints panda-panda-focus-server -n panda

# כל ה-Endpoints
kubectl get endpoints --all-namespaces
```

## כתובות חיצוניות (External IPs)

מהפלט שלך:
- `10.10.10.100` - Ingress Controller (HTTP/HTTPS)
- `10.10.10.108` - MongoDB
- `10.10.10.107` - RabbitMQ
- `10.10.10.102` - Kubernetes Dashboard

## גישה ל-Focus Server

### כתובת חיצונית (דרך Ingress):
```
https://10.10.10.100/focus-server/
```

**דוגמאות לבדיקות:**
```bash
# Health check (/ack)
curl -k https://10.10.10.100/focus-server/ack
# תשובה: 200 OK (ריק או JSON)

# Channels
curl -k https://10.10.10.100/focus-server/channels
# תשובה: {"lowest_channel":1,"highest_channel":...}

# Configure (דורש body מלא)
curl -k -X POST https://10.10.10.100/focus-server/configure \
  -H "Content-Type: application/json" \
  -d '{"displayInfo": {...}, "channels": [...], "view_type": "..."}'
```

### Port Forwarding (לגישה מקומית):
```bash
kubectl port-forward -n panda svc/panda-panda-focus-server 5000:5000
# אז: http://localhost:5000/ack
```

### גישה פנימית (מתוך פוד בקלאסטר):
```bash
# דרך Service DNS
curl http://panda-panda-focus-server.panda:5000/ack

# דרך Cluster IP
curl http://10.43.82.139:5000/ack

# ישירות ל-Pod
kubectl exec -it panda-panda-focus-server-78dbcfd9d9-nzfj8 -n panda -- curl http://localhost:5000/ack
```

### Ingress Configuration:
- **Path:** `/focus-server(/|$)(.*)` - כל מה שאחרי `/focus-server/` מועבר ישירות
- **Rewrite:** `/$2` - הנתיב מועבר ישירות ל-backend
- **Backend:** `panda-panda-focus-server:5000`

