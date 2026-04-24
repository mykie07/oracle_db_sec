#!/bin/bash
# set -e 

echo "Starting Advanced Security Configuration (Oracle 21c DevSecOps)..."

# 1. Enable ARCHIVELOG Mode & Set Wallet Root
sqlplus -S / as sysdba <<EOF
ALTER SYSTEM SET WALLET_ROOT='/opt/oracle/oradata/dbconfig/XE/wallet' SCOPE=SPFILE;
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
ALTER DATABASE ARCHIVELOG;
ALTER DATABASE OPEN;
EXIT;
EOF

echo "ARCHIVELOG mode enabled and WALLET_ROOT set."

# 2. Initialize TDE Keystore
mkdir -p /opt/oracle/oradata/dbconfig/XE/wallet/tde

sqlplus -S / as sysdba <<EOF
-- Set TDE Configuration to use the wallet root
ALTER SYSTEM SET TDE_CONFIGURATION='KEYSTORE_CONFIGURATION=FILE' SCOPE=BOTH;

-- Create Keystore in the TDE subfolder (21c convention)
ADMINISTER KEY MANAGEMENT CREATE KEYSTORE '/opt/oracle/oradata/dbconfig/XE/wallet/tde' IDENTIFIED BY "LabPassword2026!";

-- Open Keystore
ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN IDENTIFIED BY "LabPassword2026!" CONTAINER = ALL;

-- Set Master Key
ADMINISTER KEY MANAGEMENT SET KEY IDENTIFIED BY "LabPassword2026!" WITH BACKUP CONTAINER = ALL;

-- Create AUTO-LOGIN Wallet
ADMINISTER KEY MANAGEMENT CREATE AUTO_LOGIN KEYSTORE FROM KEYSTORE '/opt/oracle/oradata/dbconfig/XE/wallet/tde' IDENTIFIED BY "LabPassword2026!";

EXIT;
EOF

echo "TDE initialized with Auto-Login."

# 3. Configure RMAN Defaults
rman target / <<EOF
CONFIGURE ENCRYPTION FOR DATABASE ON;
CONFIGURE ENCRYPTION ALGORITHM 'AES256';
EXIT;
EOF

echo "Advanced Security Configuration Complete!"
