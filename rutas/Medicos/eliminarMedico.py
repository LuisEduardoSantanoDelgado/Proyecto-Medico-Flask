from flask import Blueprint, render_template ,  request, flash, redirect, url_for
from BDAyudas.QueryExecute import execute_query
from decorators.roleRequired import role_required

eliminarMedico_bp = Blueprint('eliminarMedico', __name__)

@eliminarMedico_bp.route("/eliminarMedico/<rfc>", methods=["GET"])
@role_required(2)
def mostrarEliminarMedico(rfc):
    print(f"-----------------Entrando a eliminar medico------------------ {rfc}")
    errores = {}
    try:
        medico = execute_query("SELECT * FROM dbo.DatosMedico(?) ", (rfc,), fetch="one")
        print(f"Medico encontrado: {medico}")
        print(f"Tipo de medico: {type(medico)}")
        if not medico:
            errores["medicoNotFound"] = "Médico no encontrado"
        else:
            return render_template("Medicos/EliminarMedico.html", medico=medico)
    except Exception as e:
        errores["dbError"] = "Error al obtener datos del médico"
        print(f"Error: {e}")

    return render_template("Medicos/EliminarMedico.html", errores=errores, medico=None) 

@eliminarMedico_bp.route("/eliminarMedico", methods=["POST"])
@role_required(2)
def eliminarMedico():
    print("Enviando eliminar médico --------------------------")
    errores = {}
    
    try:
        
        id_med = request.form.get("id", "0").strip()
        print(f"ID del médico recibido: {id_med}")
        print(f"Tipo de ID del médico: {type(id_med)}")
        if  not id_med:
            errores["emptyValues"] = "Error: ID del médico no proporcionado"
        else:
            resultado = execute_query(
                "DECLARE @resultado INT; EXEC EliminarMedico ?, @resultado OUTPUT; SELECT @resultado AS Resultado",
                (id_med,),
                fetch="one", commit=True
            )
            print(f"Resultado de la eliminación: {resultado}")
            if resultado is not None:
                match resultado.Resultado:
                    case 0:
                        flash("Médico eliminado exitosamente")
                        return redirect(url_for("medicoAdmin.medicoAdmin"))
                    case 1:
                        errores["medicoNotFound"] = "Error al encontrar el médico"
                        return render_template("Medicos/EliminarMedico.html", errores=errores, medico=None)
                    case 2:
                        errores["medicoInactive"] = "El médico ya está inactivo"
                        return render_template("Medicos/EliminarMedico.html", errores=errores, medico=None)
                    case _:
                        errores["dbError"] = "Error desconocido al eliminar el médico"
                        return render_template("Medicos/EliminarMedico.html", errores=errores, medico=None)
        
    except Exception as e:
        print(f"Error al eliminar médico, pipipi: {str(e)}")
        errores["dbError"] = "Error al eliminar el médico"
        print(f"Error: {e}")

    return render_template("Medicos/EliminarMedico.html", errores=errores, medico=None)