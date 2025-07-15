from connection import db

class PacientesModel(db.Model):
    __tablename__ = "Pacientes"

    ID_paciente = db.Column(db.Integer, primary_key = True, autoincrement=True)
    Nombres = db.Column(db.String(100), nullable = False)
    Apellido_paterno = db.Column(db.String(50), nullable = False)
    Apellido_materno = db.Column(db.String(50), nullable = False)
    Fecha_nacimiento = db.Column(db.Date, nullable = False)
    Alergias = db.Column(db.Text)
    Enfermedades_cronicas = db.Column(db.Text)
    Antecedentes_familiares = db.Column(db.Text)
    Estatus = db.Column(db.Boolean, default=True, nullable=False)
    Edad = db.Column(db.Integer, nullable=False)

    medicos = db.relationship('MedicosModel', secondary=pacientes_medicos, back_populates='pacientes')