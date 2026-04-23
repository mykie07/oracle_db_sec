# Oracle Security Lab: Administrator's Playbook

Setting everything can quite messy. Running the lab may be smooth  but with all systems, it takes a a bit of effort to get things running nicely. 

This guide contains the "behind-the-scenes" administrative commands and configurations required to maintain the laboratory environment. If the database restarts or the environment is rebuilt, refer to this guide to restore security functionality.

---

## 🔑 The "Master" Credentials
| Component | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **System Admin** | `SYS` | `SecurityLab2026!` | Full Database Control |
| **Security Wallet** | N/A | `LabPassword2026!` | Master Encryption Key Vault |
| **App Admin** | `IT_ADMIN` | `Admin2026_Secure!` | DBA Access (Simulated Admin) |
| **HR Owner** | `HR` | `HR_Pass123!` | Data Owner (Redacted/VPD target) |
| **PII Owner** | `CORPORATE_PII` | `PII_Secure99!` | Sensitive Data Owner |

---

## 🚀 The "Startup" Routine
Oracle wallets do not open automatically on startup in this lab. **You must run this after every container restart** to enable TDE and Secure Backups.

### Open the Security Vault
Run this command from your host terminal:
```bash
docker exec -it oracle-security-lab-db sqlplus / as sysdba <<EOF
ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN IDENTIFIED BY "LabPassword2026!" CONTAINER = ALL;
EXIT;
EOF
```
*If this fails, TDE (Module 07) and Backups (Module 09) will throw `ORA-28365: wallet is not open`.*

---

## 🛠️ Maintenance & Configuration

### 1. Enabling ARCHIVELOG Mode
Required for real-time data protection (Module 09).
```sql
-- Connect as SYSDBA
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
ALTER DATABASE ARCHIVELOG;
ALTER DATABASE OPEN;
-- Verify
SELECT log_mode FROM v$database;
```

### 2. Initializing TDE (One-time Setup)
If you recreate the database, you must initialize the master key:
```sql
-- Open the wallet first (see Startup Routine)
ADMINISTER KEY MANAGEMENT SET KEY IDENTIFIED BY "LabPassword2026!" WITH BACKUP CONTAINER = ALL;
```

### 3. Configuring RMAN Encryption
To ensure backups are always encrypted at rest:
```bash
docker exec -it oracle-security-lab-db rman target / <<EOF
CONFIGURE ENCRYPTION FOR DATABASE ON;
CONFIGURE ENCRYPTION ALGORITHM 'AES256';
EOF
```

---

## 🔍 Troubleshooting Guide

### ORA-28365: wallet is not open
**Cause**: The database restarted or the `ADMINISTER KEY MANAGEMENT` command hasn't been run.
**Fix**: Run the **Startup Routine** command above.

### ORA-00942: table or view does not exist
**Cause**: You are likely connected as `IT_ADMIN` but querying a table without the schema prefix.
**Fix**: Use `HR.EMPLOYEES` instead of just `EMPLOYEES`.

### ORA-01017: invalid username/password
**Cause**: Using `DB_PASSWORD` for a schema user (like `HR` or `IT_ADMIN`).
**Fix**: Check the **Credentials** table at the top of this guide.

### Connection Defaults
- **CDB Root**: `localhost:1521/XE` (Use for Wallet/Audit/RMAN config)
- **PDB (Lab)**: `localhost:1521/XEPDB1` (Use for application data/PII)

---
**End of Administrator Guide**
