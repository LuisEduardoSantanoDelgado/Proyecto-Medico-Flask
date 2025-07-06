from flask import Blueprint, render_template , request, flash
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from datetime import datetime

eliminarCita_bp = Blueprint('eliminarCita', __name__)
@eliminarCita_bp.route("/eliminarCita")
@login_required
def mostrarEliminarCita():
    return render_template("Citas/EliminarCita.html")