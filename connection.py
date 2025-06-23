import pyodbc

def getConnection(index):
    connections = [
        "DRIVER={SQL Server};SERVER=WANGXING;DATABASE=Medicos;Trusted_Connection=yes;",
        "DRIVER={SQL Server};SERVER=POLISTP98;DATABASE=Medicos;Trusted_Connection=yes;",
        "DRIVER={SQL Server};SERVER=DESKTOP-FGPKF6Q;DATABASE=Medicos;Trusted_Connection=yes;"
        "DRIVER={SQL Server};SERVER=IANDAVID\\SQLSERVER;DATABASE=Medicos;Trusted_Connection=yes;"
    ]
    
    if index not in range(len(connections)):
        raise IndexError("Índice de conexión fuera de rango")

    try:
        connection = pyodbc.connect(connections[index])
        return connection
    except pyodbc.Error as e:
        raise ConnectionError(f"Error al conectar a la base de datos: {e}")