import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

# Connection Details
DB_USER = os.getenv("DB_USER", "sys")
DB_PASSWORD = os.getenv("DB_PASSWORD", "SecurityLab2026!")
DB_DSN = os.getenv("DB_DSN", "localhost:1521/XE")
HR_PASSWORD = os.getenv("HR_PASSWORD", "HR_Pass123!")
PII_PASSWORD = os.getenv("PII_PASSWORD", "PII_Secure99!")

def get_connection(user=DB_USER, password=DB_PASSWORD, mode=None):
    """Returns a connection to the Oracle database in Thin mode."""
    # Automatically use SYSDBA if user is 'sys' (case-insensitive)
    if user.lower() == 'sys':
        auth_mode = oracledb.AUTH_MODE_SYSDBA
    else:
        auth_mode = oracledb.AUTH_MODE_SYSDBA if mode == 'sysdba' else oracledb.AUTH_MODE_DEFAULT
    
    return oracledb.connect(
        user=user,
        password=password,
        dsn=DB_DSN,
        mode=auth_mode
    )
