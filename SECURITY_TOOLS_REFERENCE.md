# Oracle Security Capabilities: Technical Reference

This document provides a deep dive into the Oracle Database security tools and concepts implemented in this laboratory. I am documenting to help me keep track what I used..

---

## 1. Unified Auditing
**The Tool**: `AUDIT POLICY` / `UNIFIED_AUDIT_TRAIL`
*   **What it is**: A centralized auditing framework that consolidates all audit records (SQL, RMAN, VPD, etc.) into a single, secure table.
*   **Variant used in Lab**: **Object-Level Auditing**. We created a policy specifically to monitor the `CORPORATE_PII.CLIENT_RECORDS` table.
*   **Key Advantage**: It is significantly faster than legacy auditing and can be configured to capture specific actions (like `SELECT`) while ignoring others.

## 2. Fine-Grained Auditing (FGA)
**The Tool**: `DBMS_FGA`
*   **What it is**: An advanced auditing layer that triggers only when specific **conditions** are met or specific **columns** are accessed.
*   **Variant used in Lab**: **The Admin Trap**. We set a policy that alerts whenever a user (even a DBA) queries the `SSN` or `CREDIT_CARD` columns if they are not the data owner.
*   **Key Advantage**: It can capture the exact SQL statement used by an intruder, providing high-fidelity forensic evidence.

## 3. Data Redaction
**The Tool**: `DBMS_REDACT`
*   **What it is**: A "on-the-fly" masking tool that changes the appearance of data in the query result without altering the data on the disk.
*   **Variants used in Lab**:
    *   **Full Redaction**: SSNs were completely blanked out.
    *   **Partial Redaction**: Credit Card numbers were masked except for the last 4 digits.
*   **Key Advantage**: Zero application changes required. The "masking" happens at the database exit point.

## 4. Virtual Private Database (VPD)
**The Tool**: `DBMS_RLS` (Row-Level Security)
*   **What it is**: Appends a dynamic `WHERE` clause to every user query, ensuring they only see the rows they are authorized to see.
*   **Variant used in Lab**: **Context-Driven Filtering**. We used `SYS_CONTEXT` to store the user's Department ID and filtered the `EMPLOYEES` table accordingly.
*   **Key Advantage**: It provides "True Multi-tenancy." Even a `SELECT *` query is automatically restricted by the database engine.

## 5. Transparent Data Encryption (TDE)
**The Tool**: Oracle Advanced Security (Keystore/Wallet)
*   **What it is**: Encrypts data at the storage layer (at rest).
*   **Variant used in Lab**: **Column-Level Encryption**. We encrypted only the sensitive `SSN` column using AES-192.
*   **Key Advantage**: Protects against physical theft of the database files or backups. If someone steals the `.dbf` file, the data inside is unreadable cipher text.

## 6. Secure Backups (RMAN Encryption)
**The Tool**: `RMAN` (Recovery Manager)
*   **What it is**: The industry-standard tool for Oracle backup and recovery.
*   **Variant used in Lab**: **Wallet-Linked Encryption**. We configured RMAN to use the TDE master key to encrypt backup pieces.
*   **Key Advantage**: Extends the "Security Perimeter" to your backups. This satisfies compliance requirements for "Encrypted Off-site Storage."

## 7. Role-Based Access Control (RBAC)
**The Tool**: `GRANT`, `REVOKE`, `ROLE`
*   **What it is**: The foundation of IAM (Identity & Access Management).
*   **Concept used in Lab**: **The Principle of Least Privilege**. We audited the "Shadow DBAs" (users with `ANY` privileges) to identify over-privileged accounts that should be restricted.

## 8. Real-Time Data Protection
**The Tool**: `ARCHIVELOG Mode`
*   **What it is**: A database state where every transaction log (Redo) is archived before being overwritten.
*   **Concept used in Lab**: **Zero Data Loss**. This is the technical foundation for the **ZDLRA** (Zero Data Loss Recovery Appliance) which protects against data loss between backup windows.

---
**Reference Status**: [FINAL]
