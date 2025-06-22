from connection import getConnection
from flask import Flask, jsonify, render_template, request, url_for, flash, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "mysecretkey"

@app.before_request
def session_temporal():
    session.permanent = False

# Funciones
def connectDB(index):
    return getConnection(index).cursor()

def validarSesion(valor, redirigir):
    if valor not in session:
        return redirect(url_for(redirigir))

# Rutas
@app.route("/")
def home():
    return render_template("POOproyecto/login.html")

@app.route("/medico")
def medico():
    nombre = session.get("nombre_medico", "Invitado")
    return validarSesion("nombre_medico", "login") or render_template("POOproyecto/Medico.html", nombre_medico = nombre)

@app.route("/medicoAdmin")
def medicoAdmin():
    nombre = session.get("nombre_medico", "Invitado")
    return validarSesion("nombre_medico", "login") or render_template("POOproyecto/MedicoAdmin.html", nombre_medico = nombre)

@app.route("/cita")
def cita():
    return render_template("POOproyecto/AgregarCita.html")

@app.route("/expediente")
def expediente():
    return render_template("POOproyecto/AgregarExp.html")

@app.route("/consulta")
def consulta():
    return render_template("POOproyecto/consulta.html")

@app.route("/consultarExpediente")
def consutar_expediente():
    return render_template("POOproyecto/ConsultarExp.html")

@app.route("/login", methods = ["POST"])
def login():
    errors = {}

    rfc = request.form.get("rfc", "").strip()
    password = request.form.get("password", "").strip()

    if not rfc or not password:
        errors["emptyValues"] = "RFC o contraseña vacíos"

    if not errors:
        try:
            cursor = connectDB(1)
            cursor.execute("SELECT CONCAT(Nombres, ' ', Apellido_paterno, ' ', Apellido_materno), Contrasena, ID_rol from Medicos WHERE rfc = ?", (rfc,))
            # cursor.execute("SELECT R.Nombre from Medicos M INNER JOIN Roles R ON M.ID_rol = R.ID_rol WHERE M.RFC = ?", (rfc,))
            # rol_tuple = cursor.fetchone()
            # rol_db = rol_tuple[0]
            result = cursor.fetchone()
            if not result:
                errors["invalidData"] = "RFC no encontrado"
            else:
                nombre_medico, password_medico, rol_medico = result
                if password == password_medico:
                    session["nombre_medico"] = nombre_medico
                    match rol_medico:
                        case 1:
                            return redirect(url_for("medico"))
                        case 2:
                            return redirect(url_for("medicoAdmin"))
                else:
                    errors["invalidLogin"] = "Contraseña incorrecta"
        except Exception as e:
            errors["loginError"] = "Error al intentar iniciar sesión"
            print(f"Error: {e}")
        finally:
            cursor.close()
    return render_template("POOproyecto/login.html", err = errors)

# Comprobar la conexión a la base de datos
@app.route("/DBCheck")
def dbCheck():
    try:
        cursor = connectDB(1) # Cambia el índice según la conexión que quieras probar
        cursor.execute("Select 1")
        return jsonify({"status": "Ok", "message": "Conectado"}), 200
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500
    finally:
        cursor.close()

# ERRORES
@app.errorhandler(404)
def paginaNoEncontrada(e):
    return "¡Cuidado, error de capa 8!", 404

@app.errorhandler(405)
def error505(e):
    return "¡Revisa el método de envio!", 405

if __name__ == "__main__":
    app.run(port = 3000, debug = True)