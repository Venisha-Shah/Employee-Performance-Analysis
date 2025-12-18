import sqlite3

# ======= DATABASE SETUP =======
# Connect to SQLite database (it will create file 'employee.db')
conn = sqlite3.connect('employee.db')
cursor = conn.cursor()

# Create Employees table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    position TEXT NOT NULL,
    joining_date TEXT NOT NULL
)
''')

# Create Performance table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    tasks_completed INTEGER NOT NULL,
    targets_achieved INTEGER NOT NULL,
    rating REAL NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id)
)
''')

conn.commit()

# ======= FUNCTIONS =======

# Function to add a new employee
def add_employee():
    name = input("Enter Employee Name: ")
    department = input("Enter Department: ")
    position = input("Enter Position: ")
    joining_date = input("Enter Joining Date (YYYY-MM-DD): ")
    cursor.execute("INSERT INTO Employees (name, department, position, joining_date) VALUES (?, ?, ?, ?)",
                   (name, department, position, joining_date))
    conn.commit()
    print("Employee Added Successfully!\n")

# Function to record employee performance
def record_performance():
    view_employees()
    try:
        emp_id = int(input("Enter Employee ID: "))
        cursor.execute("SELECT * FROM Employees WHERE employee_id=?", (emp_id,))
        emp = cursor.fetchone()
        if not emp:
            print("Employee ID not found!\n")
            return
    except:
        print("Invalid input.\n")
        return

    month = input("Enter Month (YYYY-MM): ")
    while True:
        try:
            tasks = int(input("Enter Tasks Completed: "))
            if tasks < 0:
                print("Tasks cannot be negative.")
            else:
                break
        except:
            print("Invalid input. Enter a number.")
    while True:
        try:
            targets = int(input("Enter Targets Achieved: "))
            if targets < 0:
                print("Targets cannot be negative.")
            else:
                break
        except:
            print("Invalid input. Enter a number.")
    while True:
        try:
            rating = float(input("Enter Rating (1-5): "))
            if 1 <= rating <= 5:
                break
            else:
                print("Rating must be between 1 and 5.")
        except:
            print("Invalid input. Enter a number.")
    cursor.execute("INSERT INTO Performance (employee_id, month, tasks_completed, targets_achieved, rating) VALUES (?, ?, ?, ?, ?)",
                   (emp_id, month, tasks, targets, rating))
    conn.commit()
    print("Performance Recorded Successfully!\n")

# Function to view all employees
def view_employees():
    cursor.execute("SELECT * FROM Employees")
    employees = cursor.fetchall()
    if not employees:
        print("No employees found.\n")
        return
    print("ID  Name          Department  Position  Joining Date")
    for e in employees:
        print(f"{e[0]}   {e[1]}  {e[2]}  {e[3]}  {e[4]}")
    print()

# Function to view employee performance
def view_performance():
    view_employees()
    if not cursor.execute("SELECT * FROM Employees").fetchall():
        return
    try:
        emp_id = int(input("Enter Employee ID to view performance: "))
        cursor.execute("SELECT * FROM Employees WHERE employee_id=?", (emp_id,))
        if not cursor.fetchone():
            print("Employee ID not found!\n")
            return
    except:
        print("Invalid input.\n")
        return
    cursor.execute("SELECT month, tasks_completed, targets_achieved, rating FROM Performance WHERE employee_id=?", (emp_id,))
    performances = cursor.fetchall()
    if not performances:
        print("No performance records found.\n")
        return
    print("Month      Tasks Completed  Targets Achieved  Rating")
    for p in performances:
        print(f"{p[0]}       {p[1]}               {p[2]}               {p[3]}")
    print()

# Function for performance analysis
def performance_analysis():
    cursor.execute('''
    SELECT Employees.name, AVG(Performance.rating) as avg_rating, SUM(Performance.tasks_completed) as total_tasks
    FROM Employees
    LEFT JOIN Performance ON Employees.employee_id = Performance.employee_id
    GROUP BY Employees.employee_id
    ORDER BY avg_rating DESC
    ''')
    results = cursor.fetchall()
    if not results:
        print("No data available for analysis.\n")
        return
    print("Name        Average Rating   Total Tasks Completed")
    for r in results:
        avg_rating = round(r[1], 2) if r[1] else 0
        total_tasks = r[2] if r[2] else 0
        print(f"{r[0]}         {avg_rating}             {total_tasks}")
    if results:
        top_performer = results[0][0]
        print(f"Top Performer: {top_performer}\n")

