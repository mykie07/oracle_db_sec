import oracledb
import sys
import time
from faker import Faker
from lab.core.config import get_connection, HR_PASSWORD, PII_PASSWORD
from rich.console import Console

console = Console()
fake = Faker()

def setup_hr_schema(conn):
    """Creates a more realistic HR schema for the lab."""
    console.print("[yellow]Setting up HR schema (2,000 records)...[/yellow]")
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"CREATE USER HR IDENTIFIED BY \"{HR_PASSWORD}\" DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS")
        cursor.execute("GRANT CREATE SESSION, CREATE TABLE TO HR")
        
        # Create Tables
        cursor.execute("""
            CREATE TABLE HR.DEPARTMENTS (
                dept_id NUMBER PRIMARY KEY,
                dept_name VARCHAR2(100),
                location VARCHAR2(100)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE HR.EMPLOYEES (
                employee_id NUMBER PRIMARY KEY,
                first_name VARCHAR2(50),
                last_name VARCHAR2(50),
                email VARCHAR2(100),
                salary NUMBER(10,2),
                dept_id NUMBER REFERENCES HR.DEPARTMENTS(dept_id)
            )
        """)

        # 1. Insert Departments
        depts = [(10, 'Finance', 'London'), (20, 'IT', 'San Francisco'), (30, 'HR', 'New York'), (40, 'Sales', 'Singapore')]
        cursor.executemany("INSERT INTO HR.DEPARTMENTS VALUES (:1, :2, :3)", depts)

        # 2. Insert 2000 Employees
        employees = []
        for i in range(1, 2001):
            dept = (i % 4 + 1) * 10
            employees.append((i, fake.first_name(), fake.last_name(), fake.email(), fake.random_int(40000, 150000), dept))
        
        cursor.executemany("INSERT INTO HR.EMPLOYEES VALUES (:1, :2, :3, :4, :5, :6)", employees)
        
        conn.commit()
        console.print("[green]HR schema populated with realistic volume.[/green]")
    except oracledb.DatabaseError as e:
        console.print(f"[red]Error setting up HR:[/red] {e}")

def setup_corporate_pii(conn):
    """Creates the sensitive CORPORATE_PII schema with 5,000 clients."""
    console.print("[yellow]Setting up CORPORATE_PII schema (5,000 records)...[/yellow]")
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"CREATE USER CORPORATE_PII IDENTIFIED BY \"{PII_PASSWORD}\" DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS")
        cursor.execute("GRANT CREATE SESSION, CREATE TABLE TO CORPORATE_PII")
        
        cursor.execute("""
            CREATE TABLE CORPORATE_PII.CLIENT_RECORDS (
                client_id NUMBER PRIMARY KEY,
                full_name VARCHAR2(100),
                ssn VARCHAR2(11),
                credit_card VARCHAR2(19),
                email VARCHAR2(100),
                secret_note VARCHAR2(255),
                risk_score NUMBER
            )
        """)
        
        # Generate 5,000 synthetic records
        data = []
        for i in range(1, 5001):
            data.append((
                i, 
                fake.name(), 
                fake.ssn(), 
                fake.credit_card_number(), 
                fake.email(),
                "Internal Note: " + fake.word(),
                fake.random_int(1, 100)
            ))
            
        cursor.executemany("INSERT INTO CORPORATE_PII.CLIENT_RECORDS VALUES (:1, :2, :3, :4, :5, :6, :7)", data)
        conn.commit()
        console.print("[green]CORPORATE_PII schema ready with high-density PII.[/green]")
    except oracledb.DatabaseError as e:
        console.print(f"[red]Error setting up CORPORATE_PII:[/red] {e}")

def inject_security_smells(conn):
    """Creates nuanced 'vulnerable' configurations for auditing exercises."""
    console.print("[yellow]Injecting realistic security smells...[/yellow]")
    cursor = conn.cursor()
    
    try:
        # 1. User with default password
        cursor.execute("CREATE USER WEAK_USER IDENTIFIED BY weak_user")
        cursor.execute("GRANT CREATE SESSION TO WEAK_USER")
        
        # 2. Over-privileged user (DBA)
        cursor.execute("CREATE USER IT_ADMIN IDENTIFIED BY \"Admin2026_Secure!\"")
        cursor.execute("GRANT CREATE SESSION, DBA TO IT_ADMIN")
        
        # 3. The "Shadow DBA" (Not DBA role, but dangerous ANY privs)
        cursor.execute("CREATE USER APP_SUPPORT IDENTIFIED BY \"Support99!\"")
        cursor.execute("GRANT CREATE SESSION, CREATE ANY TABLE, DROP ANY TABLE, SELECT ANY TABLE TO APP_SUPPORT")
        
        # 4. Public grant on sensitive data (simulated)
        cursor.execute("GRANT SELECT ON HR.EMPLOYEES TO PUBLIC")
        
        # 5. User with no password limits (using default profile)
        cursor.execute("CREATE USER LEGACY_SYS IDENTIFIED BY Legacy_Pass_1")
        cursor.execute("GRANT CREATE SESSION TO LEGACY_SYS")
        
        conn.commit()
        console.print("[green]Security smells injected. The DB is now a 'Target Environment'.[/green]")
    except oracledb.DatabaseError as e:
        console.print(f"[red]Error injecting smells:[/red] {e}")

def main():
    console.print("[bold blue]Starting Database Initialization...[/bold blue]")
    
    max_retries = 5
    retry_delay = 10
    
    for i in range(max_retries):
        try:
            conn = get_connection(mode='sysdba')
            console.print("[green]Connected to Oracle SYSDBA.[/green]")
            
            # Run setup
            setup_hr_schema(conn)
            setup_corporate_pii(conn)
            inject_security_smells(conn)
            
            conn.close()
            console.print("[bold green]Initialization Complete![/bold green]")
            break
        except Exception as e:
            console.print(f"[yellow]Waiting for DB to be ready... ({i+1}/{max_retries}) - Error: {e}[/yellow]")
            time.sleep(retry_delay)

if __name__ == "__main__":
    main()
