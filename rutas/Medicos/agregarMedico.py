from flask import Blueprint, render_template ,  request, flash, redirect, url_for
from BDAyudas.QueryExecute import execute_query
from decorators.roleRequired import role_required
from utility.encriptarContrasena import encriptar_contrasena

agregarMedico_bp = Blueprint('agregarMedico', __name__)
@agregarMedico_bp.route("/agregarMedico")
@role_required(2) 
def mostrarAgregarMedico():
    print("Accediendo a la página de agregar médico")
    return render_template("Medicos/AgregarMedico.html")
@agregarMedico_bp.route("/agregarMedico", methods = ["POST"])
@role_required(2)
def agregarMedico():
    print("Enviando agregar médico --------------------------")
    errores = {}
    nombre = request.form.get("nombre", "").strip()
    apellido_paterno = request.form.get("apellido_P", "").strip()
    apellido_materno = request.form.get("apellido_M", "").strip()
    cedula = request.form.get("cedula", "").strip()
    rfc = request.form.get("rfc", "").strip()
    correo = request.form.get("correo", "").strip()
    passwordNE = request.form.get("password", "").strip()
    id_rol = request.form.get("rol", "0").strip()

    print(f"Datos recibidos: nombre={nombre}, apellido_paterno={apellido_paterno}, apellido_materno={apellido_materno}, cedula={cedula}, rfc={rfc}, correo={correo}, passwordNE={passwordNE}, id_rol={id_rol}")
    print(f"Tipos de los datos: nombre={type(nombre)}, apellido_paterno={type(apellido_paterno)}, apellido_materno={type(apellido_materno)}, cedula={type(cedula)}, rfc={type(rfc)}, correo={type(correo)}, passwordNE={type(passwordNE)}, id_rol={type(id_rol)}")
    
    if not rfc or not nombre or not apellido_paterno or not apellido_materno or not passwordNE or not id_rol or not cedula or not correo:
        errores["emptyValues"] = "No se permiten campos vacíos"

    if len(rfc) != 13:
        errores["rfcLen"] = "El RFC debe tener 13 caracteres"
    
    if len(passwordNE) < 8:
        errores["passwordLen"] = "La contraseña debe tener al menos 8 caracteres"

    if len(cedula) < 7:
        errores["cedulaLen"] = "La cédula profesional debe tener al menos 7 caracteres"

    if errores:
        print(f"Errores encontrados: {errores}")
        return render_template("Medicos/AgregarMedico.html", errores=errores)
    else:
        print("No se encontraron errores, procediendo a agregar médico")
        try:
            hashed_bytes = encriptar_contrasena(passwordNE)
            id_rol = int(id_rol) 
            resultado = execute_query(
                "DECLARE @res INT; EXEC InsertarMedico ?, ?, ?, ?, ?, ?, ?, ?, @res OUTPUT; SELECT @res AS Resultado",
                (nombre, apellido_paterno, apellido_materno, cedula, rfc, correo, hashed_bytes, id_rol),
                fetch="one", commit=True
            )
            print(f"Resultado de la inserción: {resultado}")
            if resultado:
                print(f"Resultado obtenido: {resultado.Resultado}")
                match resultado.Resultado:
                    case 1:
                        print("Médico agregado exitosamente")
                        errores["rfcExists"] = "El RFC ya está registrado"
                        return render_template("AgregarMedico.html", errores=errores)
                    case 2:
                        print("El correo ya está registrado")
                        errores["mailExists"] = "El correo ya está registrado"
                        return render_template("AgregarMedico.html", errores=errores)
                    case 0:
                        print("Médico agregado exitosamente")
                        flash("Médico agregado exitosamente")
                        return redirect(url_for("medicoAdmin.medicoAdmin"))
                    case _:
                        print("Error desconocido al agregar médico")
                        errores["dbError"] = "Error desconocido al agregar médico"

        except Exception as e:
            errores["dbError"] = "Error al agregar médico"
            print(f"Error en agregar medicos: {str(e)}")

    return render_template("Medicos/AgregarMedico.html", errores = errores)