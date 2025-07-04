from flask import Blueprint, render_template , request, flash
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from datetime import datetime

agregarCita_bp = Blueprint('agregarCita', __name__)
@agregarCita_bp.route("/agregarCita/<id_paciente>")
@login_required
def mostrarAgregarCita(id_paciente):
    errores = {}
    try:
        nombrePaciente = execute_query("EXEC obtenerNombrePaciente @ID_paciente = ?", (id_paciente,), fetch="one")
        if not nombrePaciente:
            errores["pacienteNotFound"] = "Paciente no encontrado"
        else:
            return render_template("Citas/AgregarCita.html", id_paciente=id_paciente, nombrePaciente=nombrePaciente[0], errores=errores)
    except Exception as e:
        errores["DBError"] = "Error al obtener los datos del paciente"
        print(f"Error: {e}")
    
    return render_template("Citas/AgregarCita.html", id_paciente=id_paciente, nombrePaciente="", errores=errores)


@agregarCita_bp.route("/agregarCita", methods = ["POST"])
@login_required
def agregarCita():
    
    return mostrarAgregarCita(request.form.get("id_paciente", "").strip())



#ESTA INCOMPLETO, FALTA AGREGAR LA LOGICA PARA AGREGAR UNA CITA PTM