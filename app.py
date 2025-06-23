from connection import getConnection
from flask import Flask, jsonify, render_template, request, url_for, flash, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "mysecretkey"

# Funciones
def connectDB(index):
    return getConnection(index).cursor()

def validarSesion(valor, redirigir):
    if valor not in session:
        return redirect(url_for(redirigir))

#Rutas
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
            cursor = connectDB(3)
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


@app.route("/agregar_medico", methods=["GET", "POST"])
def agregar_medico():
    validar = validarSesion("nombre_medico", "login")
    if validar:
        return validar

    if request.method == "POST":
        rfc = request.form.get("rfc", "").strip()
        nombre = request.form.get("nombre", "").strip()
        cedula = request.form.get("cedula", "").strip()
        correo = request.form.get("correo", "").strip()
        password = request.form.get("password", "").strip()
        rol_texto = request.form.get("rol")

        errores = {}

        if not rfc or not nombre or not cedula or not correo or not password or not rol_texto:
            errores["campos_vacios"] = "Todos los campos son obligatorios"
        else:
            rol_map = {
                "Medico": 1,
                "Medico Admin": 2
            }
            rol = rol_map.get(rol_texto)

            try:
                cursor = connectDB(3)
                cursor.execute("INSERT INTO Medicos (RFC, Nombres, Cedula, Correo, Contrasena, ID_rol) VALUES (?, ?, ?, ?, ?, ?)",
                               (rfc, nombre, cedula, correo, password, rol))
                flash("Médico agregado correctamente", "success")
                return redirect(url_for("medicoAdmin"))
            except Exception as e:
                errores["error_bd"] = f"Error al guardar en la base de datos: {str(e)}"
            finally:
                cursor.close()

        return render_template("POOproyecto/AgregarMedico.html", err=errores)

    return render_template("POOproyecto/AgregarMedico.html")


@app.route("/guardar_cita", methods=["GET", "POST"])
def guardar_cita():
    validar = validarSesion("nombre_medico", "login")
    if validar:
        return validar

    if request.method == "POST":
        sintomas = request.form.get("sintomas", "").strip()
        diagnostico = request.form.get("diagnostico", "").strip()
        tratamiento = request.form.get("tratamiento", "").strip()
        estudios = request.form.get("estudios", "").strip()

        errores = {}

        if not sintomas or not diagnostico or not tratamiento:
            errores["campos_vacios"] = "Todos los campos obligatorios deben llenarse"
        else:
            try:
                cursor = connectDB(3)
                cursor.execute(
                    "INSERT INTO Citas (Sintomas, Diagnostico, Tratamiento, Estudios) VALUES (?, ?, ?, ?)",
                    (sintomas, diagnostico, tratamiento, estudios)
                )
                flash("Cita guardada correctamente", "success")
                return redirect(url_for("medico")) 
            except Exception as e:
                errores["error_bd"] = f"Error al guardar la cita: {str(e)}"
            finally:
                cursor.close()

        return render_template("POOproyecto/DatosCita.html", err=errores)

    return render_template("POOproyecto/DatosCita.html")


@app.route("/editar_cita/<int:id_cita>", methods=["GET", "POST"])
def editar_cita(id_cita):
    validar = validarSesion("nombre_medico", "login")
    if validar:
        return validar

    cursor = connectDB(3)

    if request.method == "POST":
        sintomas = request.form.get("sintomas", "").strip()
        diagnostico = request.form.get("diagnostico", "").strip()
        tratamiento = request.form.get("tratamiento", "").strip()
        estudios = request.form.get("estudios", "").strip()

        errores = {}

        if not sintomas or not diagnostico or not tratamiento:
            errores["campos_vacios"] = "Todos los campos obligatorios deben llenarse"
        else:
            try:
                cursor.execute("""
                    UPDATE Citas 
                    SET Sintomas = ?, Diagnostico = ?, Tratamiento = ?, Estudios = ?
                    WHERE ID_cita = ?
                """, (sintomas, diagnostico, tratamiento, estudios, id_cita))
                flash("Cita actualizada correctamente", "success")
                return redirect(url_for("consulta"))
            except Exception as e:
                errores["error_bd"] = f"Error al actualizar la cita: {str(e)}"
            finally:
                cursor.close()

        return render_template("POOproyecto/EditarCita.html", err=errores)

    else:
        try:
            cursor.execute("SELECT Sintomas, Diagnostico, Tratamiento, Estudios FROM Citas WHERE ID_cita = ?", (id_cita,))
            cita = cursor.fetchone()
            if cita:
                sintomas, diagnostico, tratamiento, estudios = cita
                return render_template("POOproyecto/EditarCita.html", sintomas=sintomas, diagnostico=diagnostico,
                                       tratamiento=tratamiento, estudios=estudios, id_cita=id_cita)
            else:
                flash("Cita no encontrada", "warning")
                return redirect(url_for("consulta"))
        except Exception as e:
            flash(f"Error al cargar la cita: {str(e)}", "danger")
            return redirect(url_for("consulta"))
        finally:
            cursor.close()


