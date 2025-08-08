from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from BDAyudas.QueryExecute import execute_query
from utility.encriptarContrasena import verificar_contrasena

login_bp = Blueprint('login', __name__)

@login_bp.route("/")
def home():
    return render_template("login.html")

@login_bp.route("/login", methods=["POST"])
def login():
    print('Entrando a login ---------------------------')
    errores = {}
    rfc = request.form.get("rfc", "").strip()
    password = request.form.get("password", "").strip()

    if not rfc or not password:
        errores["emptyValues"] = "RFC o contraseña vacíos"
        flash("RFC o contraseña vacíos", "error")
    
    DMexico = execute_query("SELECT Estatus FROM Medicos WHERE RFC = ?",(rfc,), fetch="one")

    if DMexico is None:
        print(f"Error al obtener el estatus estado: {DMexico}")
        errores["DBError"] = "Error al consultar el estatus"
        flash("Error durante la consulta a la base de datos", "error")
    elif DMexico[0] == 0:
        print(f"El usuario {rfc} esta inactivo")
        errores["DBError"] = "Error en las credenciales"
        flash("Hay un problema con el usuario", "error")
        

    if not errores:
        try:
            result = execute_query("EXEC Obtener_Contrasena ?", (rfc,), fetch="one")
            if not result.Hash_Contrasena:
                errores["DBError"] = "Error al obtener la contraseña de la base de datos"
                flash("Error durante la consulta a la base de datos", "error")
            else:
                if result.Hash_Contrasena == 0:
                    errores["RFCNotFound"] = "RFC no encontrado"
                    flash("No hay usuario con ese RFC", "error")
                if verificar_contrasena(password, result.Hash_Contrasena):
                    rol_result = execute_query("EXEC Obtener_ID_Rol ?", (rfc,), fetch="one")
                    if not rol_result:
                        errores["DBError"] = "Error al consultar el rol"
                        flash("Error durante la consulta a la base de datos", "error")
                    else:
                        session["rfc"] = rfc
                        session["rol"] = rol_result.ID_Rol
                        match rol_result.ID_Rol:
                            case 1:
                                return redirect(url_for("medico.medico"))
                            case 2:
                                return redirect(url_for("medicoAdmin.medicoAdmin"))
                            case _:
                                errores["invalidRole"] = "Rol no válido"
                                flash("Error durante la consulta a la base de datos", "error")
                else:
                    errores["invalidLogin"] = "Contraseña incorrecta"
                    flash("La contraseña no es correcta", "error")
             
        except Exception as e:
            errores["loginError"] = "Error al intentar iniciar sesión"
            flash("Error al iniciar sesión", "error")
            print(f"Error: {e}")

    return render_template("login.html", errores=errores)
    