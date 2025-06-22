from connection import getConnection
from flask import Flask, jsonify, render_template, request, url_for, flash, redirect, session
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "mysecretkey"

# Funciones
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def encriptar_contrasena(password_plano):
   
    # Genera el hash en formato UTF-8 (string)
    hash_utf8 = bcrypt.generate_password_hash(password_plano).decode('utf-8')
    
    # Convierte el string a bytes para almacenar como VARBINARY
    hash_bytes = hash_utf8.encode('utf-8')
    
    return hash_bytes


def validarSesion(valor, redirigir):
    if valor not in session:
        return redirect(url_for(redirigir))

#Rutas
@app.route("/")
def home():
    return render_template("AgregarMedico.html")

# Manejo de medicos
@app.route("/agregar_medico", methods = ["POST"])
def agregarMedico():
    errores = {}
    nombre = request.form.get("nombre", "").strip()
    apellido_paterno = request.form.get("apellido_P", "").strip()
    apellido_materno = request.form.get("apellido_M", "").strip()
    cedula = request.form.get("cedula", "").strip()
    rfc = request.form.get("rfc", "").strip()
    correo = request.form.get("correo", "").strip()
    passwordNE = request.form.get("password", "").strip()
    id_rol = request.form.get("rol", "").strip()

    if not rfc or not nombre or not apellido_paterno or not apellido_materno or not passwordNE or not id_rol or not cedula:
        errores["emptyValues"] = "Valores vacíos"

    if len(rfc) != 13:
        errores["rfcLen"] = "El RFC debe tener 13 caracteres"
    
    if len(passwordNE) < 8:
        errores["passwordLen"] = "La contraseña debe tener al menos 8 caracteres"

    if len(cedula) < 7:
        errores["cedulaLen"] = "La cédula profesional debe tener al menos 7 caracteres"

    if not errores:
        try:
           
            hashed_bytes = encriptar_contrasena(passwordNE)

            conn = getConnection(2)
            cursor = conn.cursor()

            cursor.execute("""
                            DECLARE @res INT;
                            EXEC InsertarMedico ?, ?, ?, ?, ?, ?, ?, ?, @res OUTPUT;
                            SELECT @res AS Resultado;
                        """, nombre, apellido_paterno, apellido_materno, cedula, rfc, correo, hashed_bytes, id_rol)

            resultado = cursor.fetchone()

            if resultado and resultado.Resultado == 1:
                errores["rfcExists"] = "El RFC ya está registrado"
                return render_template("AgregarMedico.html", errores=errores)
            
            if resultado and resultado.Resultado == 2:
                errores["mailExists"] = "El correo ya está registrado"
                return render_template("AgregarMedico.html", errores=errores)
            
            conn.commit()
            flash("Médico agregado exitosamente")

        except Exception as e:
            errores["dbError"] = "Error al agregar médico"
            print(f"Error: {e}")
        finally:
            cursor.close()

    return render_template("AgregarMedico.html", errores = errores)

@app.route("/login", methods = ["POST"])
def login():
    errors = {}

    rfc = request.form.get("rfc", "").strip()
    password = request.form.get("password", "").strip()

    if not rfc or not password:
        errors["emptyValues"] = "RFC o contraseña vacíos"

    if not errors:
        try:
            conn = getConnection(2)
            cursor = conn.cursor()
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

#Comprobar la conexión a la base de datos
@app.route("/DBCheck")
def dbCheck():
    try:
        conn = getConnection(2)
        cursor = conn.cursor()
        cursor.execute("Select 1")
        return jsonify({"status": "Ok", "message": "Conectado"}), 200
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500
    finally:
        cursor.close()

#ERRORES
@app.errorhandler(404)
def paginaNoEncontrada(e):
    return "¡Cuidado, error de capa 8!", 404

@app.errorhandler(405)
def error505(e):
    return "¡Revisa el método de envio!", 405

if __name__ == "__main__":
    app.run(port = 3000, debug = True)