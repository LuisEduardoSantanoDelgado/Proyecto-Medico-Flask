from flask import Blueprint, render_template, request, session
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required

medico_bp = Blueprint('medico', __name__)

@medico_bp.route("/medico", methods=["GET", "POST"])
@login_required
def medico():
    errores = {}
    filtro = request.form.get('filtro')
    busqueda = request.form.get('busqueda')
    
    try:
        rfc = session.get("rfc")
        idMedico = execute_query("SELECT dbo.IDMedico(?)", (rfc,), fetch="one")
        nombre = execute_query("SELECT dbo.NombreCompletoMedico(?)", (rfc,), fetch="one")
        
        if not nombre:
            errores["medicoNotFound"] = "Médico no encontrado"
        else:
            nombreMedico = nombre[0]
            
            if filtro == "Nombre":
                query = "EXEC obtenerPacientesPorNombre @ID_medico = ?, @nombre = ?"
                tblPacientes = execute_query(query, (idMedico[0], busqueda), fetch="all")
            elif filtro == "Estado":
                query = "EXEC obtenerPacientesPorEstado @ID_medico = ?, @estado = ?"
                tblPacientes = execute_query(query, (idMedico[0], busqueda), fetch="all")
            elif filtro == "Fecha":
                query = "EXEC obtenerPacientesPorFecha @ID_medico = ?, @fecha = ?"
                tblPacientes = execute_query(query, (idMedico[0], busqueda), fetch="all")
            else:
                tblPacientes = []

            if not tblPacientes:
                errores["pacientesNotFound"] = "No se encontraron pacientes con los filtros seleccionados"

        return render_template("VistasPrincipales/Medico.html", nombreMedico=nombreMedico, tblPacientes=tblPacientes, errores=errores)

    except Exception as e:
        errores["DBError"] = "Error al obtener los datos de los pacientes"
        return render_template("VistasPrincipales/Medico.html", errores=errores, tblPacientes=[])

    return render_template("VistasPrincipales/Medico.html", errores=errores, nombreMedico=[], tblPacientes=[])
