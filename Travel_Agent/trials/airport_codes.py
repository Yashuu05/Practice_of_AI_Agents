# fetching required airport codes 
import os 
import sys 
import sqlite3
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
     sys.path.insert(0, project_root)

def get_iata_by_city(city_name: str="", country_name:str="", db_name:str="CityCode.db", table_name:str="code"):
    """
    - purpose: searches database to find iata codes for given city and country
    - Args:
        1. city_name: name of the desired city
        2. country_name: name of the country where city is present.
    - returns:
        1. IATA code, airport name
    """
    db_path = os.path.join(project_root,"Travel_Agent","db",f"{db_name}")
    print(db_path)
    try:
        print(f"connecting to database: {db_name}")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            print(f"connected to {db_name}")
            if city_name and country_name=="":
                cursor.execute(f"""
                    SELECT code, airport_name
                    FROM {table_name}
                    WHERE city_name LIKE '%{city_name}%'
                    """)
                return cursor.fetchall()
        
            elif country_name and city_name=="":
                cursor.execute(f"""
                    SELECT code, airport_name
                    FROM {table_name}
                    WHERE country LIKE '%{country_name}%'
                """)
                return cursor.fetchall()
        
            elif city_name and country_name:
                cursor.execute(f"""
                    SELECT code, airport_name
                    FROM {table_name}
                    WHERE city_name LIKE '%{city_name}%' AND country LIKE '%{country_name}%'
                """)
                return cursor.fetchall()
        
            else:
                return "Error: No value for city and country provided"

    except Exception as e:
        print(f"Error while searching code in database: {e}")
        return f"{e}"

if __name__ == "__main__":
    result = get_iata_by_city(
        city_name="London",
        db_name="CityCode.db",
        table_name="code" 
    )
    
    print("result:\n", result)
    #print(f"airport={airport} | code: {code}")