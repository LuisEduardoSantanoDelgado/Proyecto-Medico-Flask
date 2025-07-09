from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from datetime import datetime

editarPaciente_bp = Blueprint('editarPaciente', __name__)


@editarPaciente_bp.route("/editarPaciente/<id_paciente>")
@login_required
def mostrarEditarPaciente(id_paciente):
    print('Entrando a editar paciente ------------------------------')
    errores = {}
    try:
        rfc = session.get("rfc")
        print(f"Desde mostrarEditarPacient RFC del médico: {rfc}")
        nombreMedico = execute_query("SELECT dbo.NombreCompletoMedico(?)", (rfc,), fetch="one")
        paciente = execute_query("SELECT * FROM Pacientes WHERE ID_paciente = ?", (id_paciente,), fetch="one")
        print(f"Desde mostrarEditarPacientePaciente encontrado: {paciente} y nombreMedico: {nombreMedico}")

        if not paciente and nombreMedico:
            print('Fallo en obtener el paciente')
            errores["pacienteNotFound"] = "Paciente no encontrado"
            return render_template("Pacientes/EditarExp.html", paciente=None, errores=errores, nombreMedico=nombreMedico)
        elif paciente and not nombreMedico:
            print('Fallo en obtener el nombre del medico')
            errores["medicoNotFound"] = "Paciente no encontrado"
            return render_template("Pacientes/EditarExp.html", paciente=paciente, errores=errores, nombreMedico="No disponible")
        else:
            return render_template("Pacientes/EditarExp.html", paciente=paciente, errores=errores, nombreMedico=nombreMedico)
    except Exception as e:
        errores["dbError"] = "Error al obtener datos del paciente y del médico"
        print(f"Error en mostrar editar paciente: {str(e)}")

    return render_template("Pacientes/EditarExp.html", errores=errores, paciente=None, nombreMedico="No disponible")


@editarPaciente_bp.route("/editarPaciente", methods=["POST"])
@login_required
def editarPaciente():
    print('Entrando a enviar editar paciente -------------------------------------------')
    errores = {}
    id_paciente = request.form.get("id_paciente", "").strip()
    nombres = request.form.get("nombre", "").strip()
    apellido_paterno = request.form.get("apellido_paterno", "").strip()
    apellido_materno = request.form.get("apellido_materno", "").strip()
    fecha_nac_txt = request.form.get("fecha_nacimiento", "").strip()
    alergias = request.form.get("alergias", "").strip() or None
    enfermedades = request.form.get("enfermedadesCronicas", "").strip() or None
    antecedentes = request.form.get("antecedentesFamiliares", "").strip() or None

    print(f"Desde editar pacientePost Datos recibidos: id_paciente={id_paciente}, nombre={nombres}, apellido_paterno={apellido_paterno}, "
          f"apellido_materno={apellido_materno}, fecha_nac_txt={fecha_nac_txt}, alergias={alergias}, "
          f"enfermedades={enfermedades}, antecedentes={antecedentes}")
    
    print(f'Datos obtenidos tipo: nombre: {type(nombres)}, ap paterno: {type(apellido_paterno)}, ap materno: {type(apellido_materno)}, fecha de nac: {type(fecha_nac_txt)},' + 
          f'alergias: {type(alergias)}, enfermedades: {type(enfermedades)}, antecedentes: {type(antecedentes)}')
    
    if not nombres or not apellido_paterno or not apellido_materno or not fecha_nac_txt:
        errores["emptyValues"] = "Todos los campos obligatorios deben llenarse."
    
    if not alergias:
        alergias = 'Ninguna'

    if not enfermedades or len(enfermedades) == 0:
        enfermedades = 'Ninguna'

    if not antecedentes or len(antecedentes) == 0:
        antecedentes = 'Ninguno'

    if errores:
        print('Han ocurrido los errores {errores}')
        return render_template("Pacientes/EditarExp.html", errores=errores, paciente=None, nombreMedico="No disponible")
    else:
        try:
            datetime.strptime(fecha_nac_txt, "%Y-%m-%d")
        except ValueError:
            print('El formato de la fecha enviada del form esta erroneo')
            errores["fechaError"] = "Formato de fecha inválido (esperado: AAAA-MM-DD)"
            return render_template("Pacientes/EditarExp.html", errores=errores, paciente=None, nombreMedico="No disponible")
    try:
        resultado = execute_query(
            " DECLARE @res INT; EXEC ActualizarPaciente ?, ?, ?, ?, ?, ?, ?, ?, @res OUTPUT; SELECT @res AS Resultado; ", 
            ( id_paciente, nombres, apellido_paterno, apellido_materno, fecha_nac_txt, alergias, enfermedades, antecedentes ), 
            fetch="one", commit=True
        )
        print(f"Desde editarPaciente Resultado de la consulta de edicion: {resultado}")
        if resultado:
            match resultado.Resultado:
                case 1:
                    print('El paciente no existe')
                    errores["pacienteNotFound"] = "Error al encontrar el paciente en la base de datos"
                    return render_template("Pacientes/EditarExp.html", errores=errores, paciente=None, nombreMedico="No disponible")
                case 2:
                    print('Error al convertir la fecha desde la base de datos')
                    errores["fechaError"] = "Fecha inválida al procesar en la base de datos."
                    return render_template("Pacientes/EditarExp.html", errores=errores, paciente=None, nombreMedico="No disponible")
                case 0:
                    print('Se actualizo el paciente')
                    flash("Paciente actualizado exitosamente")
                    return redirect(url_for("medico.medico"))
                case _:
                    print('Error desconocido desde la base de datos')
                    errores["updateError"] = "Error desconocido al actualizar el paciente."
        else:
            print('Error al obtener el resultado de actualizar paciente')
            errores["updateError"] = "No se pudo ejecutar la consulta"
            return render_template("Pacientes/EditarExp.html", errores=errores, paciente=None, nombreMedico="No disponible")
    except Exception as e:
        print(f'Error durante la actualizacion {str(e)}')
        errores["dbError"] = "Fallo la actualización del paciente"

    return render_template("Pacientes/EditarExp.html", errores=errores, paciente=None, nombreMedico="No disponible")
