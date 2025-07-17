from flask import Blueprint, render_template , request, flash
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from datetime import datetime

eliminarCita_bp = Blueprint('eliminarCita', __name__)
@eliminarCita_bp.route("/eliminarCita/<id_cita>")
@login_required
def mostrarEliminarCita(id_cita):
    errores = {}
    try:
        cita = execute_query("SELECT * FROM Citas WHERE ID_cita = (?)",(id_cita,), fetch='one')
        print(f' La cita con id {id_cita} es: {cita}')
        if cita:
            nombreCita = f""
        else:
            print('Cita vacia')
            errores['citaNotFound'] = "Error al encontrar la cita"
    except Exception as e:
        print(f'Error al ejecutar {str(e)}')
        errores['dbError'] = "Error al eliminar la cita"
    return render_template("Citas/EliminarCita.html", errores = errores)