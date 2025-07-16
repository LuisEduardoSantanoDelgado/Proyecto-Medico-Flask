from flask import Blueprint, render_template , request, flash, session, url_for, redirect
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from datetime import datetime

consultarCita_bp = Blueprint('consultarCita', __name__)
#GET PRIMERA PARTE
@consultarCita_bp.route("/consultarCita/<id_cita>")
@login_required
def mostrarConsultarCita(id_cita):
    errores = {}
    try:
        cita = execute_query("SELECT * FROM Citas WHERE ID_cita = (?) AND Estatus = (?)",(id_cita,1),fetch='one')
        print(f'Informacion de cita {cita}')
        if cita: 
            id_medico = cita.ID_medico
            id_paciente = cita.ID_paciente
            
            nombreMedico = execute_query("SELECT CONCAT(Nombres, ' ',Apellido_paterno, ' ',Apellido_materno) FROM Medicos WHERE ID_medico = (?)",(id_medico,), fetch="one")
            nombrePaciente = execute_query("SELECT CONCAT(Nombres, ' ',Apellido_paterno, ' ',Apellido_materno) FROM Pacientes WHERE ID_paciente = (?)",(id_paciente,), fetch="one")

            if not nombrePaciente:
                print('Fallo al obtener nombre del pacient')
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
                'medico': nombreMedico,
                "fecha": cita[10],
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
             
    render_template("ConsultarCita.html", errores = errores)