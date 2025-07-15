from connection import db

class RolesMedicosModel(db.Model):
    __tablename__ = "RolesMedicos"

    ID_rol = db.Column(db.Integer, primary_key = True)
    Nombre = db.Column(db.String(50), unique = True, nullable = False) 

    medicos = db.relationship("MedicosModel", back_populates="rol")