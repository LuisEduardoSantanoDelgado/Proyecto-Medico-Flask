from flask import Blueprint, render_template, request, flash, session
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from datetime import datetime

editarPaciente_bp = Blueprint('editarPaciente', __name__)


@editarPaciente_bp.route("/editarPaciente/<id_paciente>")
@login_required
def mostrarEditarPaciente(id_paciente):
    errores = {}
    try:
        rfc = session.get("rfc")
        print(f"Desde mostrarEditarPacient RFC del médico: {rfc}")
        nombreMedico = execute_query("SELECT dbo.NombreCompletoMedico(?)", (rfc,), fetch="one")
        paciente = execute_query("SELECT * FROM Pacientes WHERE ID_paciente = ?", (id_paciente,), fetch="one")
        print(f"Desde mostrarEditarPacientePaciente encontrado: {paciente} y nombreMedico: {nombreMedico}")

        if not paciente:
            errores["pacienteNotFound"] = "Paciente no encontrado"
        else:
            return render_template("Pacientes/EditarExp.html", paciente=paciente, errores=errores, nombreMedico=nombreMedico)
    except Exception as e:
        errores["dbError"] = "Error al obtener datos del paciente"
        print(f"Error: {e}")

    return render_template("Pacientes/EditarExp.html", errores=errores, paciente=None, nombreMedico="No disponible")


@editarPaciente_bp.route("/editarPaciente", methods=["POST"])
@login_required
def editarPaciente():
    errores = {}

    
    id_paciente = request.form.get("id_paciente", "").strip()
    nombre = request.form.get("nombre", "").strip()
    apellido_paterno = request.form.get("apellido_paterno", "").strip()
    apellido_materno = request.form.get("apellido_materno", "").strip()
    fecha_nac_txt = request.form.get("fecha_nacimiento", "").strip()
    alergias = request.form.get("alergias", "").strip() or None
    enfermedades = request.form.get("enfermedadesCronicas", "").strip() or None
    antecedentes = request.form.get("antecedentesFamiliares", "").strip() or None

    print(f"Desde editar pacientePost Datos recibidos: id_paciente={id_paciente}, nombre={nombre}, apellido_paterno={apellido_paterno}, "
          f"apellido_materno={apellido_materno}, fecha_nac_txt={fecha_nac_txt}, alergias={alergias}, "
          f"enfermedades={enfermedades}, antecedentes={antecedentes}")
    if not (id_paciente and nombre and apellido_paterno and apellido_materno and fecha_nac_txt):
        errores["emptyValues"] = "Todos los campos obligatorios deben llenarse."
        return render_template("Pacientes/EditarExp.html", errores=errores, paciente=None, nombreMedico="No disponible")

    try:
        datetime.strptime(fecha_nac_txt, "%Y-%m-%d")
    except ValueError:
        errores["fechaError"] = "Formato de fecha inválido (esperado: AAAA-MM-DD)"
        return render_template("Pacientes/EditarExp.html", errores=errores, paciente=None, nombreMedico="No disponible")

    
    resultado = execute_query("""
        DECLARE @res INT;
        EXEC ActualizarPaciente ?, ?, ?, ?, ?, ?, ?, ?, @res OUTPUT;
        SELECT @res;
    """, (
        id_paciente,
        nombre,
        apellido_paterno,
        apellido_materno,
        fecha_nac_txt,  
        alergias,
        enfermedades,
        antecedentes
    ), fetch="one", commit=True)
    print(f"Desde editarPaciente Resultado de la consulta de edicion: {resultado}")
    if resultado is None:
        errores["updateError"] = "No se pudo ejecutar la consulta"
        return render_template("Pacientes/EditarExp.html", errores=errores, paciente=None, nombreMedico="No disponible")

    codigo = resultado[0]
    if codigo == 1:
        errores["pacienteNotFound"] = "El paciente no existe."
    elif codigo == -2:
        errores["fechaError"] = "Fecha inválida al procesar en la base de datos."
    elif codigo == 0:
        flash("Paciente actualizado correctamente")
        return mostrarEditarPaciente(id_paciente)
    else:
        errores["updateError"] = "Error desconocido al actualizar el paciente."

    return render_template("Pacientes/EditarExp.html", errores=errores, paciente=None, nombreMedico="No disponible")
