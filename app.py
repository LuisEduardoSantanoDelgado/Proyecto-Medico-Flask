from flask import Flask
from rutas.login import login_bp
from rutas.VistasPrincipales.medicoAdmin import medicoAdmin_bp
from rutas.Medicos.agregarMedico import agregarMedico_bp
from rutas.Medicos.editarMedico import editarMedico_bp
from rutas.Medicos.eliminarMedico import eliminarMedico_bp
app = Flask(__name__)
app.secret_key = "mysecretkey"




#Rutas -----------------------------------
#Inicio de sesión
app.register_blueprint(login_bp)

# Manejo de medicos
#Medico administrador
app.register_blueprint(medicoAdmin_bp)

#Medico

#Agregar médico
app.register_blueprint(agregarMedico_bp)

#Edicion de médicos
app.register_blueprint(editarMedico_bp)


#Eliminación de médicos
app.register_blueprint(eliminarMedico_bp)
#Comprobar la conexión a la base de datos
# @app.route("/DBCheck")
# def dbCheck():
#     try:
#         conn = getConnection(2)
#         cursor = conn.cursor()
#         cursor.execute("Select 1")
#         return jsonify({"status": "Ok", "message": "Conectado"}), 200
#     except Exception as e:
#         return jsonify({"status": "Error", "message": str(e)}), 500
#     finally:
#         cursor.close()

#ERRORES
@app.errorhandler(404)
def paginaNoEncontrada(e):
    return "¡Cuidado, error de capa 8!", 404

@app.errorhandler(405)
def error505(e):
    return "¡Revisa el método de envio!", 405

if __name__ == "__main__":
    app.run(port = 3000, debug = True)