@app.route("/editar_expediente/<int:id_expediente>", methods=["GET", "POST"])
def editar_expediente(id_expediente):
    validar = validarSesion("nombre_medico", "login")
    if validar:
        return validar

    cursor = connectDB(3)

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        edad = request.form.get("edad", "").strip()
        genero = request.form.get("genero", "").strip()
        direccion = request.form.get("direccion", "").strip()
        telefono = request.form.get("telefono", "").strip()

        errores = {}
        if not nombre or not edad or not genero:
            errores["faltan_campos"] = "Nombre, edad y género son obligatorios"
        else:
            try:
                cursor.execute("""
                    UPDATE Expedientes
                    SET Nombre = ?, Edad = ?, Genero = ?, Direccion = ?, Telefono = ?
                    WHERE ID_expediente = ?
                """, (nombre, edad, genero, direccion, telefono, id_expediente))
                flash("Expediente actualizado correctamente", "success")
                return redirect(url_for("expediente"))
            except Exception as e:
                errores["bd_error"] = f"Error al actualizar expediente: {str(e)}"
            finally:
                cursor.close()

        return render_template("POOproyecto/EditarExp.html", err=errores)

    else:
        try:
            cursor.execute("SELECT Nombre, Edad, Genero, Direccion, Telefono FROM Expedientes WHERE ID_expediente = ?", (id_expediente,))
            expediente = cursor.fetchone()
            if expediente:
                return render_template("POOproyecto/EditarExp.html", expediente=expediente, id_expediente=id_expediente)
            else:
                flash("Expediente no encontrado", "warning")
                return redirect(url_for("expediente"))
        except Exception as e:
            flash(f"Error al cargar expediente: {str(e)}", "danger")
            return redirect(url_for("expediente"))
        finally:
            cursor.close()

@app.route("/editar_medico/<rfc>", methods=["GET", "POST"])
def editar_medico(rfc):
    validar = validarSesion("nombre_medico", "login")
    if validar:
        return validar

    cursor = connectDB(3)

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        cedula = request.form.get("cedula", "").strip()
        correo = request.form.get("correo", "").strip()
        password = request.form.get("password", "").strip()
        rol_texto = request.form.get("rol", "").strip()

        errores = {}

        if not nombre or not cedula or not correo or not rol_texto:
            errores["campos_vacios"] = "Todos los campos excepto la contraseña son obligatorios"
        else:
            rol_map = {
                "Medico": 1,
                "Medico Admin": 2
            }
            rol = rol_map.get(rol_texto)

            try:
                if password:
                    cursor.execute("""
                        UPDATE Medicos
                        SET Nombres = ?, Cedula = ?, Correo = ?, Contrasena = ?, ID_rol = ?
                        WHERE RFC = ?
                    """, (nombre, cedula, correo, password, rol, rfc))
                else:
                    cursor.execute("""
                        UPDATE Medicos
                        SET Nombres = ?, Cedula = ?, Correo = ?, ID_rol = ?
                        WHERE RFC = ?
                    """, (nombre, cedula, correo, rol, rfc))

                flash("Médico actualizado correctamente", "success")
                return redirect(url_for("medicoAdmin"))
            except Exception as e:
                errores["bd_error"] = f"Error al actualizar médico: {str(e)}"
            finally:
                cursor.close()

        return render_template("POOproyecto/EditarMedico.html", rfc=rfc, nombre=nombre, cedula=cedula, correo=correo, rol=rol_texto, err=errores)

    else:
        try:
            cursor.execute("""
                SELECT Nombres, Cedula, Correo, ID_rol
                FROM Medicos
                WHERE RFC = ?
            """, (rfc,))
            medico = cursor.fetchone()

            if medico:
                nombre, cedula, correo, id_rol = medico
                rol_map_reverse = {
                    1: "Medico",
                    2: "Medico Admin"
                }
                rol = rol_map_reverse.get(id_rol, "Medico")
                return render_template("POOproyecto/EditarMedico.html", rfc=rfc, nombre=nombre, cedula=cedula, correo=correo, rol=rol)
            else:
                flash("Médico no encontrado", "warning")
                return redirect(url_for("medicoAdmin"))
        except Exception as e:
            flash(f"Error al cargar médico: {str(e)}", "danger")
            return redirect(url_for("medicoAdmin"))
        finally:
            cursor.close()

@app.route("/eliminar_cita/<int:id_cita>", methods=["GET", "POST"])
def eliminar_cita(id_cita):
    validar = validarSesion("nombre_medico", "login")
    if validar:
        return validar

    try:
        cursor = connectDB(3)
        cursor.execute("DELETE FROM Citas WHERE ID_cita = ?", (id_cita,))
        flash("Cita eliminada correctamente", "success")
    except Exception as e:
        flash(f"Error al eliminar la cita: {str(e)}", "danger")
    finally:
        cursor.close()

    return redirect(url_for("consulta"))

@app.route("/eliminar_expediente/<int:id_expediente>", methods=["GET"])
def eliminar_expediente(id_expediente):
    validar = validarSesion("nombre_medico", "login")
    if validar:
        return validar

    try:
        cursor = connectDB(3)
        cursor.execute("DELETE FROM Expedientes WHERE ID_expediente = ?", (id_expediente,))
        flash("Expediente eliminado correctamente", "success")
    except Exception as e:
        flash(f"Error al eliminar expediente: {str(e)}", "danger")
    finally:
        cursor.close()

    return redirect(url_for("expediente"))


#Comprobar la conexión a la base de datos
@app.route("/DBCheck")
def dbCheck():
    try:
        cursor = connectDB(3)  # Cambia el índice según la conexión que quieras probar
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