from flask import Blueprint, render_template , request, flash, session, redirect, url_for
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required
from datetime import datetime

editarCita_bp = Blueprint('editarCita', __name__)
#GET PRIMERA PARTE
@editarCita_bp.route("/editarCita")
@login_required
def mostrarEditarCita():
    print('Mostrando editar cita primera parte ---------------------')
    errores = {}
    try:
        required_fields = [
        "idCita", "peso", "altura", "temperatura", "latidos", "oxigeno", "glucosa",
        "paciente", "edad", "medico", "fecha", "sintomas", "diagnostico", "tratamiento", "estudios"
        ]
        print(f"Lo que hay en la session es: {session.get('cita_temp')}")
        emptyValues = [field for field in required_fields if field not in session.get('cita_temp', {})]
        print(f"Campos que no hay: {emptyValues}")
        if emptyValues:
            errores['emptyValues'] = "Error al obtener los datos"
    except Exception as e:
        print(f'Ha ocurrido un error dutante la obtención y muestra de los datos en sesion: {str(e)}')
        errores['dbError'] = "Error de durante la información de la cita"
    return render_template("Citas/EditarCita.html", errores = errores)

#POST PRIMERA PARTE
@editarCita_bp.route("/editarCita",methods=["POST"])
@login_required
def editarCita():
    errores = {}
    print('Editando cita primera parte ---------------------------------')
    try:
        peso = request.form.get("peso", "").strip()
        altura = request.form.get("altura", "").strip()
        temperatura = request.form.get("temperatura", "").strip()
        latidos = request.form.get("latidos", "").strip()
        oxigeno = request.form.get("oxigeno", "").strip()
        glucosa = request.form.get("glucosa", "").strip()

        print(f"Datos llegados peso {peso} altura: {altura} temperatura: {temperatura} latidos: {latidos} oxigeno: {oxigeno} glucosa: {glucosa} ")
        print(f"Tipos llegados peso {type(peso)} altura: {type(altura)} temperatura: {type(temperatura)} latidos: {type(latidos)} oxigeno: {type(oxigeno)} glucosa: {type(glucosa)} ")


        if not peso or not altura or not temperatura or not latidos or not oxigeno or not glucosa:
            print('No llego algun dato')
            errores['emptyValues'] ="No debe de haber campos vacios"
        else:
            session['cita_temp']['peso'] = peso
            session['cita_temp']['altura'] = altura
            session['cita_temp']['temperatura'] = temperatura
            session['cita_temp']['latidos'] = latidos
            session['cita_temp']['oxigeno'] = oxigeno
            session['cita_temp']['glucosa'] = glucosa
            flash("Datos iniciales eitados con éxito, termine con el diagnostico de la cita")
            return redirect(url_for('editarCita.mostrarEditarCitaContinuar'))
                
    except Exception as e:
        print(f'Ocurrio un error durante la primera edición de list {str(e)}')
        errores['dbError'] = "Ha ocurrido un error al intentar actualizar"

    return render_template("Citas/EditarCita.html", errores = errores)
#GET SEGUNDA PARTE
@editarCita_bp.route("/editarCita/continuar")
@login_required
def mostrarEditarCitaContinuar():
    print('Mostrando editar cita segunda parte---------------------------------------------')
    errores = {}
    return render_template("Citas/EditarCitaContinuar.html", errores = errores)

#POST SEGUNDA PARTE
@editarCita_bp.route("/editarCita/continuar",methods=["POST"])
@login_required
def editarCitaContinuar():
    print('Enviando cita a editar -----------------------------------')
    errores = {}
    sintomas = request.form.get("sintomas", "").strip()
    diagnostico = request.form.get("diagnostico", "").strip()
    tratamiento = request.form.get("tratamiento", "").strip()
    estudios = request.form.get("estudios", "").strip()

    print(f"Datos obtenidos: sintomas: {sintomas}, diagnostico: {diagnostico}, tratamiento: {tratamiento}, estudios: {estudios}")
    print(f"Tipos obtenidos: sintomas: {type(sintomas)}, diagnostico: {type(diagnostico)}, tratamiento: {type(tratamiento)}, estudios: {type(estudios)}")

    if not sintomas or not diagnostico or not tratamiento:
        print('Algun campo requerido esta vacio')
        errores['emptyValues'] = "No debe de haber campos vacios"
    if not estudios:
        estudios = "No se requiere"
    try:
        session['cita_temp']['sintomas'] = sintomas
        session['cita_temp']['diagnostico'] = diagnostico
        session['cita_temp']['tratamiento'] = tratamiento
        session['cita_temp']['estudios'] = estudios

        required_fields = [
        "idCita", "peso", "altura", "temperatura", "latidos", "oxigeno", "glucosa",
        "paciente", "edad", "medico", "fecha", "sintomas", "diagnostico", "tratamiento", "estudios"
        ]
        print(f"Lo que hay en la session es: {session.get('cita_temp')}")
        emptyValues = [field for field in required_fields if field not in session.get('cita_temp', {})]
        print(f"Campos que no hay: {emptyValues}")
        if emptyValues:
            errores['emptyValues'] = "Error al obtener los datos"
        else:
            execute_query("UPDATE Citas SET Peso_paciente = (?), Altura_paciente = (?), Temperatura_paciente = (?), LPM_paciente = (?), SDO_paciente = (?), Glucosa_paciente = (?), Sintomas_paciente = (?), Diagnostico_paciente = (?), Tratamiento_paciente = (?), Estudios_paciente = (?) WHERE ID_cita = (?)", 
                        ( session['cita_temp']['peso'], session['cita_temp']['altura'], session['cita_temp']['temperatura'], session['cita_temp']['latidos'], session['cita_temp']['oxigeno'], session['cita_temp']['glucosa'], session['cita_temp']['sintomas'], session['cita_temp']['diagnostico'], session['cita_temp']['tratamiento'], session['cita_temp']['estudios'],session['cita_temp']['idCita'] ),
                        fetch=None, commit=True)
            flash('Cita editada con éxito', 'editar')
            return redirect(url_for('consultarCita.mostrarConsultarCita', id_cita = session['cita_temp']['idCita']))
    except Exception as e:
        print(f'Error en segunda parte post de editar: {str(e)}')
        errores['dbError'] = "Error al editar los campos"

    return render_template("Citas/EditarCitaContinuar.html", errores = errores)