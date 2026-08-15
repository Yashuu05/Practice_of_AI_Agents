import pandas as pd 
import sqlite3
import os 
import sys 
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from datetime import datetime

class DataIngestion:

    def create_database(self, db_name:str="TouristPlace.db", table_name:str="coordinates") -> None:
        """
        - creates new sqlite3 database 
        - input:
            1. db_name: name of database to be created
            2. table_name: name of table to be created
        - returns:
            1. None
        """
        try: 
            print(f"{datetime.now().strftime('%H:%M:%S')} : creating {db_name} database...")
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            print(f"{datetime.now().strftime('%H:%M:%S')} : creating {table_name} table...")
            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                latitude DECIMAL(10,2) NOT NULL,
                longitude DECIMAL(10,2) NOT NULL,
                City VARCHAR(50) UNIQUE,
                Country VARCHAR(50)
            );            
            """)
            conn.commit()
            print(f"{datetime.now().strftime('%H:%M:%S')} : {table_name} table created in {db_name} database")

        except Exception as e:
            print(f"error: {e}")

        finally:
            conn.close()
            print(f"{datetime.now().strftime('%H:%M:%S')} : database connection closed")

    def insert_data_to_database(self, db_path: str, data_path: str, table_name:str):
        """
        - purpose: inserts .csv or .xlsx file to sqlite database
        - inputs:
            1. db_path: database path
            2. data_path: dataset path 
            3. table_name: name of table to insert the data
        """
        # read dataset

        try:
            print("reading dataset...")
            df = pd.read_csv(data_path)
            if not df.empty:
                print("processing dataset...")
                print(f"{df.head(2)}")
                df[['City', 'Country']] = df['place'].str.split(', ', expand=True)
                df = df.drop("place", axis=1)
                print(f"{df.head(2)}")
                print(f"inserting data to {db_path}")
                conn = sqlite3.connect(db_path)
                df.to_sql(f"{table_name}", conn, if_exists="append", index=False)
                conn.close()

        except Exception as e:
            print(f"{e}")


if __name__ == "__main__":

    obj = DataIngestion()
    obj.create_database(db_name="TouristPlace.db", table_name="coordinates")
    obj.insert_data_to_database(
        db_path=r"D:\projects\AgenticAI_Practice\Travel_Agent\db\TouristPlace.db",
        data_path=r"D:\projects\AgenticAI_Practice\Travel_Agent\data\tourist_places_coordinates.csv",
        table_name="coordinates"
    )