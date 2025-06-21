import pyodbc

def getConnection(index):
    connections = ["DRIVER={SQL Server};SERVER=WANGXING;DATABASE=Medicos;Trusted_Connection=yes;", "DRIVER={SQL Server};SERVER=POLISTP98;DATABASE=Medicos;Trusted_Connection=yes;"]
    try:
        connection = pyodbc.connect(connections[index])
        return connection
    except Exception as e:
        return f"Error: {e}"