from connection import db

pacientes_medicos = db.Table(
    'Pacientes_Medicos',
    db.Column('ID_paciente', db.Integer, db.ForeignKey('Pacientes.ID_paciente'), primary_key=True),
    db.Column('ID_medico', db.Integer, db.ForeignKey('Medicos.ID_medico'), primary_key=True)
)

class MedicosModel(db.Model):
    __tablename__ = "Medicos"

    ID_medico = db.Column(db.Integer, primary_key = True, autoincrement=True)
    Nombres = db.Column(db.String(100), nullable = False)
    Apellido_paterno = db.Column(db.String(50), nullable = False)
    Apellido_materno = db.Column(db.String(50), nullable = False)
    Cedula_profesional = db.Column(db.String(20), nullable = False)
    RFC = db.Column(db.String(13), nullable = False)
    Correo_electronico = db.Column(db.String(254), nullable = False)
    Contrasena = db.Column(db.String(200), nullable = False)
    Estatus = db.Column(db.Boolean, default=True, nullable=False)

    ID_rol = db.Column(db.Integer, db.ForeignKey("rolesMedicos.ID_rol"), nullable=False)
    rol = db.relationship("RolesMedicosModel", back_populates="medicos")

    pacientes = db.relationship('PacientesModel', secondary=pacientes_medicos, back_populates='medicos')
