from flask import Blueprint, render_template, request, session, redirect, url_for
from BDAyudas.QueryExecute import execute_query
from decorators.loginRequired import login_required

citasLista_bp = Blueprint('citasLista', __name__)

@citasLista_bp.route("/citasLista", methods=["GET"])
@login_required
def citasLista():
    print('Entrando a lista de citas ----------------------------')
    errores = {}
    tblCitas = []
    rfc = session.get("rfc")

    try:
        fila = execute_query("SELECT dbo.IDMedico(?)", (rfc,), fetch="one")
        print(f'ID medico llegado: {fila}')

        if not fila or not fila[0]:
            errores['medicoNotFound'] = "No se encontró un médico"
            return render_template("VistasPrincipales/citasLista.html", errores=errores, tblCitas=tblCitas)

        idMedico = fila[0]

        query = "SELECT Citas.ID_cita, CONCAT(Pacientes.Nombres, ' ', Pacientes.Apellido_paterno, ' ', Pacientes.Apellido_materno) AS Nombre_Paciente FROM Citas JOIN Pacientes ON Citas.ID_paciente = Pacientes.ID_paciente WHERE Citas.ID_medico = (?) AND Citas.Estatus = (?)"
        tblCitas = execute_query(query, (idMedico, 1), fetch="all")
        print(f'Citas encontradas: {tblCitas}')

        if not tblCitas:
            errores["citasNotFound"] = "No se encontraron citas para mostrar"

    except Exception as e:
        print(f'Error durante obtención de lista de citas (GET): {str(e)}')
        errores['dbError'] = "Error durante obtención de lista de citas"

    return render_template("VistasPrincipales/citasLista.html", errores=errores, tblCitas=tblCitas)


@citasLista_bp.route("/citasLista/filtrar", methods=["POST"])
@login_required
def citasListaFiltro():
    print('Tratando de filtrar ----------------------------')
    errores = {}
    tblCitas = []
    filtro = request.form.get('filtro')
    busqueda = (request.form.get('busqueda') or '').strip()
    rfc = session.get("rfc")
    print(f'Filtro: {filtro}, Busqueda: {busqueda}, RFC: {rfc}')
    try:
        fila = execute_query("SELECT dbo.IDMedico(?)", (rfc,), fetch="one")
        print(f'ID medico llegado: {fila}')

        if not fila or not fila[0]:
            errores['medicoNotFound'] = "No se encontró un médico"
            return render_template("VistasPrincipales/citasLista.html", errores=errores, tblCitas=tblCitas)

        idMedico = fila[0]

        base = """
            SELECT
                C.ID_cita,
                CONCAT(P.Nombres, ' ', P.Apellido_paterno, ' ', P.Apellido_materno) AS Nombre_Paciente,
                C.Fecha_exploracion
            FROM Citas AS C
            JOIN Pacientes AS P ON C.ID_paciente = P.ID_paciente
            WHERE C.ID_medico = ? AND C.Estatus = ?
        """
        params = [idMedico, 1]

        if filtro == "Nombre" and busqueda:
            base += " AND CONCAT(P.Nombres, ' ', P.Apellido_paterno, ' ', P.Apellido_materno) LIKE ?"
            params.append(f"%{busqueda}%")

        elif filtro == "Fecha" and busqueda:
            # 'YYYY-MM-DD' para LIKE en fechas
            base += " AND CONVERT(VARCHAR(10), C.Fecha_exploracion, 23) LIKE ?"
            params.append(f"%{busqueda}%")
        
        elif filtro == "Todo":
            return redirect(url_for('citasLista.citasLista'))  

        # Si no hay busqueda o filtro desconocido, no agregamos condición extra
        base += " ORDER BY C.Fecha_exploracion DESC"

        tblCitas = execute_query(base, tuple(params), fetch="all")

        print(f'Citas encontradas: {tblCitas}')
        if not tblCitas:
            errores["busquedaNotFound"] = "no hay coincidencias"

    except Exception as e:
        print(f'Error durante obtención de lista de citas (POST): {str(e)}')
        errores['dbError'] = "Error durante obtención de lista de citas"

    return render_template("VistasPrincipales/citasLista.html", errores=errores, tblCitas=tblCitas)
