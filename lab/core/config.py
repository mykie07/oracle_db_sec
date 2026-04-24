import os
import oracledb
from dotenv import load_dotenv

# Smart Environment Loading
if os.getenv("LAB_ENV") == "AUTOMATED":
    load_dotenv(".env.auto")
else:
    load_dotenv() # Defaults to .env

# Ensure the root directory is in sys.path for container execution
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

# Connection Details
DB_USER = os.getenv("DB_USER", "sys")
DB_PASSWORD = os.getenv("DB_PASSWORD", "SecurityLab2026!")
DB_DSN = os.getenv("DB_DSN", "localhost:1521/XE")
HR_PASSWORD = os.getenv("HR_PASSWORD", "HR_Pass123!")
PII_PASSWORD = os.getenv("PII_PASSWORD", "PII_Secure99!")

def _parse_dsn(dsn):
    """Internal helper to parse DSN into (host_port, service)."""
    if '/' in dsn:
        return dsn.rsplit('/', 1)
    return dsn, "XE"

def get_cdb_dsn():
    """Returns the DSN for the CDB Root."""
    host_port, _ = _parse_dsn(DB_DSN)
    return f"{host_port}/XE"

def get_pdb_dsn():
    """Returns the DSN for the PDB (XEPDB1)."""
    host_port, _ = _parse_dsn(DB_DSN)
    return f"{host_port}/XEPDB1"

def get_connection(user=DB_USER, password=DB_PASSWORD, mode=None, service=None):
    """Returns a connection to the Oracle database in Thin mode."""
    dsn = DB_DSN
    if service:
        host_port, _ = _parse_dsn(DB_DSN)
        dsn = f"{host_port}/{service}"
        
    # Automatically use SYSDBA if user is 'sys' (case-insensitive)
    if user.lower() == 'sys':
        auth_mode = oracledb.AUTH_MODE_SYSDBA
    else:
        auth_mode = oracledb.AUTH_MODE_SYSDBA if mode == 'sysdba' else oracledb.AUTH_MODE_DEFAULT
    
    return oracledb.connect(
        user=user,
        password=password,
        dsn=dsn,
        mode=auth_mode
    )
