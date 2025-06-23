from connection import getConnection
from flask import Flask, jsonify, render_template, request, url_for, flash, redirect, session
from flask_bcrypt import Bcrypt
from functools import wraps

app = Flask(__name__)
app.secret_key = "mysecretkey"

# Funciones

bcrypt = Bcrypt()

def encriptar_contrasena(password_plano):
   
    # Genera el hash en formato UTF-8 (string)
    hash_utf8 = bcrypt.generate_password_hash(password_plano).decode('utf-8')
    
    # Convierte el string a bytes para almacenar como VARBINARY
    hash_bytes = hash_utf8.encode('utf-8')
    
    return hash_bytes


def login_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            
            if "rfc" not in session:
                flash("Inicia sesión para continuar")
                return redirect(url_for("home"))

            if roles and session.get("rol") not in roles:
                flash("No tienes permisos para ver esa página")
                # vuelve a la página anterior o al home
                return redirect(request.referrer or url_for("home"))

            
            return view_func(*args, **kwargs)
        return wrapped_view
    return decorator

#Rutas -----------------------------------
#Inicio de sesión
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    errores = {}
    rfc = request.form.get("rfc", "").strip()
    password = request.form.get("password", "").strip()

    if not rfc or not password:
        errores["emptyValues"] = "RFC o contraseña vacíos"

    if not errores:
        try:
            conn = getConnection(2)
            cursor = conn.cursor()
            cursor.execute("EXEC Obtener_Contrasena ?", rfc)
            result = cursor.fetchone()

            if not result:
                errores["DBError"] = "Error al consultar la base de datos"
            elif result:
                passHash = result.Hash_Contrasena
                if passHash == 0:
                    errores["RFCNotFound"] = "RFC no encontrado"
                print(passHash)
                print("Tipo de dato:", type(passHash))

                
                if passHash and bcrypt.check_password_hash(passHash.decode('utf-8'), password):
                    cursor.execute("EXEC Obtener_ID_Rol ?", rfc)
                    rol_result = cursor.fetchone()
                    if not rol_result:
                        errores["DBError"] = "Error al consultar el rol"
                    else:
                        session["rfc"] = rfc
                        session["rol"] = rol_result.ID_Rol
                        match rol_result.ID_Rol:
                            case 1:
                                return redirect(url_for("medico"))
                            case 2:
                                return redirect(url_for("medicoAdmin"))
                            case _:
                                errores["invalidRole"] = "Rol no válido"
                else:
                    errores["invalidLogin"] = "Contraseña incorrecta"
             
        except Exception as e:
            errores["loginError"] = "Error al intentar iniciar sesión"
            print(f"Error: {e}")
        finally:
            cursor.close()

    return render_template("login.html", err=errores)

# Manejo de medicos
#Medico administrador
@app.route("/medicoAdmin")
@login_required(2)
def medicoAdmin():
    errores = {}
    
    try:
        rfc = session.get("rfc")
        conn = getConnection(2)
        cursor = conn.cursor()  
        cursor.execute("SELECT dbo.NombreCompletoMedico(?) AS Nombre", (rfc,))
        nombre = cursor.fetchone()
        if not nombre:
            errores["medicoNotFound"] = "Médico no encontrado"
        else:
            nombreMedico = nombre.Nombre
       
        tblMedicos = cursor.execute("SELECT CONCAT(Nombres,' ',Apellido_paterno,' ',Apellido_materno) AS Nombre_Medico, Cedula_profesional,RFC,Correo_electronico FROM Medicos WHERE Estatus = ?", 1).fetchall()
       
        if not tblMedicos:
            errores["noMedicos"] = "No hay médicos registrados"

        if not errores:   
            return render_template("medicoAdmin.html", tblMedicos=tblMedicos, nombreMedico=nombreMedico)
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        nombreMedico = None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return render_template("medicoAdmin.html", errores=errores)
#Medico
@app.route("/medico")
@login_required(1)
def medico():
    return render_template("medico.html")
#Agregar médico
@app.get("/agregar_medico")
@login_required(2)
def agregarMedico():
    return render_template("AgregarMedico.html")
#Inserción de médicos
@app.route("/agregar_medico", methods = ["POST"])
@login_required(2)
def insertarMedico():
    errores = {}
    nombre = request.form.get("nombre", "").strip()
    apellido_paterno = request.form.get("apellido_P", "").strip()
    apellido_materno = request.form.get("apellido_M", "").strip()
    cedula = request.form.get("cedula", "").strip()
    rfc = request.form.get("rfc", "").strip()
    correo = request.form.get("correo", "").strip()
    passwordNE = request.form.get("password", "").strip()
    id_rol = request.form.get("rol", "0").strip()

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

#Edicion de médicos
@app.route("/editar_medico/<rfc>")
@login_required(2)
def editarMedico(rfc):
    errores = {}
    try:
        conn = getConnection(2)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Medicos WHERE RFC = ?", rfc)
        medico = cursor.fetchone()

        if not medico:
            errores["medicoNotFound"] = "Médico no encontrado"
            return render_template("EditarMedico.html", errores=errores)

        return render_template("EditarMedico.html", medico=medico)

    except Exception as e:
        errores["dbError"] = "Error al obtener datos del médico"
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template("EditarMedico.html", errores=errores)

#Eliminación de médicos
@app.route("/eliminar_medico/<rfc>", methods=["POST"])
@login_required(2)
def eliminarMedico(rfc):
    errores = {}
    try:
        conn = getConnection(2)
        cursor = conn.cursor()
        cursor.execute("EXEC EliminarMedico ?", rfc)
        resultado = cursor.fetchone()

        if not resultado:
            errores["medicoNotFound"] = "Médico no encontrado"
            return render_template("medicoAdmin.html", errores=errores)

        if resultado.Resultado == 1:
            flash("Médico eliminado exitosamente")
            return redirect(url_for("medicoAdmin"))
        else:
            errores["dbError"] = "Error al eliminar médico"

    except Exception as e:
        errores["dbError"] = "Error al eliminar médico"
        print(f"Error: {e}")
    finally:
        cursor.close()

    return render_template("medicoAdmin.html", errores=errores)
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