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
        print(f" Desde medico RFC del médico: {rfc}")
        idMedico = execute_query("SELECT dbo.IDMedico(?)", (rfc,), fetch="one")
        print(f"Desde medico ID del médico: {idMedico}")
        nombre = execute_query("SELECT dbo.NombreCompletoMedico(?)", (rfc,), fetch="one")
        print(f"Desde medico Nombre del médico: {nombre}")
        if not nombre:
            errores["medicoNotFound"] = "Médico no encontrado"
        else:
            nombreMedico = nombre[0]
            tblPacientes = execute_query("EXEC obtenerPacientes @ID_medico = ?", (idMedico[0],), fetch="all")
            print(f"Desde medico Pacientes del médico: {tblPacientes}")
            if not tblPacientes:
                errores["pacientesNotFound"] = "No se encontraron pacientes"
            else:
                print(f"Desde medico esto se envia a la vista: {tblPacientes} y {nombreMedico}")
                rol = session.get("rol")
                print(f"Desde medico Rol del médico: {rol}")
                return render_template("VistasPrincipales/Medico.html", nombreMedico=nombreMedico, tblPacientes=tblPacientes, rol=rol)
    except Exception as e:
        errores["DBError"] = "Error al obtener los datos de los pacientes"
        print(f"Error: {e}")
    if nombreMedico and not tblPacientes:
        return render_template("VistasPrincipales/Medico.html", errores=errores, nombreMedico=nombreMedico, tblPacientes=[], rol=session.get("rol"))
    return render_template("VistasPrincipales/Medico.html", errores=errores, nombreMedico=[], tblPacientes=[], rol=session.get("rol"))