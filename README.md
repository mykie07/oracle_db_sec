# Oracle Database Security Learning Lab (Python-First)

Welcome to your hands-on security lab! This environment is designed for Python engineers to learn Oracle DB security through automation and simulation.

## Prerequisites
- Docker & Docker Compose
- Python 3.10+ (for local scripts, though a container is provided)

## Getting Started

1.  **Start the Environment**:
    ```bash
    docker compose up -d
    ```
    *Note: The first run takes ~5-10 minutes as it pulls and initializes the Oracle XE image.*

2.  **Initialize the Database**:
    Once the database is healthy (check `docker ps`), run the setup script:
    ```bash
    docker exec -it oracle-security-lab-app python lab/core/setup_db.py
    ```
    This creates the `HR` and `CORPORATE_PII` schemas and injects some "security smells".

## 🎯 Security Finding Summary
| Finding ID | Vulnerability | Description | Impact |
| :--- | :--- | :--- | :--- |
| **VULN-01** | Shadow DBA | `APP_SUPPORT` has `DROP ANY TABLE` | Data Destruction |
| **VULN-02** | Over-privileged Admin | `IT_ADMIN` has the `DBA` role | Privilege Escalation |
| **VULN-03** | Public Exposure | `HR.EMPLOYEES` granted to `PUBLIC` | Data Leakage |
| **VULN-04** | Weak Authentication | `WEAK_USER` exists with default password | Account Takeover |
| **VULN-05** | SQL Injection | `vulnerable_search` uses string concat | Full DB Dump |

## Lab Modules

Run these from within the `security-lab` container or locally (if you have the dependencies installed):

### 01: Reconnaissance
`python lab/01_recon.py`
Learn how to enumerate database features, versions, and identification banners using Python.

### 02: RBAC Audit
`python lab/02_rbac_audit.py`
Identify over-privileged users (DBAs), dangerous "ANY" privileges, and sensitive tables granted to PUBLIC.

### 03: Unified Auditing
`python lab/03_audit_trail.py`
Learn how to create audit policies and query the `UNIFIED_AUDIT_TRAIL` to track sensitive data access.

### 04: Data Redaction
`python lab/04_data_masking.py`
Implement `DBMS_REDACT` policies to mask SSNs and partially redact Credit Card numbers in real-time.

### 05: SQL Injection & Secure Coding
`python lab/05_sql_injection.py`
A practical demonstration of SQL Injection on a vulnerable Python function and how to fix it using bind variables.

### 06: Row-Level Security (VPD)
`python lab/06_row_level_security.py`
Implement Virtual Private Database (VPD) to filter data rows based on the user's session context (e.g., Sales Managers only seeing their own department).

### 07: Transparent Data Encryption (TDE)
`python lab/07_tde.py`
Configure a software keystore and encrypt sensitive columns (SSN) at the storage level.

### 09: Secure Backup & Resiliency (ZDLRA Simulation)
`python lab/09_secure_backup.py`
Verify that the database is in ARCHIVELOG mode and that backups are encrypted using the TDE wallet, simulating the security of a Zero Data Loss Recovery Appliance.

## 🛠️ Laboratory Maintenance & Reference
For detailed instructions and technical deep-dives, please refer to:
*   **[Lab Administrator's Guide](LAB_ADMIN_GUIDE.md)**: Managing the vault, restarts, and troubleshooting.
*   **[Security Tools Reference](SECURITY_TOOLS_REFERENCE.md)**: Deep dive into the security features and variants used.
*   **[Automation & CI/CD Guide](SECURITY_AUTOMATION_GUIDE.md)**: Scaling to DevSecOps, IaC, and Terraform.

## Security Warning
This lab intentionally creates **vulnerable users and configurations**. Do NOT deploy this setup to a production environment.
