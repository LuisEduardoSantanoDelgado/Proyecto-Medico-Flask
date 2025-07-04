from flask import Blueprint, render_template , request, flash, session
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from datetime import datetime

agregarPaciente_bp = Blueprint('agregarPaciente', __name__)
@agregarPaciente_bp.route("/agregarPaciente")
@login_required
def mostrarAgregarPaciente():
    return render_template("Pacientes/AgregarExp.html")

@agregarPaciente_bp.route("/agregarPaciente", methods = ["POST"])
@login_required
def agregarPaciente():
    errores = {}
    try:
        nombres = request.form.get("nombres", "").strip()
        apellido_paterno = request.form.get("apellido_P", "").strip()
        apellido_materno = request.form.get("apellido_M", "").strip()
        fecha_nac = request.form.get("fecha_nacimiento", "").strip()
        alergias = request.form.get("alergias", "").strip()
        enfermedades_cronicas = request.form.get("enfermedades_cronicas", "").strip()
        antecedentes_familiares = request.form.get("antecedentes_familiares", "").strip()

        if not alergias :
            alergias = "Ninguna"
        if not enfermedades_cronicas:
            enfermedades_cronicas = "Ninguna"
        if not antecedentes_familiares:
            antecedentes_familiares = "Ninguna"
        
        if not nombres or not apellido_paterno or not apellido_materno or not fecha_nac:
            errores["emptyValues"] = "Valores vacíos"
            return render_template("Pacientes/AgregarExp.html", errores=errores)
        try:
            fecha_nacimiento = datetime.strptime(fecha_nac, '%Y-%m-%d').date()
        except ValueError:
                errores["fechaError"] = "Fecha de nacimiento inválida"
                return render_template("Pacientes/AgregarExp.html", errores=errores)
        else: 
            resultado = execute_query(
                "EXEC InsertarPaciente ?, ?, ?, ?, ?, ?, ?, ?",
                (nombres, apellido_paterno, apellido_materno, fecha_nacimiento, alergias, enfermedades_cronicas, antecedentes_familiares),
                fetch="one", commit=True
            )

            rfc = session.get("rfc")
            idMedico = execute_query("SELECT dbo.IDMedico(?)", (rfc,), fetch="one")
            idPaciente = execute_query("SELECT dbo.IDPaciente(?)", (nombres, apellido_paterno, apellido_materno, fecha_nacimiento), fetch="one")
            execute_query(
                "INSERT INTO Atiende (ID_paciente, ID_medico) VALUES (?, ?)",
                (idPaciente, idMedico),
                commit=True
            )
            
            if resultado and resultado.Resultado == 1:
                errores["pacienteExists"] = "El paciente ya está registrado"
                return render_template("Pacientes/AgregarExp.html", errores=errores)
            else:
                flash("Paciente agregado exitosamente")
                return render_template("VistasPrincipales/Medico.html", errores=errores)
    except Exception as e:
        errores["dbError"] = "Error al agregar paciente"
        print(f"Error: {e}")
    
    return render_template("Pacientes/AgregarExp.html", errores=errores)