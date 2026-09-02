# fetching required airport codes 
import os 
import sys 
import sqlite3
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
     sys.path.insert(0, project_root)
from dotenv import load_dotenv
load_dotenv()

# get IATA code for flight details
def get_iata_by_city(city_name: str="", country_name:str="", db_path:str="", table_name:str="code"):
    """
    - purpose: searches database to find iata codes for given city and country
    - Args:
        1. city_name: name of the desired city
        2. country_name: name of the country where city is present.
    - returns:
        1. IATA code, airport name
    """
    
    try:
        print(f"connecting to database: {db_path}")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            print(f"connected to {db_path}")
            if city_name and country_name=="":
                cursor.execute(f"""
                    SELECT code, airport_name
                    FROM {table_name}
                    WHERE city_name LIKE '%{city_name}%'
                    """)
                result = cursor.fetchall()
                code, airport = result[0]
                return code, airport
        
            elif country_name and city_name=="":
                cursor.execute(f"""
                    SELECT code, airport_name
                    FROM {table_name}
                    WHERE country LIKE '%{country_name}%'
                """)
                result = cursor.fetchall()
                code, airport = result[0]
                return code, airport
        
            elif city_name and country_name:
                cursor.execute(f"""
                    SELECT code, airport_name
                    FROM {table_name}
                    WHERE city_name LIKE '%{city_name}%' AND country LIKE '%{country_name}%'
                """)
                result = cursor.fetchall()
                code, airport = result[0]
                return code, airport
        
            else:
                return "Error: No value for city and country provided"

    except Exception as e:
        print(f"Error while searching code in database: {e}")
        return f"{e}"

# fetch coordinated of the given country
def fetch_corrdinates(city: str, country: str, db_name:str, table_name: str):
    db_path = os.path.join(project_root,"Travel_Agent","db",f"{db_name}.db")

    try:
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            if city and country=="":
                cursor.execute(f"""
                    SELECT latitude, longitude
                    FROM {table_name}
                    WHERE City LIKE '%{city}%'
                """)
                return cursor.fetchall()

            elif country and city=="":
                cursor.execute(f"""
                    SELECT latitude, longitude
                    FROM {table_name}
                    WHERE Country LIKE '%{country}%'
                """)
                return cursor.fetchall()

            elif city and country:
                cursor.execute(f"""
                    SELECT latitude, longitude
                    FROM {table_name}
                    WHERE City LIKE '%{city}%' AND Country LIKE '%{country}%'
                """)
                return cursor.fetchall()

            else:
                return "Error: No value for city and country provided"
    except Exception as e:
        return e