# fetching required airport codes 
import os 
import sys 
import sqlite3
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
     sys.path.insert(0, project_root)

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