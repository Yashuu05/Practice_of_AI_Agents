import sqlite3

def verify_result(query:str):
    try: 
        conn = sqlite3.connect("SuperStore.db")
        cursor = conn.cursor()
        cursor.execute(query)
        ans = cursor.fetchall()
        cursor.close()
        return(str(ans))

    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    # goal: to find the region having highest profit
    my_query = """
    SELECT Region, SUM(Profit) AS TotalProfit
    FROM Records
    GROUP BY Region
    ORDER BY SUM(Profit) DESC
    LIMIT 1;
    """
    output = verify_result(
        query=my_query
    )

    print(output)