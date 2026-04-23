import oracledb
from lab.core.config import get_connection
from rich.console import Console

console = Console()

def setup_tde():
    """Sets up TDE keystore and encrypts columns."""
    from lab.core.config import DB_USER, DB_PASSWORD
    
    # Need to connect to CDB Root for keystore management
    cdb_dsn = "oracle-db:1521/XE"
    pdb_dsn = "oracle-db:1521/XEPDB1"
    
    try:
        console.print("[yellow]Setting up Transparent Data Encryption (TDE)...[/yellow]")
        
        # 1. Open/Create Keystore in CDB Root
        console.print("[dim]Connecting to CDB Root for Keystore Management...[/dim]")
        cdb_conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=cdb_dsn, mode=oracledb.AUTH_MODE_SYSDBA)
        cdb_cursor = cdb_conn.cursor()
        
        console.print("[dim]Creating/Opening keystore in CDB...[/dim]")
        try:
            cdb_cursor.execute("""
                ADMINISTER KEY MANAGEMENT CREATE KEYSTORE '/opt/oracle/oradata/dbconfig/XE/wallet' 
                IDENTIFIED BY "LabPassword2026!"
            """)
        except oracledb.DatabaseError as e:
            if "ORA-28328" in str(e) or "ORA-46630" in str(e):
                console.print("[blue]Keystore already exists or location is initialized.[/blue]")
            else:
                raise e
                
        try:
            cdb_cursor.execute("""
                ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN 
                IDENTIFIED BY "LabPassword2026!"
            """)
        except oracledb.DatabaseError as e:
            if "ORA-28322" in str(e) or "ORA-28354" in str(e): # Already open
                console.print("[blue]Keystore already open.[/blue]")
            else:
                raise e
        
        cdb_cursor.execute("""
            ADMINISTER KEY MANAGEMENT SET KEY 
            IDENTIFIED BY "LabPassword2026!" 
            WITH BACKUP
        """)
        cdb_conn.close()

        # 2. Open Keystore in PDB
        console.print("[dim]Opening keystore in PDB (XEPDB1)...[/dim]")
        pdb_conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=pdb_dsn, mode=oracledb.AUTH_MODE_SYSDBA)
        pdb_cursor = pdb_conn.cursor()
        
        try:
            pdb_cursor.execute("""
                ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN 
                IDENTIFIED BY "LabPassword2026!"
            """)
        except oracledb.DatabaseError as e:
            if "ORA-28322" in str(e) or "ORA-28354" in str(e):
                console.print("[blue]Keystore already open in PDB.[/blue]")
            else:
                raise e
        
        console.print("[dim]Setting master encryption key in PDB...[/dim]")
        try:
            pdb_cursor.execute("""
                ADMINISTER KEY MANAGEMENT SET KEY 
                IDENTIFIED BY "LabPassword2026!" 
                WITH BACKUP
            """)
        except oracledb.DatabaseError as e:
            if "ORA-28339" in str(e): # Already has a master key
                console.print("[blue]Master key already set in PDB.[/blue]")
            else:
                raise e
        
        # 3. Encrypt the SSN column in CORPORATE_PII.CLIENT_RECORDS
        console.print("[yellow]Encrypting CORPORATE_PII.CLIENT_RECORDS(SSN) column...[/yellow]")
        try:
            pdb_cursor.execute("ALTER TABLE CORPORATE_PII.CLIENT_RECORDS MODIFY (SSN ENCRYPT)")
        except oracledb.DatabaseError as e:
            if "ORA-28424" in str(e) or "ORA-28334" in str(e): # Already encrypted
                console.print("[blue]Column already encrypted.[/blue]")
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
