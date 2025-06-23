from flask import Flask, jsonify, render_template,  url_for, flash, redirect
from decorators.loginRequired import login_required
from rutas.login import login_bp
from rutas.VistasPrincipales.medicoAdmin import medicoAdmin_bp
from rutas.Medicos.agregarMedico import agregarMedico_bp
from rutas.Medicos.editarMedico import editarMedico_bp

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
@app.route("/eliminar_medico/<rfc>", methods=["POST"])
@login_required(2)
def eliminarMedico(rfc):
    errores = {}
    try:
        conn = getConnection(2)
        cursor = conn.cursor()
        cursor.execute("EXEC EliminarMedico ?", rfc)
        resultado = cursor.fetchone()

        if not resultado:
            errores["medicoNotFound"] = "Médico no encontrado"
            return render_template("medicoAdmin.html", errores=errores)

        if resultado.Resultado == 1:
            flash("Médico eliminado exitosamente")
            return redirect(url_for("medicoAdmin"))
        else:
            errores["dbError"] = "Error al eliminar médico"

    except Exception as e:
        errores["dbError"] = "Error al eliminar médico"
        print(f"Error: {e}")
    finally:
        cursor.close()

    return render_template("medicoAdmin.html", errores=errores)
#Comprobar la conexión a la base de datos
@app.route("/DBCheck")
def dbCheck():
    try:
        conn = getConnection(2)
        cursor = conn.cursor()
        cursor.execute("Select 1")
        return jsonify({"status": "Ok", "message": "Conectado"}), 200
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500
    finally:
        cursor.close()

#ERRORES
@app.errorhandler(404)
def paginaNoEncontrada(e):
    return "¡Cuidado, error de capa 8!", 404

@app.errorhandler(405)
def error505(e):
    return "¡Revisa el método de envio!", 405

if __name__ == "__main__":
    app.run(port = 3000, debug = True)