from flask import Blueprint, render_template ,  request, flash
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from utility.encriptarContrasena import encriptar_contrasena

agregarMedico_bp = Blueprint('agregarMedico', __name__)
@agregarMedico_bp.route("/agregarMedico")
@login_required(2) 
def mostrarAgregarMedico():
    return render_template("Medicos/AgregarMedico.html")
@agregarMedico_bp.route("/agregarMedico", methods = ["POST"])
@login_required(2)
def agregarMedico():
    errores = {}

    nombre = request.form.get("nombre", "").strip()
    apellido_paterno = request.form.get("apellido_P", "").strip()
    apellido_materno = request.form.get("apellido_M", "").strip()
    cedula = request.form.get("cedula", "").strip()
    rfc = request.form.get("rfc", "").strip()
    correo = request.form.get("correo", "").strip()
    passwordNE = request.form.get("password", "").strip()
    id_rol = request.form.get("rol", "0").strip()

    if not rfc or not nombre or not apellido_paterno or not apellido_materno or not passwordNE or not id_rol or not cedula:
        errores["emptyValues"] = "Valores vacíos"

    if len(rfc) != 13:
        errores["rfcLen"] = "El RFC debe tener 13 caracteres"
    
    if len(passwordNE) < 8:
        errores["passwordLen"] = "La contraseña debe tener al menos 8 caracteres"

    if len(cedula) < 7:
        errores["cedulaLen"] = "La cédula profesional debe tener al menos 7 caracteres"

    if not errores:
        try:
           
            hashed_bytes = encriptar_contrasena(passwordNE)

            resultado = execute_query(
                "DECLARE @res INT; EXEC InsertarMedico ?, ?, ?, ?, ?, ?, ?, ?, @res OUTPUT; SELECT @res AS Resultado",
                (nombre, apellido_paterno, apellido_materno, cedula, rfc, correo, hashed_bytes, id_rol),
                fetch="one", commit=True
            )

            if resultado and resultado.Resultado == 1:
                errores["rfcExists"] = "El RFC ya está registrado"
                return render_template("AgregarMedico.html", errores=errores)
            
            if resultado and resultado.Resultado == 2:
                errores["mailExists"] = "El correo ya está registrado"
                return render_template("AgregarMedico.html", errores=errores)
            
            flash("Médico agregado exitosamente")

        except Exception as e:
            errores["dbError"] = "Error al agregar médico"
            print(f"Error: {e}")

    return render_template("Medicos/AgregarMedico.html", errores = errores)