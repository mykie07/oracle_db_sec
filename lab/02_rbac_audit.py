import oracledb
from lab.core.config import get_connection
from rich.console import Console
from rich.table import Table

console = Console()

def audit_dba_users():
    """Finds all users who have been granted the DBA role."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT grantee, admin_option, delegate_option 
        FROM dba_role_privs 
        WHERE granted_role = 'DBA' 
        ORDER BY grantee
    """)
    results = cursor.fetchall()
    conn.close()
    return results

def audit_any_privileges():
    """Finds users with dangerous 'ANY' privileges (e.g., CREATE ANY TABLE)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT grantee, privilege, admin_option 
        FROM dba_sys_privs 
        WHERE privilege LIKE '% ANY %'
        AND grantee NOT IN ('SYS', 'SYSTEM', 'DBA')
        ORDER BY grantee
    """)
    results = cursor.fetchall()
    conn.close()
    return results

def audit_public_grants():
    """Finds object privileges granted to PUBLIC."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT owner, table_name, privilege 
        FROM dba_tab_privs 
        WHERE grantee = 'PUBLIC' 
        AND owner NOT IN ('SYS', 'SYSTEM', 'XDB', 'MDSYS')
    """)
    results = cursor.fetchall()
    conn.close()
    return results

def main():
    console.print("[bold cyan]Module 02: RBAC Audit (Identity & Access Management)[/bold cyan]")
    
    try:
        # DBA Users
        dba_users = audit_dba_users()
        table = Table(title="Users with DBA Role")
        table.add_column("Grantee", style="magenta")
        table.add_column("Admin Opt", style="yellow")
        for user in dba_users:
            table.add_row(user[0], user[1])
        console.print(table)
        
        # Dangerous Privs
        any_privs = audit_any_privileges()
        priv_table = Table(title="Dangerous 'ANY' Privileges")
        priv_table.add_column("Grantee", style="magenta")
        priv_table.add_column("Privilege", style="red")
        for p in any_privs:
            priv_table.add_row(p[0], p[1])
        console.print(priv_table)
        
        # Public Grants
        pub_grants = audit_public_grants()
        pub_table = Table(title="Sensitive Public Grants")
        pub_table.add_column("Owner", style="cyan")
        pub_table.add_column("Table", style="green")
        pub_table.add_column("Privilege", style="white")
        for g in pub_grants:
            pub_table.add_row(g[0], g[1], g[2])
        console.print(pub_table)

    except Exception as e:
        console.print(f"[red]Error during RBAC audit:[/red] {e}")

if __name__ == "__main__":
    main()
