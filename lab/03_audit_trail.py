import oracledb
import time
from lab.core.config import get_connection
from rich.console import Console
from rich.table import Table

console = Console()

def setup_audit_policy():
    """Creates a Unified Audit policy for sensitive data access."""
    conn = get_connection(mode='sysdba')
    cursor = conn.cursor()
    
    try:
        # Check if policy exists
        cursor.execute("SELECT count(*) FROM dba_audit_policies WHERE policy_name = 'AUDIT_PII_ACCESS'")
        if cursor.fetchone()[0] == 0:
            console.print("[yellow]Creating Audit Policy: AUDIT_PII_ACCESS...[/yellow]")
            cursor.execute("""
                CREATE AUDIT POLICY AUDIT_PII_ACCESS
                ACTIONS SELECT ON CORPORATE_PII.CLIENT_RECORDS,
                        UPDATE ON CORPORATE_PII.CLIENT_RECORDS
            """)
            cursor.execute("AUDIT POLICY AUDIT_PII_ACCESS")
            conn.commit()
            console.print("[green]Audit policy active.[/green]")
        else:
            console.print("[blue]Audit policy 'AUDIT_PII_ACCESS' already exists.[/blue]")
    except Exception as e:
        console.print(f"[red]Error setting up audit policy:[/red] {e}")
    finally:
        conn.close()

def simulate_access():
    """Simulates access to the sensitive table to generate audit logs."""
    from lab.core.config import PII_PASSWORD
    console.print("[yellow]Simulating access to CORPORATE_PII.CLIENT_RECORDS...[/yellow]")
    conn = get_connection(user="CORPORATE_PII", password=PII_PASSWORD)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM CLIENT_RECORDS")
    cursor.fetchone()
    conn.close()

def query_audit_trail():
    """Queries the Unified Audit Trail for recent activity."""
    conn = get_connection(mode='sysdba')
    cursor = conn.cursor()
    
    # We filter by our policy name
    cursor.execute("""
        SELECT event_timestamp, dbusername, action_name, object_schema, object_name 
        FROM UNIFIED_AUDIT_TRAIL 
        WHERE unified_audit_policies = 'AUDIT_PII_ACCESS'
        ORDER BY event_timestamp DESC
    """)
    results = cursor.fetchmany(10)
    conn.close()
    return results

def main():
    console.print("[bold cyan]Module 03: Unified Auditing[/bold cyan]")
    
    try:
        setup_audit_policy()
        simulate_access()
        
        # Give DB a second to flush audit logs
        console.print("Waiting for audit trail flush...")
        time.sleep(2)
        
        logs = query_audit_trail()
        table = Table(title="Recent Audit Logs (PII Access)")
        table.add_column("Timestamp", style="dim")
        table.add_column("User", style="magenta")
        table.add_column("Action", style="green")
        table.add_column("Schema", style="cyan")
        table.add_column("Object", style="white")
        
        for log in logs:
            table.add_row(str(log[0]), log[1], log[2], log[3], log[4])
        console.print(table)

    except Exception as e:
        console.print(f"[red]Error in Audit lab:[/red] {e}")

if __name__ == "__main__":
    main()
