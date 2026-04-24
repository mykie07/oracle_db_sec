import oracledb
from lab.core.config import get_connection, HR_PASSWORD
from rich.console import Console
from rich.table import Table

console = Console()

def setup_vpd_policy():
    """Implements Virtual Private Database (VPD) for row-level security."""
    conn = get_connection(mode='sysdba')
    cursor = conn.cursor()
    
    try:
        console.print("[yellow]Setting up VPD Policy...[/yellow]")
        
        # 1. Create a context to store session-specific attributes
        cursor.execute("CREATE OR REPLACE CONTEXT LAB_CTX USING HR.LAB_CTX_PKG")
        
        # 2. Create a package to manage the context
        cursor.execute("""
            CREATE OR REPLACE PACKAGE HR.LAB_CTX_PKG AS
                PROCEDURE SET_DEPT(p_dept_id NUMBER);
            END;
        """)
        
        cursor.execute("""
            CREATE OR REPLACE PACKAGE BODY HR.LAB_CTX_PKG AS
                PROCEDURE SET_DEPT(p_dept_id NUMBER) IS
                BEGIN
                    DBMS_SESSION.SET_CONTEXT('LAB_CTX', 'DEPT_ID', p_dept_id);
                END;
            END;
        """)
        
        # 3. Create the policy function
        cursor.execute("""
            CREATE OR REPLACE FUNCTION HR.GET_DEPT_PREDICATE(
                p_schema IN VARCHAR2,
                p_object IN VARCHAR2
            ) RETURN VARCHAR2 AS
            BEGIN
                -- If it's SYS or IT_ADMIN, they see everything
                IF (SYS_CONTEXT('USERENV', 'SESSION_USER') IN ('SYS', 'SYSTEM', 'IT_ADMIN')) THEN
                    RETURN '1=1';
                END IF;
                
                -- Otherwise, filter by the DEPT_ID stored in our custom context
                RETURN 'DEPT_ID = SYS_CONTEXT(''LAB_CTX'', ''DEPT_ID'')';
            END;
        """)
        
        # 4. Apply the policy to the HR.EMPLOYEES table
        # We use DBMS_RLS.ADD_POLICY
        try:
            cursor.execute("""
                BEGIN
                    DBMS_RLS.DROP_POLICY('HR', 'EMPLOYEES', 'DEPT_ACCESS_POLICY');
                EXCEPTION WHEN OTHERS THEN NULL;
                END;
            """)
            cursor.execute("""
                BEGIN
                    DBMS_RLS.ADD_POLICY(
                        object_schema   => 'HR',
                        object_name     => 'EMPLOYEES',
                        policy_name     => 'DEPT_ACCESS_POLICY',
                        function_schema => 'HR',
                        policy_function => 'GET_DEPT_PREDICATE',
                        statement_types => 'SELECT'
                    );
                END;
            """)
        except oracledb.DatabaseError as e:
            # If it already exists, that's fine
            pass

        conn.commit()
        console.print("[green]VPD Policy 'DEPT_ACCESS_POLICY' is now active on HR.EMPLOYEES.[/green]")
        
    except Exception as e:
        console.print(f"[red]Error setting up VPD:[/red] {e}")
    finally:
        conn.close()

def simulate_user_session(dept_id, user_description):
    """Simulates a session for a user in a specific department."""
    console.print(f"\n[bold blue]Simulating Session: {user_description} (Authorized for Dept {dept_id})[/bold blue]")
    
    # We'll use the HR user but set the context
    conn = get_connection(user="HR", password=HR_PASSWORD)
    cursor = conn.cursor()
    
    # Set the context using our package
    cursor.execute(f"BEGIN HR.LAB_CTX_PKG.SET_DEPT({dept_id}); END;")
    
    # Now query the table - the VPD policy should automatically filter results
    cursor.execute("SELECT count(*) FROM HR.EMPLOYEES")
    count = cursor.fetchone()[0]
    
    # Sample data
    cursor.execute("SELECT first_name, last_name, dept_id FROM HR.EMPLOYEES FETCH FIRST 5 ROWS ONLY")
    rows = cursor.fetchall()
    
    table = Table(title=f"Visible Records for Dept {dept_id}")
    table.add_column("First Name", style="magenta")
    table.add_column("Last Name", style="magenta")
    table.add_column("Dept ID", style="cyan")
    
    for row in rows:
        table.add_row(row[0], row[1], str(row[2]))
        
    console.print(table)
    console.print(f"Total Rows Visible: [bold green]{count}[/bold green] (Out of 2,000 total)")
    
    conn.close()

def main():
    console.print("[bold cyan]Module 06: Virtual Private Database (VPD)[/bold cyan]")
    
    try:
        setup_vpd_policy()
        
        # Scenario 1: Manager in Dept 1
        simulate_user_session(1, "Sales Manager")
        
        # Scenario 2: Manager in Dept 3
        simulate_user_session(3, "Engineering Lead")
        
        # Scenario 3: Admin (Bypassing VPD)
        console.print("\n[bold red]Simulating Session: IT_ADMIN (Bypassing VPD)[/bold red]")
        from lab.core.config import DB_PASSWORD
        conn = get_connection(user="IT_ADMIN", password="Admin2026_Secure!")
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM HR.EMPLOYEES")
        count = cursor.fetchone()[0]
        console.print(f"Total Rows Visible to Admin: [bold green]{count}[/bold green] (Full Access)")
        conn.close()

    except Exception as e:
        console.print(f"[red]Error in VPD lab:[/red] {e}")

if __name__ == "__main__":
    main()
