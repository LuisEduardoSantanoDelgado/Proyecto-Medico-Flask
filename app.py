from flask import Flask, render_template, session, flash, url_for, redirect
from rutas.login import login_bp
from decorators.loginRequired import login_required
# Importar las rutas de los médicos
from rutas.Medicos import medicos_bps
# Importar las rutas de los pacientes
from rutas.Pacientes import pacientes_bps
#Importar las rutas de las citas
from rutas.Citas import citas_bps
#Importar las vistas principales
from rutas.VistasPrincipales import vistasPrincipales_bps
app = Flask(__name__)
app.secret_key = "mysecretkey"




#Rutas -----------------------------------
#Inicio de sesión
app.register_blueprint(login_bp)

#Creacion de rutas
for bp in vistasPrincipales_bps + medicos_bps + pacientes_bps + citas_bps:
    app.register_blueprint(bp)


#Cerrar sesion
@app.route("/cerrarSesion")
@login_required
def cerrarSesion():
    print("Entrando a cerrar sesión ------------------")
    try:
        session.clear()  
        flash("Sesión cerrada correctamente.")
        return redirect(url_for("login.home"))
    except Exception as e:
        errores = {}
        errores["sessionError"] = "Error al cerrar sesión"
        print(f"Error al cerrar sesión: {str(e)}")
        return render_template("login.html", err=errores)

#ERRORES
@app.errorhandler(404)
def error404(e):
    print(f"Error 404: {str(e)}")
    return render_template("Errores/error404.html"), 404

@app.errorhandler(405)
def error405(e):
    print(f"Error 405: {str(e)}")
    return render_template("Errores/error405.html"), 405

@app.errorhandler(Exception)
def handle_unexpected_error(e):
    print(f"Error inesperado: {str(e)}")
    return render_template("Errores/errorGenerico.html"), 500

if __name__ == "__main__":
    app.run(port = 3000, debug = True)