import mysql.connector
from mysql.connector import Error

def initialize_db(db_name: str, mysql_pass: str):

    try: 
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=mysql_pass
        )

        cursorObject = connection.cursor()
        # initialize db
        print(f"creating database {db_name}...")
        cursorObject.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
        print(f"database {db_name} successfully created.")

    except Error as e:
        print(f"Error: {e}")

    finally:
        print("closing MySQL connection...")
        if cursorObject:
            cursorObject.close()
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":

    password = str(input("enter Mysql Password= "))
    db = str(input("name of database= "))

    if password and db:
        # execute
        initialize_db(db_name=db, mysql_pass=password)
    else:
        print("terminating program. No password and database entered.")