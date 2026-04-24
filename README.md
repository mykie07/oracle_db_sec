# Oracle Database Security Learning Lab

Welcome to the **Oracle Database Security Laboratory**. This project is a containerized, "vulnerable-by-design" environment built for security engineers to master Oracle defense-in-depth through automation.

---

## 🚀 Choose Your Lab Path

This project supports two distinct learning tracks:

### Option A: The Manual Learning Lab (Port 1521)
Best for learning the "surgical" administrative commands. You build the defense layer by layer.
```bash
# 1. Start the containers
docker compose up -d

# 2. Initialize the vulnerable state
docker exec -it oracle-security-lab-app python lab/core/setup_db.py
```

### Option B: The Automated DevSecOps Lab (Port 1522)
Best for testing automation and CI/CD. This environment is "Born Secure" with all data, schemas, and **Auto-Login encryption wallets** active on startup.
```bash
# 1. Start the autonomous stack
docker compose -f docker-compose-auto.yml up -d

# 2. Watch the progress (Wait for "DATABASE IS READY")
docker logs -f oracle-db-auto
```
*   **Interactive Control**: Use **[Oracle_Security_Lab_Automated.ipynb](Oracle_Security_Lab_Automated.ipynb)**

### 🛑 Shutting Down
To stop the lab and free up system resources:
```bash
# Stop Manual Lab
docker compose down

# Stop Automated Lab
docker compose -f docker-compose-auto.yml down
```
*Note: Add `-v` to the commands above to also delete all persistent database data.*

---

## 📚 Module Syllabus

| Module | Defense Concept | Description |
| :--- | :--- | :--- |
| **01** | **Reconnaissance** | Enumerating DB features and version banners. |
| **02** | **RBAC Audit** | Identifying over-privileged "Shadow DBAs". |
| **03** | **Unified Auditing** | Creating centralized audit policies for PII access. |
| **04** | **Data Redaction** | Implementing on-the-fly masking via `DBMS_REDACT`. |
| **05** | **Secure Coding** | Mitigating SQL Injection with bind variables. |
| **06** | **Row-Level Security**| Implementing VPD (Virtual Private Database). |
| **07** | **Data-at-Rest** | Configuring TDE (Transparent Data Encryption). |
| **08** | **The Admin Trap** | Using FGA (Fine-Grained Auditing) to catch DBAs peeking at data. |
| **09** | **Resiliency** | Configuring Encrypted Backups and ARCHIVELOG mode. |

---

## 🎯 Security Finding Summary (The Target)
| Finding ID | Vulnerability | Impact |
| :--- | :--- | :--- |
| **VULN-01** | Shadow DBA | `APP_SUPPORT` has `DROP ANY TABLE` |
| **VULN-02** | Over-privileged Admin | `IT_ADMIN` has the `DBA` role |
| **VULN-03** | Public Exposure | `HR.EMPLOYEES` granted to `PUBLIC` |
| **VULN-04** | Weak Authentication | `WEAK_USER` exists with default password |
| **VULN-05** | SQL Injection | `vulnerable_search` uses string concat |

---

## 🛠️ Maintenance & Reference Guides
*   **[Lab Administrator's Guide](LAB_ADMIN_GUIDE.md)**: Manual wallet commands and troubleshooting.
*   **[Security Tools Reference](SECURITY_TOOLS_REFERENCE.md)**: Deep dive into the "Why" and "How" of Oracle tools.
*   **[Automation & CI/CD Guide](SECURITY_AUTOMATION_GUIDE.md)**: Scaling to DevSecOps and Terraform.
*   **[DevSecOps Implementation](DEVSECOPS_IMPLEMENTATION.md)**: The technical blueprint for the automated stack.

## ⚠️ Security Warning
This lab intentionally creates **vulnerable users and configurations**. Do NOT deploy this setup to a production environment.
