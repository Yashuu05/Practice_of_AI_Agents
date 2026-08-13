import mysql.connector
from mysql.connector import Error

def initialize_database(database_name: str, mysql_username: str, mysql_password: str):
    connection = None
    cursor = None
    db_name = database_name
    
    try:
        # 1. Connect to the MySQL server (leave out the 'database' argument)
        connection = mysql.connector.connect(
            host="localhost",
            user=mysql_username,
            password=mysql_password 
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 2. Switch context to the database
            cursor.execute(f"USE {db_name};")
            
            # 3. Create table
            query_1 = """
            CREATE TABLE IF NOT EXISTS input (
                id INT AUTO_INCREMENT PRIMARY KEY,
                source VARCHAR(50),
                destination VARCHAR(50),
                departure DATE,
                arrival DATE,
                head_count INT,
                budget BIGINT
            );
            """
            cursor.execute(query_1)
            print("'input' table verified/created.")

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        
    finally:
        # 5. Clean up and close connections safely
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":

    db_name = str(input("enter database name= "))
    username = str(input("enter mysql username= "))
    password = str(input("enter mysql password= "))

    if db_name and username and password:
        initialize_database(
            database_name=db_name,
            mysql_username=username,
            mysql_password=password
        )
    else:
        print('program terminated. No input entered.')