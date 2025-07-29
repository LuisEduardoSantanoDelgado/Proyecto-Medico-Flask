from flask import Blueprint, render_template , request, flash, session, url_for, redirect
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from datetime import datetime

agregarCita_bp = Blueprint('agregarCita', __name__)
#GET PRIMERA PARTE
@agregarCita_bp.route("/agregarCita/<id_paciente>")
@login_required
def mostrarAgregarCita(id_paciente):
    errores={}
    print('Entrando a agregar cita -------------------------------')
    print(f'ID de paciente: {id_paciente} tipo: {type(id_paciente)}')
    try:
        if not id_paciente:
            print(f"Campo vacio id paciente: {id_paciente}")
            errores["dbError"] = "Error al obtener datos."
        else:
            nombrePaciente = execute_query("SELECT ISNULL(Nombres, '') + ' ' + ISNULL(Apellido_paterno, '') + ' ' + ISNULL(Apellido_materno, '') FROM Pacientes WHERE ID_paciente = (?)", (id_paciente,), fetch="one")
            edadPaciente = execute_query("SELECT Edad FROM Pacientes WHERE ID_paciente = (?)", (id_paciente,), fetch="one")
            fechaExploracion = datetime.today().strftime('%Y-%m-%d')
            print(f"Datos obtenidos nombre del paciente: {nombrePaciente} edad: {edadPaciente} fecha de exploración {fechaExploracion}")
            if not nombrePaciente or not edadPaciente or not fechaExploracion:
                print('Alguno de los datos obtenidos esta vacio ---')
                errores["dbError"] = "Error durante la obtencion de datos"
            else:
                nombrePaciente = nombrePaciente[0]
                edadPaciente = edadPaciente[0]
                return render_template('Citas/AgregarCita.html', nombrePaciente = nombrePaciente, paciente = id_paciente, edadPaciente = edadPaciente, fechaExploracion = fechaExploracion, errores = errores)
    except Exception as e:
        print(f'Ha ocurrido un error al intentar obtener datos del medico o del paciente: {str(e)}')
        errores["dbError"] = "Error durante la consulta de la base de datos"
        
    return render_template("Citas/AgregarCita.html", nombrePaciente = None, paciente = None, edadPaciente = None, fechaExploracion = None, errores = errores)

#POST PRIMERA PARTE
@agregarCita_bp.route("/agregarCita",methods=["POST"])
@login_required
def agregarCita():
    errores = {}
    print('Intentando insertar cita --------------------------------')
    peso = request.form.get("peso", "").strip()
    altura = request.form.get("altura", "").strip()
    temperatura = request.form.get("temperatura", "").strip()
    latidos = request.form.get("latidos", "").strip()
    oxigeno = request.form.get("oxigeno", "").strip()
    glucosa = request.form.get("glucosa", "").strip()
    idPaciente = request.form.get("id_paciente", "").strip()

    print(f"Datos llegados peso {peso} altura: {altura} temperatura: {temperatura} latidos: {latidos} oxigeno: {oxigeno} glucosa: {glucosa} id: {idPaciente}")
    print(f"Tipos llegados peso {type(peso)} altura: {type(altura)} temperatura: {type(temperatura)} latidos: {type(latidos)} oxigeno: {type(oxigeno)} glucosa: {type(glucosa)} id: {type(idPaciente)}")

    if not peso or not altura or not temperatura or not latidos or not oxigeno or not glucosa or not idPaciente:
        print('No llego algun dato')
        errores['emptyDatos'] ="No debe de haber campos vacios"
    else:
        rfc = session.get("rfc")
        id_medico   = execute_query("SELECT dbo.IDMedico(?)", (rfc,), fetch="one")
        print(f'RFC del medico que atiende {rfc} y id: {id_medico}')
        if not id_medico:
            errores['dbError'] = "Error al obtener al asignar cita con medico"
        try:
            session['cita_temp'] = {
                "peso": peso,
                "altura": altura,
                "temperatura": temperatura,
                "latidos": latidos,
                "oxigeno": oxigeno,
                "glucosa": glucosa,
                "idPaciente": idPaciente,
                "id_medico": id_medico[0] if id_medico else None  
            }
            print(f"Lo guardado en sesion {session.get("cita_temp")}")
            if session.get("cita_temp"): 
                flash("Datos iniciales guardados con éxito, termine con el diagnostico de la cita")
                return redirect(url_for('agregarCita.mostrarAgregarCitaContinuar'))
            else:
                print('Error sesion sin datos')
                errores['dbError'] = "Error, sesion sin datos"
        except Exception as e:
            print(f'Error al guardar datos iniciales de cita {str(e)}')
            errores['dbError'] = "Error al guardar datos iniciales"
        
    return render_template("Citas/AgregarCita.html", nombrePaciente = None, paciente = None, edadPaciente = None, fechaExploracion = None, errores = errores)
    
#GET SEGUNDA PARTE
@agregarCita_bp.route("/agregarCita/continuar")
@login_required
def mostrarAgregarCitaContinuar():
    print('Mostrando segunda parte de agregar cita ------------------------------------------------')
    return render_template("Citas/AgregarCitaContinuar.html")

@agregarCita_bp.route("/agregarCita/continuar",methods=["POST"])
@login_required
def agregarCitaContinuar():
    errores = {}
    sintomas = request.form.get("sintomas", "").strip()
    diagnostico = request.form.get("diagnostico", "").strip()
    tratamiento = request.form.get("tratamiento", "").strip()
    estudios = request.form.get("estudios", "").strip()

    print(f"Datos obtenidos: sintomas: {sintomas}, diagnostico: {diagnostico}, tratamiento: {tratamiento}, estudios: {estudios}")
    print(f"Tipos obtenidos: sintomas: {type(sintomas)}, diagnostico: {type(diagnostico)}, tratamiento: {type(tratamiento)}, estudios: {type(estudios)}")

    if not sintomas or not diagnostico or not tratamiento:
        print('Algun campo requerido esta vacio')
        errores['emptyDatos'] = "No debe de haber campos vacios"
    if not estudios:
        estudios = "No se requiere"

    try:
        cita = session.get('cita_temp')
        print(f'Información de cita {cita}')
        if cita:
            resultado = execute_query(" DECLARE @resultado INT; EXEC sp_InsertarCita ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, @resultado OUTPUT; SELECT @resultado;", 
                    (cita["peso"], cita["altura"], cita["temperatura"], cita["latidos"], cita["oxigeno"], cita["glucosa"], cita["idPaciente"], cita["id_medico"],
                    sintomas, diagnostico, tratamiento, estudios), fetch="one", commit=True)
            print(f"Resultado obtenido de insertar {resultado}")
            if resultado:
                match resultado[0]:
                    case -1:
                        print('La cita se repite')
                        errores['citaExist'] = "Ya se tuvo una cita con esa persona este día"
                    case 0:
                        print('Exito al agregar cita')
                        flash("Cita agregada con éxito")
                        return redirect(url_for("citasLista.citasLista"))
                    case _:
                        print("Error inesperado")
                        errores["dbError"] = "Algo falló"
            else:
                print('Fallo con resultado')
                errores['dbError'] = "Error al obtener el resultado"
        else:
            print('Cita vacia')
            errores['citaError'] = "Error al obtener datos anteriores"
    except Exception as e:
        print(f"Ocurrio el error: {str(e)}")
        errores['dbError'] = "Error durante la insersion"
        
    return render_template("Citas/AgregarCitaContinuar.html", errores = errores)

