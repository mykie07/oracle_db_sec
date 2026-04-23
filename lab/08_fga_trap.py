import oracledb
from lab.core.config import get_connection, HR_PASSWORD
from rich.console import Console
from rich.table import Table

console = Console()

def setup_admin_trap():
    """Sets up Fine-Grained Auditing (FGA) to catch admins peeking at data."""
    conn = get_connection(mode='sysdba')
    cursor = conn.cursor()
    
    try:
        console.print("[yellow]Setting up Fine-Grained Auditing (FGA) 'Admin Trap'...[/yellow]")
        
        # 1. Clear existing policy if any
        try:
            cursor.execute("""
                BEGIN
                    DBMS_FGA.DROP_POLICY(
                        object_schema => 'CORPORATE_PII',
                        object_name   => 'CLIENT_RECORDS',
                        policy_name   => 'CATCH_DBA_PEEKING'
                    );
                EXCEPTION WHEN OTHERS THEN NULL;
                END;
            """)
        except: pass

        # 2. Add FGA Policy
        # This policy triggers whenever someone queries the SSN or CREDIT_CARD columns
        # where the user is NOT the owner (CORPORATE_PII)
        cursor.execute("""
            BEGIN
                DBMS_FGA.ADD_POLICY(
                    object_schema   => 'CORPORATE_PII',
                    object_name     => 'CLIENT_RECORDS',
                    policy_name     => 'CATCH_DBA_PEEKING',
                    audit_column    => 'SSN, CREDIT_CARD',
                    audit_condition => 'SYS_CONTEXT(''USERENV'', ''SESSION_USER'') != ''CORPORATE_PII''',
                    statement_types => 'SELECT'
                );
            END;
        """)
        
        conn.commit()
        console.print("[green]FGA Policy 'CATCH_DBA_PEEKING' is now active.[/green]")
        console.print("[dim]This policy monitors any non-owner access to sensitive PII columns.[/dim]")

    except Exception as e:
        console.print(f"[red]Error setting up FGA:[/red] {e}")
    finally:
        conn.close()

def simulate_admin_access():
    """Simulates an IT_ADMIN user peeking at the PII data."""
    console.print("\n[bold red]Scenario: IT_ADMIN (DBA) is peeking at PII data...[/bold red]")
    
    try:
        # Connect as IT_ADMIN
        from lab.core.config import DB_PASSWORD
        conn = get_connection(user="IT_ADMIN", password="Admin2026_Secure!")
        cursor = conn.cursor()
        
        # The admin thinks they are being sneaky
        cursor.execute("SELECT full_name, ssn FROM CORPORATE_PII.CLIENT_RECORDS FETCH FIRST 5 ROWS ONLY")
        results = cursor.fetchall()
        
        console.print("[dim]Admin successfully retrieved data (Redaction might still be active, but FGA caught the attempt).[/dim]")
        conn.close()
    except Exception as e:
        console.print(f"[red]Admin access failed:[/red] {e}")

def check_fga_logs():
    """Checks the FGA audit logs to see if the admin was caught."""
    console.print("\n[bold yellow]Checking FGA Audit Logs (The Trap Result):[/bold yellow]")
    
    conn = get_connection(mode='sysdba')
    cursor = conn.cursor()
    
    try:
        # Force a flush of the audit trail to make it instant for the lab
        cursor.execute("BEGIN DBMS_AUDIT_MGMT.FLUSH_UNIFIED_AUDIT_TRAIL(FLUSH_TYPE => DBMS_AUDIT_MGMT.FLUSH_CURRENT_INSTANCE); END;")
        
        # 1. Check Unified Audit Trail
        cursor.execute("""
            SELECT event_timestamp, dbusername, sql_text 
            FROM UNIFIED_AUDIT_TRAIL 
            WHERE fga_policy_name = 'CATCH_DBA_PEEKING'
            ORDER BY event_timestamp DESC
            FETCH FIRST 5 ROWS ONLY
        """)
        logs = cursor.fetchall()
        
        # 2. Check Legacy FGA Trail (Just in case Mixed Mode is active)
        if not logs:
            cursor.execute("""
                SELECT timestamp, db_user, sql_text 
                FROM DBA_FGA_AUDIT_TRAIL 
                WHERE policy_name = 'CATCH_DBA_PEEKING'
                ORDER BY timestamp DESC
                FETCH FIRST 5 ROWS ONLY
            """)
            logs = cursor.fetchall()

        if not logs:
            console.print("[red]No logs found in Unified or Legacy trails. This can happen if the audit trail is delayed or FGA is restricted.[/red]")
            return

        table = Table(title="FGA Intrusion Detection Logs")
        table.add_column("Timestamp", style="cyan")
        table.add_column("Intruder", style="bold red")
        table.add_column("SQL Statement", style="magenta")
        
        for log in logs:
            table.add_row(str(log[0]), log[1], log[2][:50] + "...")
            
        console.print(table)
        console.print("[bold green]TRAP SPRUNG: Administrative access to sensitive data was detected and logged![/bold green]")
        
    except Exception as e:
        console.print(f"[red]Error checking FGA logs:[/red] {e}")
    finally:
        conn.close()

def main():
    console.print("[bold cyan]Module 08: Fine-Grained Auditing (FGA) - The 'Admin Trap'[/bold cyan]")
    
    try:
        setup_admin_trap()
        simulate_admin_access()
        
        import time
        console.print("[dim]Waiting for audit trail flush (5s)...[/dim]")
        time.sleep(5)
        
        check_fga_logs()
        
        console.print("\n[bold green]Laboratory Training Complete![/bold green]")
        console.print("You have successfully implemented 8 core security modules in Oracle Database 21c.")

    except Exception as e:
        console.print(f"[red]Error in FGA lab:[/red] {e}")

if __name__ == "__main__":
    main()
