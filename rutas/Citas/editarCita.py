from flask import Blueprint, render_template , request, flash
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from datetime import datetime

editarCita_bp = Blueprint('editarCita', __name__)
@editarCita_bp.route("/editarCita")
@login_required
def mostrarEditarCita():
    return render_template("Citas/EditarCita.html")

@editarCita_bp.route("/editarCita/continuar")
@login_required
def mostrarEditarCitaContinuar():
    return render_template("Citas/EditarCitaContinuar.html")