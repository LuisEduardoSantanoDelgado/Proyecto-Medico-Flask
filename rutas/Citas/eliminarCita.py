from flask import Blueprint, render_template , request, flash
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from datetime import datetime

eliminarCita_bp = Blueprint('eliminarCita', __name__)
@eliminarCita_bp.route("/eliminarCita/<id_cita>")
@login_required
def mostrarEliminarCita(id_cita):
    return render_template("Citas/EliminarCita.html")