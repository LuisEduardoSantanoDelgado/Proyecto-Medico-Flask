from flask import Blueprint, render_template ,  request, flash, redirect, url_for
from BDAyudas.QueryExecute import execute_query
from decorators.roleRequired import role_required
from utility.encriptarContrasena import encriptar_contrasena

editarMedico_bp = Blueprint('editarMedico', __name__)

@editarMedico_bp.route("/editarMedico/<rfc>", methods=["GET"])
@role_required(2) 
def mostrarEditarMedico(rfc):
    errores = {}
    print(f"-----------------Entrando a editar medico------------------ {rfc}")
    try:
        medico = execute_query("SELECT * FROM dbo.DatosMedico(?)", (rfc,), fetch="one")
        if not medico:
            errores["medicoNotFound"] = "Médico no encontrado"
        else:
            for med in medico:
                print(f"Informacion medico encontrada: {med}")
            return render_template("Medicos/EditarMedico.html", medico=medico)
    except Exception as e:
        errores["dbError"] = "Error al obtener datos del médico"
        print(f"Error al obtener datos del médico a editar: {str(e)}")

    return render_template("Medicos/EditarMedico.html", errores=errores, medico=None)

@editarMedico_bp.route("/editarMedico", methods=["POST"])
@role_required(2)
def editarMedico():
    print("Enviando editar médico --------------------------")
    errores = {}
    try:
        nombre = request.form.get("nombre", "").strip()
        apellido_paterno = request.form.get("apellido_P", "").strip()
        apellido_materno = request.form.get("apellido_M", "").strip()
        cedula = request.form.get("cedula", "").strip()
        rfc = request.form.get("rfc", "").strip()
        correo = request.form.get("correo", "").strip()
        passwordNE = request.form.get("password", "").strip()
        id_rol = request.form.get("rol", "0").strip()
        id_med = request.form.get("id", "").strip()

        if not id_med:
            errores["idMedico"] = "ID de médico no recibido"
            return render_template("Medicos/EditarMedico.html", errores=errores, medico=None)

        if not rfc or not nombre or not apellido_paterno or not apellido_materno or not passwordNE or not id_rol or not cedula or not correo or not passwordNE:
            errores["emptyValues"] = "Valores vacíos"
        
        if len(rfc) != 13:
            errores["rfcLen"] = "El RFC debe tener 13 caracteres"
        
        if len(passwordNE) < 8:
            errores["passwordLen"] = "La contraseña debe tener al menos 8 caracteres"

        if len(cedula) < 7:
            errores["cedulaLen"] = "La cédula profesional debe tener al menos 7 caracteres"

        idMed = int(id_med)
        idRol = int(id_rol)

        if errores:
            print(f"Errores encontrados: {errores}")
            return render_template("Medicos/EditarMedico.html", errores=errores, medico=None)
        else:
            print("No se encontraron errores, procediendo a editar médico")

            print(f"Datos recibidos para editar: nombre={nombre}, apellido_paterno={apellido_paterno}, apellido_materno={apellido_materno}, "
                f"cedula={cedula}, rfc={rfc}, correo={correo}, passwordNE={passwordNE}, id_rol={id_rol}, id_med={id_med}")
            
            print(f"Tipos de los datos: nombre={type(nombre)}, apellido_paterno={type(apellido_paterno)}, apellido_materno={type(apellido_materno)}, "
                f"cedula={type(cedula)}, rfc={type(rfc)}, correo={type(correo)}, passwordNE={type(passwordNE)}, id_rol={type(id_rol)}, id_med={type(id_med)}")
        
            hashed_bytes = encriptar_contrasena(passwordNE)
            resultado = execute_query(
                    "DECLARE @resultado INT; EXEC ActualizarMedico ?, ?, ?, ?, ?, ?, ?, ?,?, @resultado OUTPUT; SELECT @resultado AS Resultado",
                    (idMed,nombre, apellido_paterno, apellido_materno, cedula, rfc, correo, hashed_bytes, idRol),
                    fetch="one", commit=True
                )
            print(f"Resultado de la consulta de edición: {resultado}")

            if resultado:
                match resultado.Resultado:
                    case 1:
                        errores["medicoNotFound"] = "El medico no existe"
                        return render_template("Medicos/EditarMedico.html", errores=errores, medico=None)
                    case 2:
                        errores["rfcExists"] = "El RFC ya está registrado"
                        return render_template("Medicos/EditarMedico.html", errores=errores, medico=None)
                    case 3:
                        errores["mailExists"] = "El correo ya está registrado"
                        return render_template("Medicos/EditarMedico.html", errores=errores, medico=None)
                    case 0:
                        flash("Médico actualizado exitosamente")
                        return redirect(url_for("medicoAdmin.medicoAdmin"))
                    case _:
                        errores["dbError"] = "Error al actualizar médico"
                        return render_template("Medicos/EditarMedico.html", errores=errores, medico=None)
            else:
                errores["queryError"] = "Error al ejecutar la consulta"
                return render_template("Medicos/EditarMedico.html", errores=errores, medico=None)

    except Exception as e:
        errores["dbError"] = "Error al obtener datos del médico"
        print(f"Error en editar médico: {str(e)}")
    

    return render_template("Medicos/EditarMedico.html", errores=errores, medico=None)