from flask import Blueprint, render_template , session
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from utility.generarPDF import generateDocument


consultarCita_bp = Blueprint('consultarCita', __name__)
#GET PRIMERA PARTE
@consultarCita_bp.route("/consultarCita/<id_cita>")
@login_required
def mostrarConsultarCita(id_cita):
    print('Ingresando a la consulta de la cita ------------------------------')
    errores = {}
    try:
        cita = execute_query("SELECT * FROM Citas WHERE ID_cita = (?) AND Estatus = (?)",(id_cita,1),fetch='one')
        print(f'Informacion de cita {cita}')
        if cita: 
            id_medico = cita.ID_medico
            id_paciente = cita.ID_paciente
            
            rfcMedico = execute_query("SELECT RFC FROM Medicos WHERE ID_medico = (?)", (id_medico,), fetch="one")
            cedulaMedico = execute_query("SELECT Cedula_profesional FROM Medicos WHERE ID_Medico = (?)", (id_medico,) fetch="one")
            nombreMedico = execute_query("SELECT CONCAT(Nombres, ' ',Apellido_paterno, ' ',Apellido_materno) FROM Medicos WHERE ID_medico = (?)",(id_medico,), fetch="one")
            correoMedico = execute_query("SELECT Correo_electronico FROM Medicos WHERE ID_medico = (?)", (id_medico,), fetch="one")
            nombrePaciente = execute_query("SELECT CONCAT(Nombres, ' ',Apellido_paterno, ' ',Apellido_materno) FROM Pacientes WHERE ID_paciente = (?)",(id_paciente,), fetch="one")
            edadPaciente = execute_query("SELECT Edad FROM Pacientes WHERE ID_paciente = (?)",(id_paciente,),fetch="one")
            rfcMedico = rfcMedico[0]
            cedulaMedico = cedulaMedico[0]
            nombreMedico = nombreMedico[0]
            correoMedico = correoMedico[0]
            nombrePaciente = nombrePaciente[0]
            edadPaciente = edadPaciente[0]

            print(f"Lo obtenido nombre med: {nombreMedico}, nombre pac: {nombrePaciente}, edad pac: {edadPaciente}")
            print(f"Lo tipo nombre med: {type(nombreMedico)}, nombre pac: {type(nombrePaciente)}, edad pac: {type(edadPaciente)}")

            if not nombrePaciente or not edadPaciente:
                print('Fallo al obtener nombre del paciente')
                errores['pacienteNotFound'] = "No se obtuvo un paciente"
            if not nombreMedico:
                print('Fallo al obtener nombre del med')
                errores['medicoNotFound'] ="No se obtuvo el medico"
            if errores:
                print(f'Hay errores: {errores}')
            else:
                print('Se empieza a agregar a la sesion -------------------')
                session['cita_temp'] = {
                "idCita": id_cita,
                "peso": cita[1],
                "altura": cita[2],
                "temperatura": cita[3],
                "latidos": cita[4],
                "oxigeno": cita[5],
                "glucosa": cita[6],
                "paciente": nombrePaciente,
                "edad": edadPaciente,
                "fecha": cita[10],
                'medico': nombreMedico,
                "rfc": rfcMedico,
                "cedula": cedulaMedico,
                "correo_electronico": correoMedico,
                'sintomas': cita[11],
                'diagnostico': cita[12],
                'tratamiento': cita[13],
                'estudios': cita[14]
                }
                print(f'Lo guardado en la sesion es: {session.get('cita_temp')}')
        else:
            print('Error al obtener datos de la cita')
            errores['citaNotFound'] = "Fallo al recuperar informacion de la cita"
    except Exception as e:
        print(f'Ocurrio el erro {str(e)}')
        errores['dbError'] = "Error durante la obtencion de la informacion de la cita" 
             
    return render_template("Citas/ConsultarCita.html", errores = errores)

def descargarPDF():
    session_data = session.get("cita_temp")
    generateDocument(session_data)