from flask import Flask, render_template, session, flash, url_for, redirect
from rutas.login import login_bp
from decorators.loginRequired import login_required
# Importar las rutas de los médicos
from rutas.VistasPrincipales.medicoAdmin import medicoAdmin_bp
from rutas.Medicos.agregarMedico import agregarMedico_bp
from rutas.Medicos.editarMedico import editarMedico_bp
from rutas.Medicos.eliminarMedico import eliminarMedico_bp
# Importar las rutas de los pacientes
from rutas.VistasPrincipales.medico import medico_bp
from rutas.Pacientes.agregarPaciente import agregarPaciente_bp
from rutas.Pacientes.editarPaciente import editarPaciente_bp
from rutas.Pacientes.eliminarPaciente import eliminarPaciente_bp
#Importar las rutas de las citas
from rutas.VistasPrincipales.citasLista import citasLista_bp
from rutas.Citas.agregarCita import agregarCita_bp
from rutas.Citas.eliminarCita import eliminarCita_bp
from rutas.Citas.editarCita import editarCita_bp
app = Flask(__name__)
app.secret_key = "mysecretkey"




#Rutas -----------------------------------
#Inicio de sesión
app.register_blueprint(login_bp)

# Manejo de medicos
#Medico administrador
app.register_blueprint(medicoAdmin_bp)

#Medico

#Agregar médico
app.register_blueprint(agregarMedico_bp)

#Edicion de médicos
app.register_blueprint(editarMedico_bp)


#Eliminación de médicos
app.register_blueprint(eliminarMedico_bp)

#Pacientes

# Manejo de pacientes
app.register_blueprint(medico_bp)

#Agregar paciente
app.register_blueprint(agregarPaciente_bp)

#Edición de pacientes
app.register_blueprint(editarPaciente_bp)

#Eliminación de pacientes
app.register_blueprint(eliminarPaciente_bp)

#Citas

#Lista de citas
app.register_blueprint(citasLista_bp)
#Agregar cita
app.register_blueprint(agregarCita_bp)
#Eliminar cita
app.register_blueprint(eliminarCita_bp)
#Editar cita
app.register_blueprint(editarCita_bp)
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