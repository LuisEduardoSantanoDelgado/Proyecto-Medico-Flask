from flask import Blueprint, render_template , session
from BDAyudas.QueryExecute import execute_query
from decorators.roleRequired import role_required


medicoAdmin_bp = Blueprint('medicoAdmin', __name__)
@medicoAdmin_bp.route("/medicoAdmin")
@role_required(2)
def medicoAdmin():
    errores = {}
    print("Accediendo a la lista de médicos --------------------------")
    try:
        rfc = session.get("rfc")
        print(f"RFC del médico: {rfc}")
        nombre = execute_query("SELECT dbo.NombreCompletoMedico(?)", (rfc,), fetch="one")
        print(f"Nombre del médico: {nombre} y tipo: {type(nombre)}")
        if not nombre:
            errores["medicoNotFound"] = "Nombre de médico no encontrado"
        else:
            nombreMedico = nombre[0]
               
        tblMedicos = execute_query(
            "SELECT CONCAT(Nombres, ' ', Apellido_paterno, ' ', Apellido_materno) AS Nombre_Medico, "
            "Cedula_profesional, RFC, Correo_electronico FROM Medicos WHERE Estatus = ? AND RFC != ?", 
            (1, rfc), fetch="all"
        )
        print(f"Tabla de médicos obtenida: {tblMedicos}")
        if not tblMedicos:
            errores["noMedicos"] = "No hay médicos registrados"

        if not errores:   
            print("No hay errores, mostrando la lista de médicos")
            for medico in tblMedicos:
                print(medico)  
            return render_template("VistasPrincipales/medicoAdmin.html", tblMedicos=tblMedicos, nombreMedico=nombreMedico)
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        nombreMedico = None
    
    return render_template("VistasPrincipales/medicoAdmin.html", errores=errores, tblMedicos=[], nombreMedico=None)

