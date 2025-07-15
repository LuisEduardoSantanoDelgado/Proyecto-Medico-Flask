#Tabla intermedia entre medicos y pacientes
from connection import db

pacientes_medicos = db.Table(
    'Pacientes_Medicos',
    db.Column('ID_paciente', db.Integer, db.ForeignKey('Pacientes.ID_paciente'), primary_key=True),
    db.Column('ID_medico', db.Integer, db.ForeignKey('Medicos.ID_medico'), primary_key=True)
)
