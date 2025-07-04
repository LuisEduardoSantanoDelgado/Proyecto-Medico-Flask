# Blueprints / imports originales…
from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from datetime import datetime

agregarPaciente_bp = Blueprint('agregarPaciente', __name__)

# ---------- GET (formulario) ----------
@agregarPaciente_bp.route("/agregarPaciente")
@login_required
def mostrarAgregarPaciente():
    return render_template("Pacientes/AgregarExp.html")

# ---------- POST (envío del formulario) ----------
@agregarPaciente_bp.route("/agregarPaciente", methods=["POST"])
@login_required
def agregarPaciente():
    errores = {}

    # 1. Leer y limpiar datos -----------------------
    nombres                = request.form.get("nombres", "").strip()
    apellido_paterno       = request.form.get("apellido_P", "").strip()
    apellido_materno       = request.form.get("apellido_M", "").strip()
    fecha_nac_txt          = request.form.get("fecha_nacimiento", "").strip()   # «yyyy-mm-dd»
    alergias               = request.form.get("alergias", "").strip() or None
    enfermedades_cronicas  = request.form.get("enfermedades_cronicas", "").strip() or None
    antecedentes_familiares= request.form.get("antecedentes_familiares", "").strip() or None

    # 2. Validaciones básicas -----------------------
    if not (nombres and apellido_paterno and apellido_materno and fecha_nac_txt):
        errores["emptyValues"] = "Todos los campos obligatorios deben llenarse."
        return render_template("Pacientes/AgregarExp.html", errores=errores)

    # Validar formato de fecha (solo formato, no conversión a date)
    try:
        datetime.strptime(fecha_nac_txt, "%Y-%m-%d")
    except ValueError:
        errores["fechaError"] = "La fecha debe tener formato AAAA-MM-DD."
        return render_template("Pacientes/AgregarExp.html", errores=errores)

    # 3. Ejecutar el procedimiento almacenado -------
    resultado = execute_query(
        """
        DECLARE @r INT;
        EXEC InsertarPaciente
             ?, ?, ?, ?, ?, ?, ?, @r OUTPUT;
        SELECT @r AS Resultado;
        """,
        (
            nombres,
            apellido_paterno,
            apellido_materno,
            fecha_nac_txt,               # se envía como VARCHAR(10)
            alergias,
            enfermedades_cronicas,
            antecedentes_familiares
        ),
        fetch="one",
        commit=True
    )

    if resultado is None:
        errores["dbError"] = "No se pudo ejecutar la consulta."
        return render_template("Pacientes/AgregarExp.html", errores=errores)

    codigo = resultado[0]
    if codigo == 1:          # duplicado
        errores["pacienteExists"] = "El paciente ya está registrado."
        return render_template("Pacientes/AgregarExp.html", errores=errores)
    elif codigo == -2:       # fecha inválida (por si el SP hace otra validación)
        errores["fechaError"] = "Formato de fecha inválido."
        return render_template("Pacientes/AgregarExp.html", errores=errores)

    # 4. Relacionar paciente con médico -------------
    try:
        rfc = session.get("rfc")
        id_medico   = execute_query("SELECT dbo.IDMedico(?)",
                                    (rfc,), fetch="one")
        id_paciente = execute_query("SELECT dbo.IDPaciente(?, ?, ?, ?)",
                                    (nombres, apellido_paterno,
                                     apellido_materno, fecha_nac_txt),
                                    fetch="one")
        print(f"ID Médico: {id_medico}, ID Paciente: {id_paciente}")
        print(f"ID Médico: {type(id_medico)}, ID Paciente: {type(id_paciente)}")
        id_med = int(id_medico[0])
        id_pac = int(id_paciente[0])
        print(f"ID Médico: {type(id_med)}, ID Paciente: {type(id_pac)}")
        execute_query("INSERT INTO Atiende(ID_paciente, ID_medico) VALUES (?, ?)",
                      (id_pac, id_med), fetch=None,  
                      commit=True)
    except Exception as e:
        # No detiene la inserción del paciente; solo reporta
        errores["asignacion"] = "Paciente creado, pero no se pudo asignar al médico."
        print("Error al asignar paciente–médico:", e)

    # 5. Éxito -------------------------------------
    flash("Paciente agregado exitosamente.")
    return redirect(url_for("medico.medico"))  # ajusta al nombre real de tu ruta
