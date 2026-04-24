import oracledb
import os
from lab.core.config import get_connection
from rich.console import Console

console = Console()

def setup_tde():
    """Sets up TDE keystore and encrypts columns."""
    from lab.core.config import DB_USER, DB_PASSWORD, get_cdb_dsn, get_pdb_dsn
    
    # Dynamic DSNs based on environment
    cdb_dsn = get_cdb_dsn()
    pdb_dsn = get_pdb_dsn()
    
    # Unified Password
    WALLET_PASS = "SecurityLab2026!"
    
    try:
        console.print("[yellow]Checking current encryption status...[/yellow]")
        pdb_conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=pdb_dsn, mode=oracledb.AUTH_MODE_SYSDBA)
        pdb_cursor = pdb_conn.cursor()
        pdb_cursor.execute("SELECT encryption_alg FROM dba_encrypted_columns WHERE owner = 'CORPORATE_PII' AND table_name = 'CLIENT_RECORDS' AND column_name = 'SSN'")
        row = pdb_cursor.fetchone()
        if row:
            console.print(f"[green]TDE is already active. SSN is encrypted with {row[0]}.[/green]")
            pdb_conn.close()
            return
        pdb_conn.close()
        
        console.print("[yellow]Setting up Transparent Data Encryption (TDE)...[/yellow]")
        
        # 1. Connect to CDB Root
        console.print(f"[dim]Connecting to CDB Root ({cdb_dsn}) for Infrastructure Setup...[/dim]")
        cdb_conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=cdb_dsn, mode=oracledb.AUTH_MODE_SYSDBA)
        cdb_cursor = cdb_conn.cursor()
        
        # 2. Check WALLET_ROOT
        cdb_cursor.execute("SELECT value FROM v$parameter WHERE name = 'wallet_root'")
        wallet_root = cdb_cursor.fetchone()[0]
        
        if not wallet_root or wallet_root == '':
            console.print("[bold red]ERROR:[/bold red] WALLET_ROOT is not set in this environment.")
            console.print("[yellow]Please run the following command in SQL*Plus to initialize the vault directory:[/yellow]")
            console.print(f'[cyan]ALTER SYSTEM SET WALLET_ROOT = "/opt/oracle/oradata/dbconfig/XE/wallet" SCOPE=SPFILE;[/cyan]')
            console.print("[yellow]Then RESTART the database container to apply changes.[/yellow]")
            cdb_conn.close()
            return

        # 3. Create/Open Keystore
        console.print("[dim]Creating/Opening keystore in CDB...[/dim]")
        try:
            # Oracle 21c requires the 'tde' subdirectory under WALLET_ROOT
            cdb_cursor.execute(f"ADMINISTER KEY MANAGEMENT CREATE KEYSTORE IDENTIFIED BY \"{WALLET_PASS}\"")
        except oracledb.DatabaseError as e:
            if "ORA-28328" in str(e) or "ORA-46630" in str(e):
                console.print("[blue]Keystore already exists.[/blue]")
            else:
                raise e
                
        try:
            cdb_cursor.execute(f"ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN IDENTIFIED BY \"{WALLET_PASS}\"")
        except oracledb.DatabaseError as e:
            if "ORA-28322" in str(e) or "ORA-28354" in str(e):
                console.print("[blue]Keystore already open (possibly as AUTOLOGIN).[/blue]")
            else:
                raise e
        
        try:
            cdb_cursor.execute(f"ADMINISTER KEY MANAGEMENT SET KEY IDENTIFIED BY \"{WALLET_PASS}\" WITH BACKUP")
        except oracledb.DatabaseError as e:
            if "ORA-28339" in str(e):
                console.print("[blue]Master key already set in CDB.[/blue]")
            elif "ORA-28417" in str(e):
                console.print("[yellow]Note: Password-based keystore not open in CDB (AUTOLOGIN). Proceeding...[/yellow]")
            else:
                raise e
        cdb_conn.close()

        # 4. Open Keystore in PDB (XEPDB1)
        console.print(f"[dim]Opening keystore in PDB ({pdb_dsn})...[/dim]")
        pdb_conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=pdb_dsn, mode=oracledb.AUTH_MODE_SYSDBA)
        pdb_cursor = pdb_conn.cursor()
        
        try:
            pdb_cursor.execute(f"ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN IDENTIFIED BY \"{WALLET_PASS}\"")
        except oracledb.DatabaseError as e:
            if "ORA-28322" in str(e) or "ORA-28354" in str(e):
                console.print("[blue]Keystore already open in PDB.[/blue]")
            else:
                raise e
        
        try:
            pdb_cursor.execute(f"ADMINISTER KEY MANAGEMENT SET KEY IDENTIFIED BY \"{WALLET_PASS}\" WITH BACKUP")
        except oracledb.DatabaseError as e:
            if "ORA-28339" in str(e):
                console.print("[blue]Master key already set in PDB.[/blue]")
            elif "ORA-28417" in str(e):
                console.print("[yellow]Note: Password-based keystore not open in PDB. Proceeding to check if encryption works anyway...[/yellow]")
            else:
                raise e
        
        # 5. Encrypt the SSN column
        console.print("[yellow]Encrypting CORPORATE_PII.CLIENT_RECORDS(SSN) column...[/yellow]")
        try:
            pdb_cursor.execute("ALTER TABLE CORPORATE_PII.CLIENT_RECORDS MODIFY (SSN ENCRYPT)")
        except oracledb.DatabaseError as e:
            if "ORA-28424" in str(e) or "ORA-28334" in str(e):
                console.print("[blue]Column already encrypted.[/blue]")
            elif "ORA-28331" in str(e):
                console.print("[red]ERROR:[/red] Master key not found. You may need to manually initialize the TDE wallet in this container.")
                raise e
            else:
                raise e
        
        pdb_conn.commit()
        console.print("[green]TDE is now active. The SSN column is encrypted at rest.[/green]")
        
        # Verify
        pdb_cursor.execute("SELECT column_name, encryption_alg FROM dba_encrypted_columns WHERE owner = 'CORPORATE_PII'")
        row = pdb_cursor.fetchone()
        if row:
            console.print(f"Verified: [cyan]{row[0]}[/cyan] is encrypted with [cyan]{row[1]}[/cyan]")
        
        pdb_conn.close()

    except Exception as e:
        console.print(f"[red]Error setting up TDE:[/red] {e}")

def main():
    console.print("[bold cyan]Module 07: Transparent Data Encryption (TDE)[/bold cyan]")
    setup_tde()

if __name__ == "__main__":
    main()
