from flask import Blueprint, render_template , session
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required

citasLista_bp = Blueprint('citasLista', __name__)
@citasLista_bp.route("/citasLista")

@login_required
def citasLista():
    print('Entrando a la lista de citas')
    errores = {}
    rfc = session.get("rfc")
    try:
        id_medico   = execute_query("SELECT dbo.IDMedico(?)", (rfc,), fetch="one")
        print(f'ID medico llegado: {id_medico}')
        if id_medico:
            idMedico = id_medico[0]
            tblCitas = execute_query(" SELECT Citas.ID_cita, CONCAT(Pacientes.Nombres, ' ', Pacientes.Apellido_paterno, ' ', Pacientes.Apellido_materno) AS Nombre_Paciente FROM Citas JOIN Pacientes ON Citas.ID_paciente = Pacientes.ID_paciente WHERE Citas.ID_medico = (?) AND Citas.Estatus = (?)",(idMedico,1), fetch="all")
            # tblCitas = execute_query("SELECT * FROM Citas WHRERE ID_medico = (?) and Estatus = (?)",(idMedico,1), fetch="all")
            print(f'Tabla de citas: {tblCitas}')
            if not tblCitas or len(tblCitas) == 0:
                print('No hay citas')
                errores["citasNotFound"] = "No se encontraron citas para mostrar"
            else:
                print('Enviando tabla de citas---->')
                return render_template('VistasPrincipales/citasLista.html', tblCitas = tblCitas, errores = errores)
        else:
            print('No llego un ID de medico')
            errores['medicoNotFound'] = "No se  hayo a un médico"
    except Exception as e:
        print(f'Error durante obtencion de lista de citas: {str(e)}')
        errores['dbError'] = "Error durante obtencion de lista de citas"

    return render_template("VistasPrincipales/CitasLista.html", errores = errores, tblCitas = [])