from flask import Blueprint, render_template ,  request, flash
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required

eliminarMedico_bp = Blueprint('eliminarMedico', __name__)

@eliminarMedico_bp.route("/eliminar_medico/<rfc>", methods=["GET"])
@login_required(2)
def mostrarEliminarMedico(rfc):
    errores = {}
    try:
        medico = execute_query("SELECT * FROM dbo.DatosMedico(?) ", (rfc,), fetch="one")
        if not medico:
            errores["medicoNotFound"] = "Médico no encontrado"
        else:
            return render_template("Medicos/EliminarMedico.html", medico=medico)
    except Exception as e:
        errores["dbError"] = "Error al obtener datos del médico"
        print(f"Error: {e}")

    return render_template("Medicos/EliminarMedico.html", errores=errores) 

@eliminarMedico_bp.route("/eliminar_medico", methods=["POST"])
@login_required(2)
def eliminarMedico():
    errores = {}
    try:
        
        id_med = request.form.get("id", "0").strip()

        if  not id_med:
            errores["emptyValues"] = "Error: ID del médico no proporcionado"
        else:
            resultado = execute_query(
                "DECLARE @resultado INT; EXEC EliminarMedico ?, @resultado OUTPUT; SELECT @resultado AS Resultado",
                (id_med,),
                fetch="one", commit=True
            )
            
            if resultado is not None:
                match resultado.Resultado:
                    case 0:
                        flash("Médico eliminado correctamente", "success")
                        return render_template("VistasPrincipales/MedicoAdmin.html")
                    case 1:
                        errores["medicoNotFound"] = "Error al encontrar el médico"
                    case 2:
                        errores["medicoInactive"] = "El médico ya está inactivo"
                    case _:
                        errores["unknownError"] = "Error desconocido al eliminar el médico"
        
    except Exception as e:
        errores["dbError"] = "Error al eliminar el médico"
        print(f"Error: {e}")

    return render_template("Medicos/EliminarMedico.html", errores=errores)