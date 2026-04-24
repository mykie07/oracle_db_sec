# 🐋 Oracle Security Lab: CLI & Tools Guide

This guide provides a reference for the most common command-line interface (CLI) operations required to manage, audit, and interact with the laboratory environment.

---

## 🛠️ Docker & Container Interaction

### 1. Accessing the Database Shell
To enter the database container and interact with the Linux OS:
```bash
docker exec -it oracle-db-auto bash
```

### 2. Accessing the App Shell
To enter the application container (where the Python lab scripts reside):
```bash
docker exec -it oracle-app-auto bash
```

---

## 🏗️ Database CLI (SQL*Plus)

### 1. Connecting as SYSDBA
The most powerful connection, used for infrastructure changes (Wallets, Auditing, RMAN).
```bash
docker exec -it oracle-db-auto sqlplus / as sysdba
```

### 2. Connecting to a Specific Schema (PDB)
Used to test data access, VPD policies, or redaction.
```bash
# Connect to HR Schema in the Pluggable Database
docker exec -it oracle-db-auto sqlplus HR/HR_Pass123!@localhost:1521/XEPDB1
```

> [!TIP]
> Once inside SQL*Plus, you can switch containers manually using:
> `ALTER SESSION SET CONTAINER = XEPDB1;`

---

## 🔍 Oracle DBSAT (Security Assessment Tool) !!! need to download and setup before use, not yet done. 

DBSAT is used to perform high-level security audits. It consists of a **Collector** and a **Reporter**.

### 1. Run the Collector
Collects metadata from the database (run this inside the `oracle-db-auto` container).
```bash
./dbsat collect sys/SecurityLab2026!@localhost:1521/XEPDB1 /opt/oracle/out/lab_assessment
```

### 2. Run the Reporter
Generates the HTML security report from the collected data.
```bash
./dbsat report /opt/oracle/out/lab_assessment
```

---

## 🤖 Automated Lab Modules

You can run the laboratory security modules directly from your host terminal.

| Module | Command | Purpose |
| :--- | :--- | :--- |
| **01 Recon** | `docker exec -it oracle-app-auto python lab/01_recon.py` | DB Version & Installed Options |
| **02 RBAC** | `docker exec -it oracle-app-auto python lab/02_rbac_audit.py` | Identifying Shadow DBAs |
| **03 Audit** | `docker exec -it oracle-app-auto python lab/03_audit_trail.py` | Unified Audit Trail Analysis |
| **04 Masking** | `docker exec -it oracle-app-auto python lab/04_data_masking.py` | Data Redaction Verification |
| **06 VPD** | `docker exec -it oracle-app-auto python lab/06_row_level_security.py` | Row-Level Filtering (VPD) |
| **07 TDE** | `docker exec -it oracle-app-auto python lab/07_tde.py` | Encryption at Rest (Wallets) |
| **09 Backup** | `docker exec -it oracle-app-auto python lab/09_secure_backup.py` | RMAN Encrypted Backups |

---

## 🔧 Useful SQL One-Liners (PowerShell Safe)

Run these quickly from your host terminal using pipes.

> [!IMPORTANT]
> On Windows (PowerShell), always use **single quotes** `'` for the SQL string to prevent PowerShell from trying to expand database variables (like `v$parameter`).

### Check Wallet Status
```powershell
echo 'SELECT status, wallet_type FROM v$encryption_wallet;' | docker exec -i oracle-db-auto sqlplus -S / as sysdba
```

### Check Active Audit Policies
```powershell
echo 'SELECT policy_name, enabled_option FROM audit_unified_enabled_policies;' | docker exec -i oracle-db-auto sqlplus -S / as sysdba
```

### Check Redaction Policies
```powershell
echo 'SELECT policy_name, enable FROM redaction_policies;' | docker exec -i oracle-db-auto sqlplus -S / as sysdba
```

### Check Current Container
```powershell
echo 'SELECT name FROM v$pdbs;' | docker exec -i oracle-db-auto sqlplus -S / as sysdba
```
