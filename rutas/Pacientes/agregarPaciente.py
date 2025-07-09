# Blueprints / imports originales…
from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from datetime import datetime

agregarPaciente_bp = Blueprint('agregarPaciente', __name__)


@agregarPaciente_bp.route("/agregarPaciente")
@login_required
def mostrarAgregarPaciente():
    print('Entrando a agregar pacientesss --------------------------------------------')
    return render_template("Pacientes/AgregarExp.html")


@agregarPaciente_bp.route("/agregarPaciente", methods=["POST"])
@login_required
def agregarPaciente():
    print('Comenzando a eviar paciente --------------------------------------------')
    errores = {}
    nombres = request.form.get("nombres", "").strip()
    apellido_paterno = request.form.get("apellido_P", "").strip()
    apellido_materno = request.form.get("apellido_M", "").strip()
    fecha_nac_txt = request.form.get("fecha_nacimiento", "").strip()   
    alergias = request.form.get("alergias", "").strip() or None
    enfermedades_cronicas = request.form.get("enfermedades_cronicas", "").strip() or None
    antecedentes_familiares= request.form.get("antecedentes_familiares", "").strip() or None

    print(f'Datos obtenidos: nombre: {nombres}, ap paterno: {apellido_paterno}, ap materno: {apellido_materno}, fecha de nac: {fecha_nac_txt}, alergias: {alergias},'+ 
          f'enfermedades: {enfermedades_cronicas}, antecedentes: {antecedentes_familiares}')
    
    print(f'Datos obtenidos tipo: nombre: {type(nombres)}, ap paterno: {type(apellido_paterno)}, ap materno: {type(apellido_materno)}, fecha de nac: {type(fecha_nac_txt)},' + 
          f'alergias: {type(alergias)}, enfermedades: {type(enfermedades_cronicas)}, antecedentes: {type(antecedentes_familiares)}')
    
    if not nombres or not apellido_paterno or not apellido_materno or not fecha_nac_txt:
        errores["emptyValues"] = "Todos los campos obligatorios deben llenarse."
    
    if not alergias or len(alergias) == 0:
        alergias = 'Ninguna'

    if not enfermedades_cronicas or len(enfermedades_cronicas) == 0:
        enfermedades_cronicas = 'Ninguna'

    if not antecedentes_familiares or len(antecedentes_familiares) == 0:
        antecedentes_familiares = 'Ninguno'

    if errores:
        print(f'Han ocurrido los errores: {errores}')
        return render_template("Pacientes/AgregarExp.html", errores=errores)

    else:
        try:
            datetime.strptime(fecha_nac_txt, "%Y-%m-%d")
        except ValueError:
            print('El formato de la fecha enviada del form esta erroneo')
            errores["fechaError"] = "Error en el formato de fecha"
            return render_template("Pacientes/AgregarExp.html", errores=errores)
        try:
            rfc = session.get("rfc")
            print(f'RFC del medico que atiende {rfc}')
            id_medico   = execute_query("SELECT dbo.IDMedico(?)", (rfc,), fetch="one")
            print(f'ID del medico {id_medico}')
            id_med = int(id_medico[0])
            print(f"ID formateado {type(id_med)} de {id_med}")
        except Exception as e:
            print("Error al obtener el ID del médico")
            errores["dbError"] = "Error al encontrar al médico que atiende"
            return render_template("Pacientes/AgregarExp.html", errores=errores)

        try:
            resultado = execute_query(
                "DECLARE @r INT; EXEC InsertarPaciente ?, ?, ?, ?, ?, ?, ?, ?, @r OUTPUT; SELECT @r AS Resultado; ",
                ( nombres, apellido_paterno, apellido_materno, fecha_nac_txt,alergias, enfermedades_cronicas, antecedentes_familiares, id_med),
                fetch="one", commit=True
            )
            if resultado:
                match resultado.Resultado:
                    case 1:
                        print('El paciente existe')
                        errores["pacienteExists"] = "El paciente ya está registrado."
                        return render_template("Pacientes/AgregarExp.html", errores=errores)
                    case -2:
                        print('Error al transformar la fecha')
                        errores["fechaError"] = "Formato de fecha inválido."
                        return render_template("Pacientes/AgregarExp.html", errores=errores)
                    case 3:
                        print('Error al asignar el paciente al medico')
                        errores["asignacionError"] = "Error al asignar el médico al paciente"
                        return render_template("Pacientes/AgregarExp.html", errores=errores)
                    case 0:
                        print('Se inserto el paciente')
                        flash("Paciente agregado exitosamente")
                        return redirect(url_for("medico.medico"))     
                    case _:
                        print("Error desconocido al agregar paciente")
                        errores["dbError"] = "Error desconocido al agregar paciente"
            else:
                print('Error al obtener el resultado de la consulta para insertar pac')
                errores["dbError"] = "No se pudo ejecutar la consulta."
                return render_template("Pacientes/AgregarExp.html", errores=errores)
        except Exception as e:
            print(f'Error durante la actualizacion {str(e)}')
            errores["dbError"] = "No se consiguió añadir el paciente"


    return render_template("Pacientes/AgregarExp.html", errores=errores)
