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
        # Check if policy exists in Unified Auditing views
        cursor.execute("SELECT count(*) FROM AUDIT_UNIFIED_POLICIES WHERE policy_name = 'AUDIT_PII_ACCESS'")
        if cursor.fetchone()[0] == 0:
            console.print("[yellow]Creating Audit Policy: AUDIT_PII_ACCESS...[/yellow]")
            cursor.execute("""
                CREATE AUDIT POLICY AUDIT_PII_ACCESS
                ACTIONS SELECT ON CORPORATE_PII.CLIENT_RECORDS,
                        UPDATE ON CORPORATE_PII.CLIENT_RECORDS
            """)
            console.print("[green]Audit policy created.[/green]")
        else:
            console.print("[blue]Audit policy 'AUDIT_PII_ACCESS' already exists.[/blue]")
            
        # Ensure policy is ENABLED
        console.print("[dim]Enabling audit policy...[/dim]")
        try:
            cursor.execute("AUDIT POLICY AUDIT_PII_ACCESS")
        except oracledb.DatabaseError as e:
            if "ORA-46360" in str(e): # Already enabled
                pass
            else: raise e
            
        conn.commit()
        console.print("[green]Audit policy is active and enabled.[/green]")
    except Exception as e:
        console.print(f"[red]Error setting up audit policy:[/red] {e}")
    finally:
        conn.close()

def simulate_access():
    """Simulates access to the sensitive table to generate audit logs."""
    from lab.core.config import PII_PASSWORD
    console.print("[yellow]Simulating access to CORPORATE_PII.CLIENT_RECORDS...[/yellow]")
    try:
        # Connect as CORPORATE_PII to trigger the audit
        conn = get_connection(user="CORPORATE_PII", password=PII_PASSWORD)
        cursor = conn.cursor()
        
        # 1. Select
        cursor.execute("SELECT count(*) FROM CLIENT_RECORDS")
        count = cursor.fetchone()[0]
        console.print(f"[dim]Simulation: SELECT successful ({count} records).[/dim]")
        
        # 2. Update (harmless)
        cursor.execute("UPDATE CLIENT_RECORDS SET CREATED_AT = CREATED_AT WHERE ROWNUM = 1")
        conn.commit()
        console.print("[dim]Simulation: UPDATE successful.[/dim]")
        
        conn.close()
    except Exception as e:
        console.print(f"[red]Simulation failed:[/red] {e}")

def query_audit_trail():
    """Queries the Unified Audit Trail for recent activity."""
    conn = get_connection(mode='sysdba')
    cursor = conn.cursor()
    
    # Force a flush of the audit trail to disk for immediate visibility
    console.print("[dim]Flushing audit trail...[/dim]")
    try:
        cursor.execute("BEGIN DBMS_AUDIT_MGMT.FLUSH_UNIFIED_AUDIT_TRAIL; END;")
    except Exception as e:
        console.print(f"[dim]Note: Flush failed (maybe not in pure Unified mode): {e}[/dim]")
    
    # We filter by our policy name using LIKE to handle multiple policies
    cursor.execute("""
        SELECT event_timestamp, dbusername, action_name, object_schema, object_name 
        FROM UNIFIED_AUDIT_TRAIL 
        WHERE unified_audit_policies LIKE '%AUDIT_PII_ACCESS%'
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
        console.print("Waiting for logs to process...")
        time.sleep(5)
        
        logs = query_audit_trail()
        
        if not logs:
            console.print("[yellow]No audit logs found for AUDIT_PII_ACCESS.[/yellow]")
            console.print("[dim]Checking for ANY recent unified audit logs...[/dim]")
            conn = get_connection(mode='sysdba')
            cursor = conn.cursor()
            cursor.execute("SELECT event_timestamp, dbusername, action_name, unified_audit_policies FROM UNIFIED_AUDIT_TRAIL ORDER BY event_timestamp DESC FETCH FIRST 5 ROWS ONLY")
            recent = cursor.fetchall()
            if recent:
                console.print("[dim]Recent Logs found (but not for our policy):[/dim]")
                for r in recent:
                    console.print(f"[dim]- {r[0]} | {r[1]} | {r[2]} | Policy: {r[3]}[/dim]")
            else:
                console.print("[red]No Unified Audit logs found at all today. Unified Auditing might be in traditional mode.[/red]")
            conn.close()
            return

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
