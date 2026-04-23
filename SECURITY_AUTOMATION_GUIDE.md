# DevSecOps: Automating Database Security

This guide explains how to transition from a manual "Surgical" laboratory setup to a fully automated, scalable enterprise security pipeline using Infrastructure as Code (IaC) and Continuous Integration/Continuous Deployment (CI/CD).

---

## 🏗️ Level 1: Local Automation (Docker Init)
The first step in automation is ensuring the database is "Born Secure."

### The "Init" Pattern
Oracle Docker images look for SQL or Shell scripts in the `/docker-entrypoint-initdb.d/` directory. 
*   **Action**: Move our `setup_db.py` logic into a set of SQL scripts in this folder.
*   **Result**: Every time you run `docker compose up`, the users, schemas, and security "smells" are injected automatically before the database is even available to the network.

### Auto-Login Wallets
To eliminate the manual "Startup Routine" (opening the wallet), you convert the software keystore to an **Auto-Login** type.
*   **How**: `ADMINISTER KEY MANAGEMENT CREATE AUTO_LOGIN KEYSTORE FROM KEYSTORE '...' IDENTIFIED BY '...';`
*   **Result**: This creates a `.sso` (System Secret Store) file. Oracle uses this file to open the vault automatically on startup.

---

## 🛠️ Level 2: Infrastructure as Code (Terraform)
In a professional environment, you never click "Create Database" in a console. You use **Terraform**.

### Why Terraform for Security?
1.  **Immutability**: You define the security state (e.g., "TDE must be AES256") in a `.tf` file.
2.  **Auditability**: Your infrastructure is stored in Git. Every change to a security group or firewall rule is tracked via a Commit Hash.
3.  **Speed**: You can spin up an identical, hardened environment in Frankfurt, New York, and Singapore in minutes.

---

## 🤖 Level 3: Configuration Management (Ansible)
While Terraform builds the "House" (the server), **Ansible** manages the "Furniture" (the database settings).

### The Ansible "Security Baseline"
You can create an Ansible Playbook that runs every hour to:
*   Verify that `IT_ADMIN` still has the correct password.
*   Check that the `CATCH_DBA_PEEKING` FGA policy hasn't been dropped.
*   **Auto-Remediation**: If Ansible finds a security setting has been changed (Configuration Drift), it automatically changes it back to the compliant state.

---

## 🔄 Level 4: Continuous Security (CI/CD)
The final stage is integrating your laboratory tests into a tool like **GitHub Actions**, **GitLab CI**, or **Jenkins**.

### The "Security Gate" Pipeline
1.  **Push**: A developer pushes code to Git.
2.  **Build**: The CI/CD pipeline spins up our **Security Lab Container**.
3.  **Test**: The pipeline runs our 9 Python modules (`lab/01_recon.py` through `lab/09_secure_backup.py`).
4.  **Verify**: If the SQL injection module (05) passes or the TDE module (07) fails, the build is **Failed**.
5.  **Deploy**: Code only reaches Production if it passes all 9 security "Gates."

---

## 📈 The DevSecOps Maturity Model
| Feature | Manual Lab | Enterprise DevSecOps |
| :--- | :--- | :--- |
| **Setup** | Surgical Commands | Docker Init / Terraform |
| **Vault** | Manual Password | Auto-Login / KMS Integration |
| **Audit** | Manual Review | SIEM (Splunk) / Automated Reports |
| **Testing** | Ad-hoc Python | GitHub Actions / Pipeline Integration |
| **Compliance** | Static Document | Continuous Monitoring (Ansible) |

---
**Guide Status**: [FINAL]
