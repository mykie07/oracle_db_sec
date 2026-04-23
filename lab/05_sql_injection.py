import oracledb
from lab.core.config import get_connection
from rich.console import Console

console = Console()

def vulnerable_search(name_query):
    """VULNERABLE: Uses string concatenation."""
    conn = get_connection(user="IT_ADMIN", password="Admin2026_Secure!")
    cursor = conn.cursor()
    
    # DO NOT DO THIS IN PRODUCTION
    sql = f"SELECT first_name, last_name, salary FROM HR.EMPLOYEES WHERE first_name = '{name_query}'"
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
    conn = get_connection(user="IT_ADMIN", password="Admin2026_Secure!")
    cursor = conn.cursor()
    
    # THIS IS THE SECURE WAY
    sql = "SELECT first_name, last_name, salary FROM HR.EMPLOYEES WHERE first_name = :name"
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
    conn = get_connection(user="IT_ADMIN", password="Admin2026_Secure!")
    cursor = conn.cursor()
    cursor.execute("SELECT first_name FROM HR.EMPLOYEES FETCH FIRST 1 ROWS ONLY")
    row = cursor.fetchone()
    
    if row:
        real_name = row[0]
    else:
        console.print("[yellow]Warning: No employees found in HR.EMPLOYEES. Using fallback 'Alice'.[/yellow]")
        real_name = "Alice"
        
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
