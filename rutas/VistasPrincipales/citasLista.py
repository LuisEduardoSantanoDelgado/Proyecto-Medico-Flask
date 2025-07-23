from flask import Blueprint, render_template, request, session
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required

citasLista_bp = Blueprint('citasLista', __name__)

@citasLista_bp.route("/citasLista", methods=["GET", "POST"])
@login_required
def citasLista():
    print('Entrando a la lista de citas ----------------------------')
    errores = {}
    filtro = request.form.get('filtro')
    busqueda = request.form.get('busqueda')
    rfc = session.get("rfc")
    
    try:
        id_medico = execute_query("SELECT dbo.IDMedico(?)", (rfc,), fetch="one")
        print(f'ID medico llegado: {id_medico}')
        
        if id_medico:
            idMedico = id_medico[0]
            
            if filtro == "Nombre":
                query = "SELECT Citas.ID_cita, CONCAT(Pacientes.Nombres, ' ', Pacientes.Apellido_paterno, ' ', Pacientes.Apellido_materno) AS Nombre_Paciente FROM Citas JOIN Pacientes ON Citas.ID_paciente = Pacientes.ID_paciente WHERE Citas.ID_medico = (?) AND Citas.Estatus = (?) AND CONCAT(Pacientes.Nombres, ' ', Pacientes.Apellido_paterno, ' ', Pacientes.Apellido_materno) LIKE ?"
                tblCitas = execute_query(query, (idMedico, 1, '%' + busqueda + '%'), fetch="all")
            elif filtro == "Fecha":
                query = "SELECT Citas.ID_cita, CONCAT(Pacientes.Nombres, ' ', Pacientes.Apellido_paterno, ' ', Pacientes.Apellido_materno) AS Nombre_Paciente FROM Citas JOIN Pacientes ON Citas.ID_paciente = Pacientes.ID_paciente WHERE Citas.ID_medico = (?) AND Citas.Estatus = (?) AND Citas.Fecha LIKE ?"
                tblCitas = execute_query(query, (idMedico, 1, '%' + busqueda + '%'), fetch="all")
            else:
                query = "SELECT Citas.ID_cita, CONCAT(Pacientes.Nombres, ' ', Pacientes.Apellido_paterno, ' ', Pacientes.Apellido_materno) AS Nombre_Paciente FROM Citas JOIN Pacientes ON Citas.ID_paciente = Pacientes.ID_paciente WHERE Citas.ID_medico = (?) AND Citas.Estatus = (?)"
                tblCitas = execute_query(query, (idMedico, 1), fetch="all")
            
            if not tblCitas or len(tblCitas) == 0:
                errores["citasNotFound"] = "No se encontraron citas para mostrar"
        else:
            errores['medicoNotFound'] = "No se encontró un médico"
    
    except Exception as e:
        print(f'Error durante obtención de lista de citas: {str(e)}')
        errores['dbError'] = "Error durante obtención de lista de citas"

    return render_template("VistasPrincipales/citasLista.html", errores=errores, tblCitas=tblCitas)
