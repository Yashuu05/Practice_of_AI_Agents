import sqlite3

# 1. Connect to the database (creates 'my_database.db' if it doesn't exist)
conn = sqlite3.connect("Superstore.db")

# 2. Create a cursor object to execute SQL commands
cursor = conn.cursor()

try: 
    # 3. Create a table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Records(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Segment VARCHAR(50) NOT NULL,
            City VARCHAR(30) NOT NULL,
            State VARCHAR(30) NOT NULL,
            Region VARCHAR(30) NOT NULL,
            Category VARCHAR(50) NOT NULL,
            SubCategory VARCHAR(50) NOT NULL,
            Sales DECIMAL(10,2) NOT NULL,
            Quantity INT NOT NULL,
            Discount DECIMAL(10,2) NOT NULL,
            Profit DECIMAL(10,2) NOT NULL
        );
    """)
    conn.commit()

except Exception as e:
    print(f"{e}")

finally:
    conn.close()

print("Database and table created successfully!")
