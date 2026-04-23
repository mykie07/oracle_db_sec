import oracledb
from lab.core.config import get_connection
from rich.console import Console
from rich.table import Table

console = Console()

def get_db_info():
    """Retrieves basic DB version and identification info."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Version info
    cursor.execute("SELECT banner FROM v$version")
    version = cursor.fetchone()[0]
    
    # Instance Name
    cursor.execute("SELECT instance_name, host_name, status FROM v$instance")
    inst = cursor.fetchone()
    
    conn.close()
    return version, inst

def check_security_options():
    """Checks for installed security options (Vault, Label Security, etc.)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT parameter, value FROM v$option WHERE parameter IN ('Oracle Database Vault', 'Oracle Label Security', 'Unified Auditing')")
    options = cursor.fetchall()
    
    conn.close()
    return options

def main():
    console.print("[bold cyan]Module 01: Reconnaissance[/bold cyan]")
    
    try:
        version, inst = get_db_info()
        console.print(f"\n[bold]Database Banner:[/bold] {version}")
        
        table = Table(title="Instance Status")
        table.add_column("Instance", style="magenta")
        table.add_column("Host", style="green")
        table.add_column("Status", style="yellow")
        table.add_row(inst[0], inst[1], inst[2])
        console.print(table)
        
        options = check_security_options()
        opt_table = Table(title="Security Options")
        opt_table.add_column("Feature", style="cyan")
        opt_table.add_column("Installed/Enabled", style="white")
        for opt in options:
            color = "green" if opt[1] == 'TRUE' else "red"
            opt_table.add_row(opt[0], f"[{color}]{opt[1]}[/{color}]")
        console.print(opt_table)

    except Exception as e:
        console.print(f"[red]Error during recon:[/red] {e}")

if __name__ == "__main__":
    main()
