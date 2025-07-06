from flask import Blueprint, render_template , request, flash
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from datetime import datetime

agregarCita_bp = Blueprint('agregarCita', __name__)
@agregarCita_bp.route("/agregarCita")
@login_required
def mostrarAgregarCita():
    return render_template("Citas/AgregarCita.html")

@agregarCita_bp.route("/agregarCita/continuar")
@login_required
def mostrarAgregarCitaContinuar():
    return render_template("Citas/AgregarCitaContinuar.html")
#ESTA INCOMPLETO, FALTA AGREGAR LA LOGICA PARA AGREGAR UNA CITA 