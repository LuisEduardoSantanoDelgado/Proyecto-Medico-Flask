from flask import Blueprint, render_template ,  request, flash, redirect, url_for
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required

eliminarPaciente_bp = Blueprint('eliminarPaciente', __name__)
@eliminarPaciente_bp.route("/eliminarPaciente/<id_paciente>")
@login_required
def mostrarEliminarPaciente(id_paciente):
    print('----------------- Entrando a eliminar paciente ----------------------------')
    errores = {}
    try:
        paciente = execute_query("SELECT * FROM Pacientes WHERE ID_paciente = ?", (id_paciente,), fetch="one")
        print(f'Paciente obtenido {paciente}')
        if not paciente:
            print('Error paciente no encontrado')
            errores["pacienteNotFound"] = "Paciente no encontrado"
        else:
            return render_template("Pacientes/EliminarExp.html", paciente=paciente, errores=errores)
    except Exception as e:
        print('Excepción durante obtener paciente a eliminar')
        errores["dbError"] = "Error al obtener datos del paciente"
        print(f"Error: {str(e)}")

    return render_template("Pacientes/EliminarExp.html", errores=errores, paciente=None)


@eliminarPaciente_bp.route("/eliminarPaciente", methods = ["POST"])
@login_required
def eliminarPaciente():
    print('Enviando solicitud para eliminar paciente-------------------------')
    errores = {}
    try:
        id_paciente = request.form.get("id_paciente", "").strip()
        print(f'id obtenida {id_paciente}')
        if not id_paciente:
            print('No se pudo obtener el id del paciente del formulario')
            errores["pacienteNotFound"] = "Error al eliminar el paciente, ID no proporcionado"
            return render_template("Pacientes/EliminarExp.html", errores=errores, paciente=None)
        
        resultado = execute_query(
            "DECLARE @res INT; EXEC EliminarPaciente ?, @res OUTPUT; SELECT @res AS Resultado;",
            (id_paciente,), fetch="one", commit=True
        )

        print(f"Desde eliminarPaciente Resultado de la consulta de eliminacion: {resultado}")
        
        if resultado is None or resultado[0] == 1:
            errores["deleteError"] = "Error al eliminar el paciente"
        elif resultado[0] == 2:
            errores["pacienteNotFound"] = "Paciente no encontrado"
            print("Paciente ya eliminado")
        else:
            flash("Paciente eliminado correctamente")
            return redirect(url_for("medico.medico"))

    except Exception as e:
        errores["dbError"] = "Error al eliminar el paciente"
        print(f"Error: {e}")
    return render_template("Pacientes/EliminarExp.html", errores=errores, paciente=None)