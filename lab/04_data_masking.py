import oracledb
from lab.core.config import get_connection
from rich.console import Console
from rich.table import Table

console = Console()

def setup_redaction_policy():
    """Applies a Data Redaction policy to sensitive columns."""
    conn = get_connection(mode='sysdba')
    cursor = conn.cursor()
    
    try:
        # Verify table existence first
        cursor.execute("SELECT count(*) FROM all_tables WHERE owner = 'CORPORATE_PII' AND table_name = 'CLIENT_RECORDS'")
        if cursor.fetchone()[0] == 0:
            console.print("[red]Error: CORPORATE_PII.CLIENT_RECORDS table not found! Run setup_db.py first.[/red]")
            return

        # Check if policy exists - using the standard view
        cursor.execute("SELECT count(*) FROM REDACTION_POLICIES WHERE policy_name = 'MASK_SENSITIVE_PII'")
        if cursor.fetchone()[0] == 0:
            console.print("[yellow]Creating Redaction Policy: MASK_SENSITIVE_PII...[/yellow]")
            # Redact SSN (Full Masking) and Credit Card (Partial Masking)
            cursor.execute("""
                BEGIN
                    DBMS_REDACT.ADD_POLICY(
                        object_schema => 'CORPORATE_PII',
                        object_name   => 'CLIENT_RECORDS',
                        column_name   => 'SSN',
                        policy_name   => 'MASK_SENSITIVE_PII',
                        function_type => DBMS_REDACT.FULL,
                        expression    => '1=1'
                    );
                    
                    DBMS_REDACT.ALTER_POLICY(
                        object_schema => 'CORPORATE_PII',
                        object_name   => 'CLIENT_RECORDS',
                        column_name   => 'CREDIT_CARD',
                        policy_name   => 'MASK_SENSITIVE_PII',
                        function_type => DBMS_REDACT.PARTIAL,
                        function_parameters => 'VVVVVVVVVVVVVVVV,VVVVVVVVVVVVVVVV,*,1,12',
                        expression    => '1=1'
                    );
                END;
            """)
            conn.commit()
            console.print("[green]Redaction policy active.[/green]")
        else:
            console.print("[blue]Redaction policy already exists.[/blue]")
    except Exception as e:
        console.print(f"[red]Error setting up redaction:[/red] {e}")
    finally:
        conn.close()

def verify_redaction():
    """Queries the table to see redaction in action."""
    from lab.core.config import PII_PASSWORD
    console.print("\n[bold]Verifying Data Redaction as CORPORATE_PII user...[/bold]")
    conn = get_connection(user="CORPORATE_PII", password=PII_PASSWORD)
    cursor = conn.cursor()
    
    cursor.execute("SELECT full_name, ssn, credit_card FROM CLIENT_RECORDS FETCH FIRST 5 ROWS ONLY")
    results = cursor.fetchall()
    
    table = Table(title="Redacted Data View")
    table.add_column("Name", style="magenta")
    table.add_column("SSN (Redacted)", style="red")
    table.add_column("Credit Card (Partial)", style="yellow")
    
    for row in results:
        table.add_row(row[0], str(row[1]), row[2])
    
    console.print(table)
    conn.close()

def main():
    console.print("[bold cyan]Module 04: Data Redaction[/bold cyan]")
    
    try:
        setup_redaction_policy()
        verify_redaction()
    except Exception as e:
        if "ORA-28365" in str(e):
            console.print("[yellow]Note: This table appears to be encrypted (TDE).[/yellow]")
            console.print("[yellow]In the Manual Lab, you must either complete Module 07 first or open the wallet manually.[/yellow]")
        console.print(f"[red]Error in Redaction lab:[/red] {e}")

if __name__ == "__main__":
    main()
