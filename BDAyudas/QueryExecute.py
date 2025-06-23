from connection import getConnection

def execute_query(query, params=None, fetch="all", commit = False):
    try:
        conn = getConnection()
        cursor = conn.cursor()

       
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        
        if fetch == "all":
            result = cursor.fetchall()
        elif fetch == "one":
            result = cursor.fetchone()
        else:
            result = None
            
        if commit:
            conn.commit()  # Para INSERT, UPDATE, DELETE, etc.

        return result

    except Exception as e:
        print(f"Error executing query: {e}")
        return None

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
