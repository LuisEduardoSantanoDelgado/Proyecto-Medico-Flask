from flask import Blueprint, render_template , session
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required


medicoAdmin_bp = Blueprint('medicoAdmin', __name__)
@medicoAdmin_bp.route("/medicoAdmin")
@login_required(2)
def medicoAdmin():
    errores = {}
    try:
        rfc = session.get("rfc")
       
        nombre = execute_query("SELECT dbo.NombreCompletoMedico(?)", (rfc,), fetch="one")
        if not nombre:
            errores["medicoNotFound"] = "Médico no encontrado"
        else:
            nombreMedico = nombre[0]
               
        tblMedicos = execute_query(
            "SELECT CONCAT(Nombres, ' ', Apellido_paterno, ' ', Apellido_materno) AS Nombre_Medico, "
            "Cedula_profesional, RFC, Correo_electronico FROM Medicos WHERE Estatus = ?", 
            (1,), fetch="all"
        )
        if not tblMedicos:
            errores["noMedicos"] = "No hay médicos registrados"

        if not errores:   
            print(nombreMedico)
            for medico in tblMedicos:
                print(medico)  # Para ver cómo se ve la fila completa
            return render_template("VistasPrincipales/medicoAdmin.html", tblMedicos=tblMedicos, nombreMedico=nombreMedico)
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        nombreMedico = None
    
    return render_template("VistasPrincipales/medicoAdmin.html", errores=errores)

