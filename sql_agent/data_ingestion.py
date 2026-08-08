import os 
import sys 
import sqlite3
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from ensure import ensure_annotations
import pandas as pd 
import kagglehub

DATA_SAVE_PATH = os.path.join(project_root, "sql_agent", "DataSource", "SampleSuperstore.csv")

def download_from_kaggle():
    # Download latest version
    file_path = kagglehub.dataset_download("bravehart101/sample-supermarket-dataset")
    print("Path to dataset files:", file_path)

@ensure_annotations
def prepare_smaller_data(file_path: str, column_lst: list, no_of_rows: int):
    """
    - *purpose*: reads raw data and convert into smaller data according to project's requirements.
    - *inputs*:
    1. file_path: path of file
    2. column_lst: list of column names to keep
    3. no_of_rows: total number of rows to keep
    - *output*:
    1. new_df: smaller dataframe
    """

    try:
        no_col_count = 0
        no_column = []
        df = pd.read_csv(file_path)
        if not df.empty:
            print("Dataset found. Preparing smaller version")
            if no_of_rows > df.shape[0]:
                print(f"your {no_of_rows} exceed total rows of {df.shape[0]} dataset.")
            else:
                print("Valid rows. Verifying columns")
                for user_column in column_lst:
                    if user_column not in df.columns:
                        no_col_count += 1
                        no_column.append(user_column) 
                if no_col_count >= 1:
                    print(f"total {no_col_count} not found.\nColumn Names: {no_column}")
                else:
                    print("all columns matched. Returning df")
                    new_df = df[column_lst].head(no_of_rows)
                    return new_df
        else:
            print("Couldn't find dataset.")
        
    except Exception as e:
        print(f"error: {e}")
        return None

def store_into_db(df: pd.DataFrame, db_path: str = "Superstore.db"):
    """
    - *purpose*: stores the given dataframe into SQLite database row by row.
    - *inputs*:
    1. df: dataframe to store
    2. db_path: path to the SQLite database
    """
    if df is None or df.empty:
        print("Dataframe is empty or None. Nothing to store.")
        return

    try:
        # Create connection to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Storing {df.shape[0]} rows into database {db_path}...")
        for index, row in df.iterrows():
            cursor.execute("""
                INSERT INTO Records (Segment, City, State, Region, Category, SubCategory, Sales, Quantity, Discount, Profit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['Segment'],
                row['City'],
                row['State'],
                row['Region'],
                row['Category'],
                row['Sub-Category'],
                row['Sales'],
                row['Quantity'],
                row['Discount'],
                row['Profit']
            ))
        
        # Commit the transaction
        conn.commit()
        print("Data stored successfully.")
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error while storing data: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()


if __name__ == "__main__":
    os.path.exists(path=DATA_SAVE_PATH)
    col_lst = ['Segment','City','State','Region','Category','Sub-Category','Sales','Quantity','Discount','Profit']
    #print("downloading...")
    # download_from_kaggle()
    #print("downloaded.")
    print("program initiated")
    df = prepare_smaller_data(file_path=DATA_SAVE_PATH, column_lst=col_lst, no_of_rows=50)
    if df is None:
        print("Error: dataset is None.")
    else:
        print("total rows: ", df.shape[0])
        print("overview: \n",df.head(5))
        print("storing the dataset into Superstore.db")
        db_file = os.path.join(project_root, "sql_agent", "Superstore.db")
        store_into_db(df, db_path=db_file)
        print("data ingestion complete")