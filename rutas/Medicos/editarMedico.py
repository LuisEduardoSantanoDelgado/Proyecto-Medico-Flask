from flask import Blueprint, render_template ,  request, flash
from BDAyudas.QueryExecute import execute_query
from decorators.roleRequired import role_required
from utility.encriptarContrasena import encriptar_contrasena

editarMedico_bp = Blueprint('editarMedico', __name__)

@editarMedico_bp.route("/editar_medico/<rfc>", methods=["GET"])
@role_required(2) 
def mostrarEditarMedico(rfc):
    errores = {}
    print(f"-----------------Aqui datos del edirar medico------------------ {rfc}")
    try:
        medico = execute_query("SELECT * FROM dbo.DatosMedico(?)", (rfc,), fetch="one")
        if not medico:
            errores["medicoNotFound"] = "Médico no encontrado"
        else:
            for med in medico:
                print(f"Medico encontrado: {med}")
            return render_template("Medicos/EditarMedico.html", medico=medico)
    except Exception as e:
        errores["dbError"] = "Error al obtener datos del médico"
        print(f"Error: {e}")

    return render_template("Medicos/EditarMedico.html", errores=errores)

@editarMedico_bp.route("/editar_medico", methods=["POST"])
@role_required(2)
def editarMedico():
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

        if not rfc or not nombre or not apellido_paterno or not apellido_materno or not passwordNE or not id_rol or not cedula or not id_med or not correo:
            errores["emptyValues"] = "Valores vacíos"

        if len(rfc) != 13:
            errores["rfcLen"] = "El RFC debe tener 13 caracteres"
        
        if len(passwordNE) < 8:
            errores["passwordLen"] = "La contraseña debe tener al menos 8 caracteres"

        if len(cedula) < 7:
            errores["cedulaLen"] = "La cédula profesional debe tener al menos 7 caracteres"
        print(f"Datos recibidos para editar: nombre={nombre}, apellido_paterno={apellido_paterno}, apellido_materno={apellido_materno}, "
              f"cedula={cedula}, rfc={rfc}, correo={correo}, passwordNE={passwordNE}, id_rol={id_rol}, id_med={id_med}")
        
        hashed_bytes = encriptar_contrasena(passwordNE)
        idMed = int(id_med)
        resultado = execute_query(
                "DECLARE @resultado INT; EXEC ActualizarMedico ?, ?, ?, ?, ?, ?, ?, ?,?, @resultado OUTPUT; SELECT @resultado AS Resultado",
                (idMed,nombre, apellido_paterno, apellido_materno, cedula, rfc, correo, hashed_bytes, id_rol),
                fetch="one", commit=True
            )
        print(f"Resultado de la consulta de edición: {resultado}")
        if resultado is not None and not errores:
            match resultado.Resultado:
                case 1:
                    errores["medicoNotFound"] = "El medico no existe"
                case 2:
                    errores["mailExists"] = "El correo ya está registrado"
                case 3:
                    errores["rfcExists"] = "El RFC ya está registrado"
                case 0:
                    flash("Médico actualizado exitosamente")
                    return render_template("Medicos/EditarMedico.html", medico=resultado)
                case _:
                    errores["dbError"] = "Error al actualizar médico"
        else:
            errores["queryError"] = "Error al ejecutar la consulta"

    except Exception as e:
        errores["dbError"] = "Error al obtener datos del médico"
        print(f"Error: {e}")
    

    return render_template("Medicos/EditarMedico.html", errores=errores, medico=None)