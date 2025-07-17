from flask import Blueprint, render_template , request, flash, redirect, url_for
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from datetime import datetime

eliminarCita_bp = Blueprint('eliminarCita', __name__)
@eliminarCita_bp.route("/eliminarCita/<id_cita>")
@login_required
def mostrarEliminarCita(id_cita):
    print('Mostrando eliminar cita ------------------------------------------')
    errores = {}
    try:
        cita = execute_query("SELECT * FROM Citas WHERE ID_cita = (?)",(id_cita,), fetch='one')
        print(f' La cita con id {id_cita} es: {cita}')
        if cita:
            nombrePaciente = execute_query("SELECT CONCAT(Nombres, ' ',Apellido_paterno,' ',Apellido_materno) FROM Pacientes WHERE ID_paciente = (?)",(cita[8],), fetch="one")
            print(f'Nombre paciente: {nombrePaciente}')
            if nombrePaciente:
                nombrePaciente = nombrePaciente[0]
                return render_template("Citas/EliminarCita.html", errores = errores, nombrePaciente = nombrePaciente, cita = cita)
            else:
                print('Nombre paciente vacia')
                errores['pacienteNotFound'] = "Error al encontrar el paciente"

        else:
            print('Cita vacia')
            errores['citaNotFound'] = "Error al encontrar la cita"
    except Exception as e:
        print(f'Error al ejecutar {str(e)}')
        errores['dbError'] = "Error al eliminar la cita"
    return render_template("Citas/EliminarCita.html", errores = errores, nombrePaciente = None, cita = None)

@eliminarCita_bp.route("/eliminarCita",methods=["POST"])
@login_required
def eliminarCita():
    errores = {}
    print('Eliminando cita---------------------------')
    id_cita = request.form.get("id_cita", "").strip()
    
    print(f"ID obtenido {id_cita}")

    if id_cita:
        try:
            execute_query("UPDATE Citas SET Estatus = 0 WHERE ID_cita = (?) and Estatus = 1", (id_cita,), fetch=None, commit=True)
            flash('Cita eliminada con éxito')
            return redirect(url_for('citasLista.citasLista'))
        except Exception as e:
            print('Ocurrio el error al intentar eliminar {str(e)}')
            errores['dbError'] = "Error al eliminar reintente"
    else:
        print('No hay id de cita')
        errores['dbError'] = "No se encontro la cita a eliminar"
    
    return render_template("Citas/EliminarCita.html", errores = errores, nombrePaciente = None, cita = None)