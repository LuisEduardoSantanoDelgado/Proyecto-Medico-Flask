from flask import Blueprint, render_template , session
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required

citasLista_bp = Blueprint('citasLista', __name__)
@citasLista_bp.route("/citasLista")

@login_required
def citasLista():
    return render_template("VistasPrincipales/CitasLista.html")