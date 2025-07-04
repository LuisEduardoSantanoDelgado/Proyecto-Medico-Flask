from flask import Blueprint, render_template ,  request, flash
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required

eliminarPaciente_bp = Blueprint('eliminarPaciente', __name__)
@eliminarPaciente_bp.route("/eliminarPaciente")
@login_required
def mostrarEliminarPaciente(id_paciente):
    errores = {}
    try:
        paciente = execute_query("SELECT * FROM Pacientes WHERE ID_paciente = ?", (id_paciente,), fetch="one")
        if not paciente:
            errores["pacienteNotFound"] = "Paciente no encontrado"
        else:
            return render_template("Pacientes/EliminarExp.html", paciente=paciente, errores=errores)
    except Exception as e:
        errores["dbError"] = "Error al obtener datos del paciente"
        print(f"Error: {e}")

    return render_template("Pacientes/EliminarExp.html", errores=errores, paciente=[])


@eliminarPaciente_bp.route("/eliminarPaciente", methods = ["POST"])
@login_required
def eliminarPaciente():
    errores = {}
    try:
        id_paciente = request.form.get("id_paciente", "").strip()
        if not id_paciente:
            errores["pacienteNotFound"] = "Error al eliminar el paciente, ID no proporcionado"

        resultado = execute_query(
            "EXEC EliminarPaciente ?",
            (id_paciente,),
            fetch="one", commit=True
        )

        if resultado is None or resultado[0] == 1:
            errores["deleteError"] = "Error al eliminar el paciente"
        elif resultado[0] == 2:
            errores["pacienteNotFound"] = "Paciente no encontrado"
            print("Paciente ya eliminado")
        else:
            flash("Paciente eliminado correctamente")
            return render_template("VistasPrincipales/Medico.html")

    except Exception as e:
        errores["dbError"] = "Error al eliminar el paciente"
        print(f"Error: {e}")
    return render_template("Pacientes/EliminarExp.html", errores=errores, paciente=[])