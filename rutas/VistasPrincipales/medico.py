from flask import Blueprint, render_template , session
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required

medico_bp = Blueprint('medico', __name__)
@medico_bp.route("/medico")

@login_required
def medico():
    errores = {}
    try:
        rfc = session.get("rfc")
        idMedico = execute_query("SELECT dbo.IDMedico(?)", (rfc,), fetch="one")
        nombre = execute_query("EXEC obtenerPacientes @ID_medico = ?", (idMedico,), fetch="one")
        if not nombre:
            errores["medicoNotFound"] = "Médico no encontrado"
        else:
            nombreMedico = nombre[0]
            tblPacientes = execute_query("EXEC obtenerPacientes @ID_medico = ?", (idMedico,), fetch="all")
            if not tblPacientes:
                errores["pacientesNotFound"] = "No se encontraron pacientes"
            else:
                return render_template("VistasPrincipales/Medico.html", nombreMedico=nombreMedico, tblPacientes=tblPacientes)
    except Exception as e:
        errores["DBError"] = "Error al obtener los datos de los pacientes"
        print(f"Error: {e}")
    
    return render_template("VistasPrincipales/Medico.html", errores=errores, nombreMedico=[], tblPacientes=[])