# Function to search performance by month
def search_performance_by_month():
    month = input("Enter Month to Search (YYYY-MM): ")
    cursor.execute('''
    SELECT Employees.name, Performance.tasks_completed, Performance.targets_achieved, Performance.rating
    FROM Performance
    JOIN Employees ON Performance.employee_id = Employees.employee_id
    WHERE Performance.month=?
    ''', (month,))
    records = cursor.fetchall()
    if not records:
        print("No performance records found for this month.\n")
        return
    print("Name        Tasks Completed   Targets Achieved   Rating")
    for r in records:
        print(f"{r[0]}          {r[1]}               {r[2]}               {r[3]}")
    print()

# Function to update employee details
def update_employee():
    view_employees()
    if not cursor.execute("SELECT * FROM Employees").fetchall():
        return
    try:
        emp_id = int(input("Enter Employee ID to update: "))
        cursor.execute("SELECT * FROM Employees WHERE employee_id=?", (emp_id,))
        emp = cursor.fetchone()
        if not emp:
            print("Employee ID not found!\n")
            return
    except:
        print("Invalid input.\n")
        return
    print("Leave blank to keep current value.")
    name = input(f"Enter Name ({emp[1]}): ")
    dept = input(f"Enter Department ({emp[2]}): ")
    pos = input(f"Enter Position ({emp[3]}): ")
    join = input(f"Enter Joining Date ({emp[4]}): ")
    cursor.execute('''
    UPDATE Employees
    SET name=?, department=?, position=?, joining_date=?
    WHERE employee_id=?
    ''', (name if name else emp[1],
          dept if dept else emp[2],
          pos if pos else emp[3],
          join if join else emp[4],
          emp_id))
    conn.commit()
    print("Employee Updated Successfully!\n")

# Function to delete employee or performance record
def delete_employee_or_performance():
    print("1. Delete Employee")
    print("2. Delete Performance Record")
    choice = input("Enter choice: ")
    if choice == "1":
        view_employees()
        try:
            emp_id = int(input("Enter Employee ID to" \
            " delete: "))
            cursor.execute("DELETE FROM Employees WHERE employee_id=?", (emp_id,))
            cursor.execute("DELETE FROM Performance WHERE employee_id=?", (emp_id,))
            conn.commit()
            print("Employee and related performance records deleted.\n")
        except:
            print("Invalid input.\n")
    elif choice == "2":
        cursor.execute("SELECT * FROM Performance")
        performances = cursor.fetchall()
        if not performances:
            print("No performance records found.\n")
            return
        print("ID  Employee ID  Month  Tasks  Targets  Rating")
        for p in performances:
            print(f"{p[0]}      {p[1]}           {p[2]}     {p[3]}       {p[4]}      {p[5]}")
        try:
            perf_id = int(input("Enter Performance ID to delete: "))
            cursor.execute("DELETE FROM Performance WHERE performance_id=?", (perf_id,))
            conn.commit()
            print("Performance record deleted.\n")
        except:
            print("Invalid input.\n")
    else:
        print("Invalid choice.\n")

# ======= MAIN MENU =======
def main_menu():
    while True:
        print("===== Employee Performance Analysis =====")
        print("1. Add Employee")
        print("2. Record Employee Performance")
        print("3. View All Employees")
        print("4. View Employee Performance")
        print("5. Performance Analysis")
        print("6. Search Performance by Month")
        print("7. Update Employee Details")
        print("8. Delete Employee or Performance Record")
        print("9. Exit")
        choice = input("Enter your choice (1-9): ")
        print()

        if choice == "1":
            add_employee()
        elif choice == "2":
            record_performance()
        elif choice == "3":
            view_employees()
        elif choice == "4":
            view_performance()
        elif choice == "5":
            performance_analysis()
        elif choice == "6":
            search_performance_by_month()
        elif choice == "7":
            update_employee()
        elif choice == "8":
            delete_employee_or_performance()
        elif choice == "9":
            print("Exiting Program. Goodbye!")
            break
        else:
            print("Invalid Choice! Try again.\n")

# Run the program
main_menu()

# Close database connection
conn.close()