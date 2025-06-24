from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from BDAyudas.QueryExecute import execute_query
from utility.encriptarContrasena import verificar_contrasena

login_bp = Blueprint('login', __name__)

@login_bp.route("/")
def home():
    return render_template("login.html")

@login_bp.route("/login", methods=["POST"])
def login():
    errores = {}
    rfc = request.form.get("rfc", "").strip()
    password = request.form.get("password", "").strip()

    if not rfc or not password:
        errores["emptyValues"] = "RFC o contraseña vacíos"

    if not errores:
        try:
            result = execute_query("EXEC Obtener_Contrasena ?", (rfc,), fetch="one")
            if not result.Hash_Contrasena:
                errores["DBError"] = "Error al obtener la contraseña de la base de datos"
            else:
                if result.Hash_Contrasena == 0:
                    errores["RFCNotFound"] = "RFC no encontrado"
                if verificar_contrasena(password, result.Hash_Contrasena):
                    rol_result = execute_query("EXEC Obtener_ID_Rol ?", (rfc,), fetch="one")
                    if not rol_result:
                        errores["DBError"] = "Error al consultar el rol"
                    else:
                        session["rfc"] = rfc
                        session["rol"] = rol_result.ID_Rol
                        match rol_result.ID_Rol:
                            case 1:
                                return redirect(url_for("VistasPrincipales.medico"))
                            case 2:
                                return redirect(url_for("medicoAdmin.medicoAdmin"))
                            case _:
                                errores["invalidRole"] = "Rol no válido"
                else:
                    errores["invalidLogin"] = "Contraseña incorrecta"
             
        except Exception as e:
            errores["loginError"] = "Error al intentar iniciar sesión"
            print(f"Error: {e}")

    return render_template("login.html", err=errores)
    