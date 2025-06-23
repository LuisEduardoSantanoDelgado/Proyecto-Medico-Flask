from flask import Blueprint, render_template ,  request, flash
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from utility.encriptarContrasena import encriptar_contrasena

editarMedico_bp = Blueprint('editarMedico', __name__)

@editarMedico_bp.route("/editar_medico/<rfc>", methods=["GET"])
@login_required(2) 
def mostrarEditarMedico(rfc):
    errores = {}
    try:
        medico = execute_query("SELECT dbo.DatosMedico(?) ", (rfc,), fetch="one")
        if not medico:
            errores["medicoNotFound"] = "Médico no encontrado"
        else:
            return render_template("Medicos/EditarMedico.html", medico=medico)
    except Exception as e:
        errores["dbError"] = "Error al obtener datos del médico"
        print(f"Error: {e}")

    return render_template("Medicos/EditarMedico.html", errores=errores)

@editarMedico_bp.route("/editar_medico", methods=["POST"])
@login_required(2)
def editarMedico():
    errores = {}
    try:
        # conn = getConnection(2)
        # cursor = conn.cursor()
        # cursor.execute("SELECT * FROM Medicos WHERE RFC = ?", rfc)
        # medico = cursor.fetchone()
        

        if not medico:
            errores["medicoNotFound"] = "Médico no encontrado"
            return render_template("EditarMedico.html", errores=errores)

        return render_template("EditarMedico.html", medico=medico)

    except Exception as e:
        errores["dbError"] = "Error al obtener datos del médico"
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template("EditarMedico.html", errores=errores)