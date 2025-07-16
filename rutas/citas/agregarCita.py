from flask import Blueprint, render_template , request, flash, session
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from datetime import datetime

agregarCita_bp = Blueprint('agregarCita', __name__)
@agregarCita_bp.route("/agregarCita/<id_paciente>")
@login_required
def mostrarAgregarCita(id_paciente):
    errores={}
    print('Entrando a agregar cita -------------------------------')
    print(f'ID de paciente: {id_paciente} tipo: {type(id_paciente)}')
    try:
        if not id_paciente:
            print(f"Campo vacio id paciente: {id_paciente}")
            errores["dbError"] = "Error al obtener datos."
        else:
            nombrePaciente = execute_query("SELECT CONCAT(Nombres, ' ', Apellido_paterno, ' ', Apellido_materno) FROM Pacientes WHERE ID_pacientes = (?)", id_paciente, fetch="one")

            return render_template('Citas/AgregarCita.html', nombrePaciente = nombrePaciente, paciente = id_paciente)
    except Exception as e:
        print(f'Ha ocurrido un error al intentar obtener datos del medico o del paciente: {str(e)}')
        errores["dbError"] = "Error durante la obtencion de datos"
        
    return render_template("Citas/AgregarCita.html")

@agregarCita_bp.route("/agregarCita/continuar")
@login_required
def mostrarAgregarCitaContinuar():
    return render_template("Citas/AgregarCitaContinuar.html")
#ESTA INCOMPLETO, FALTA AGREGAR LA LOGICA PARA AGREGAR UNA CITA 