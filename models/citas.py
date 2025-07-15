from datetime import date
from connection import db

class CitasModel(db.Model):
    __tablename__ = "Citas"

    ID_cita = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Peso_paciente = db.Column(db.Numeric(5,2), nullable = False )
    Altura_paciente = db.Column(db.Numeric(5,2), nullable = False )
    Temperatura_paciente = db.Column(db.Numeric(5,2), nullable = False )
    LPM_paciente = db.Column(db.Numeric(5,2), nullable = False ) #Latidos por MN
    SDO_paciente = db.Column(db.Numeric(5,2), nullable = False ) #Oxigeno
    Glucosa_paciente = db.Column(db.Numeric(5,2), nullable = False ) 
    Estatus = db.Column(db.Boolean, default=True, nullable=False)
    fecha = db.Column(db.Date, default=date.today, nullable=False)
    Sintomas_paciente = db.Column(db.Text, nullable=True)
    Diagnostico_paciente = db.Column(db.Text, nullable=True)
    Tratamiento_paciente = db.Column(db.Text, nullable=True)

    ID_paciente = db.Column(db.Integer, db.ForeignKey("Pacientes.ID_paciente"), nullable=False)
    ID_medico = db.Column(db.Integer, db.ForeignKey("Medicos.ID_medico"), nullable=False)

    paciente = db.relationship("PacientesModel", backref="citas")
    medico = db.relationship("MedicosModel", backref="citas")
