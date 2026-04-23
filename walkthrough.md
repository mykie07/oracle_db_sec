# Oracle Database Security Laboratory: Final Walkthrough

This document summarizes the implementation and verification of the Oracle Database Security Lab. The environment is designed as a "vulnerable-by-design" training ground to teach advanced database security concepts.

## 🛠️ Infrastructure Overview
- **Database**: Oracle Database 21c Express Edition (Containerized).
- **Application Layer**: Python 3.11 with `oracledb` (Thin Mode).
- **Synthetic Data**: 2,000 Employees (HR) and 5,000 PII Records (CORPORATE_PII).

## 🛡️ Completed Security Modules

### 01. Reconnaissance (`01_recon.py`)
- **Action**: Scanned database banners and active security options.
- **Result**: Confirmed environment as Oracle 21c XE. Identified that Unified Auditing is in Mixed Mode and advanced options like Vault/Label Security are present but unconfigured.

### 02. RBAC & Privilege Auditing (`02_rbac_audit.py`)
- **Action**: Scanned for over-privileged users and "Shadow DBAs".
- **Findings**: 
    - `IT_ADMIN` has full `DBA` role.
    - `APP_SUPPORT` has dangerous `ANY` privileges (SELECT/DROP/CREATE).
    - `HR.EMPLOYEES` has a `SELECT` grant to `PUBLIC`.

### 03. Unified Auditing (`03_audit_trail.py`)
- **Action**: Created a `UNIFIED AUDIT POLICY` to monitor the `CORPORATE_PII.CLIENT_RECORDS` table.
- **Verification**: Successfully captured and retrieved audit logs showing unauthorized access timestamps and user identities.

### 04. Data Redaction (`04_data_masking.py`)
- **Action**: Implemented `DBMS_REDACT` policies.
- **Result**: SSNs are fully masked (blanked) and Credit Card numbers show only the last 4 digits for application users.

### 05. SQL Injection & Secure Coding (`05_sql_injection.py`)
- **Action**: Simulated a string-concatenation exploit vs. a bind-variable defense.
- **Result**: The exploit successfully dumped all 2,000 employees; the bind-variable version blocked the attack entirely.

### 06. Virtual Private Database / VPD (`06_row_level_security.py`)
- **Action**: Implemented Row-Level Security (RLS) using session contexts.
- **Result**: 
    - Sales Manager only sees Dept 10 records (500 rows).
    - Engineering Lead only sees Dept 30 records (500 rows).
    - `IT_ADMIN` (Exempt) sees all 2,000 records.

### 07. Transparent Data Encryption / TDE (`07_tde.py`)
- **Action**: Created a software keystore (wallet) and encrypted the `SSN` column.
- **Verification**: Metadata check confirmed `SSN` is now encrypted with `AES 192-bit` algorithm at the storage level.

### 08. Fine-Grained Auditing / FGA (`08_fga_trap.py`)
- **Action**: Created an "Administrator Trap" policy on sensitive PII columns.
- **Result**: Detected and logged a DBA (`IT_ADMIN`) attempting to "peek" at PII data, even though they have the highest system privileges.

### 09. Secure Backup & Resiliency (`09_secure_backup.py`)
- **Action**: Enabled ARCHIVELOG mode and configured RMAN encryption.
- **Result**: Verified that the USERS tablespace is backed up in encrypted format (`AES256`) and that the database is tracking transactions in real-time.

---
**Laboratory Status**: [COMPLETED]
**Vulnerabilities Identified**: 5/5
**Defense Modules Active**: 9/9
