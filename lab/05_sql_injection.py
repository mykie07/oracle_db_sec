import oracledb
from lab.core.config import get_connection
from rich.console import Console

console = Console()

def vulnerable_search(name_query):
    """VULNERABLE: Uses string concatenation."""
    from lab.core.config import HR_PASSWORD
    conn = get_connection(user="HR", password=HR_PASSWORD)
    cursor = conn.cursor()
    
    # DO NOT DO THIS IN PRODUCTION
    sql = f"SELECT first_name, last_name, salary FROM EMPLOYEES WHERE first_name = '{name_query}'"
    console.print(f"[dim]Executing Vulnerable SQL: {sql}[/dim]")
    
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()

def secure_search(name_query):
    """SECURE: Uses bind variables."""
    from lab.core.config import HR_PASSWORD
    conn = get_connection(user="HR", password=HR_PASSWORD)
    cursor = conn.cursor()
    
    # THIS IS THE SECURE WAY
    sql = "SELECT first_name, last_name, salary FROM EMPLOYEES WHERE first_name = :name"
    console.print(f"[dim]Executing Secure SQL: {sql} with bind :name='{name_query}'[/dim]")
    
    try:
        cursor.execute(sql, name=name_query)
        results = cursor.fetchall()
        return results
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()

def main():
    console.print("[bold cyan]Module 05: SQL Injection & Secure Coding[/bold cyan]")
    
    # Get a valid name for demonstration
    from lab.core.config import HR_PASSWORD
    conn = get_connection(user="HR", password=HR_PASSWORD)
    cursor = conn.cursor()
    cursor.execute("SELECT first_name FROM EMPLOYEES FETCH FIRST 1 ROWS ONLY")
    real_name = cursor.fetchone()[0]
    conn.close()

    console.print(f"\n[bold]1. Standard Search ({real_name}):[/bold]")
    print(secure_search(real_name))
    
    console.print("\n[bold red]2. Attempting SQL Injection on Vulnerable Function:[/]")
    attack_query = "Alice' OR '1'='1"
    console.print(f"Attack Payload: [magenta]{attack_query}[/magenta]")
    results = vulnerable_search(attack_query)
    console.print(f"Result count (Expected 1, got all): [bold red]{len(results)}[/bold red]")
    
    console.print("\n[bold green]3. Attempting SQL Injection on Secure Function:[/]")
    results = secure_search(attack_query)
    console.print(f"Result count (Correctly got 0): [bold green]{len(results)}[/bold green]")

if __name__ == "__main__":
    main()
