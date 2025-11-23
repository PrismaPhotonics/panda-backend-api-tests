# התחברות ל-worker-node

## אם אתה כבר על worker-node:

אם אתה רואה `prisma@worker-node:~$` - אתה כבר שם! לא צריך להתחבר שוב.

## אם אתה צריך להתחבר:

### דרך 1: דרך jump host (כמו שעשית קודם)

```bash
# 1. התחבר ל-jump host
ssh root@10.10.10.10

# 2. משם התחבר ל-worker-node
ssh prisma@10.10.10.150
```

### דרך 2: ישירות (אם יש לך SSH key)

```bash
ssh prisma@10.10.10.150
```

אם זה לא עובד, השתמש בדרך 1.

---

## אחרי שהתחברת:

```bash
# בדוק שאתה על worker-node
hostname
# צריך להראות: worker-node

# בדוק גישה ל-Focus Server
curl -k https://10.10.10.100/focus-server/channels

# אם זה עובד, אתה מוכן להתקין את ה-runner!
```

