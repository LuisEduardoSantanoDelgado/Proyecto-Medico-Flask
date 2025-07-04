from flask import Blueprint, render_template ,  request, flash
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required

editarPaciente_bp = Blueprint('editarPaciente', __name__)
@editarPaciente_bp.route("/editarPaciente")
@login_required
def mostrarEditarPaciente(id_paciente):
    errores = {}
    try:
        paciente = execute_query("SELECT * FROM Pacientes WHERE ID_paciente = ?", (id_paciente,), fetch="one")
        if not paciente:
            errores["pacienteNotFound"] = "Paciente no encontrado"
        else:
            return render_template("Pacientes/EditarExp.html", paciente=paciente, errores=errores)
    except Exception as e:
        errores["dbError"] = "Error al obtener datos del paciente"
        print(f"Error: {e}")

    return render_template("Pacientes/EditarExp.html", errores=errores, paciente=[])


@editarPaciente_bp.route("/editarPaciente", methods = ["POST"])
@login_required
def editarPaciente():
    errores = {}
    try:
        id_paciente = request.form.get("id_paciente", "").strip()
        nombre = request.form.get("nombre", "").strip()
        apellido_paterno = request.form.get("apellido_P", "").strip()
        apellido_materno = request.form.get("apellido_M", "").strip()
        fecha_nacimiento = request.form.get("fecha_nacimiento", "").strip()
        alegias = request.form.get("alegias", "").strip()
        enfermedadesCronicas = request.form.get("enfermedadesCronicas", "").strip()
        antecedentesFamiliares = request.form.get("antecedentesFamiliares", "").strip()

        if not alegias:
            alegias = "Ninguna"
        if not enfermedadesCronicas:
            enfermedadesCronicas = "Ninguna"   
        if not antecedentesFamiliares:
            antecedentesFamiliares = "Ninguna"

        if not id_paciente or not nombre or not apellido_paterno or not apellido_materno or not fecha_nacimiento :
            errores["emptyValues"] = "Valores vacíos"

        resultado = execute_query(
            "EXEC ActualizarPaciente ?, ?, ?, ?, ?, ?, ?, ?",
            (id_paciente,nombre, apellido_paterno, apellido_materno, fecha_nacimiento, alegias, enfermedadesCronicas, antecedentesFamiliares),
            fetch="one", commit=True
        )

        if resultado is None:
            errores["updateError"] = "Error al actualizar el paciente"
        else:
            flash("Paciente actualizado correctamente")
            return mostrarEditarPaciente(id_paciente)

    except Exception as e:
        errores["dbError"] = "Error al actualizar el paciente"
        print(f"Error: {e}")
    return render_template("Pacientes/EditarExp.html", errores=errores, paciente=[])