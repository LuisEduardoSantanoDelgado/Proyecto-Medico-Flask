from .agregarPaciente import agregarPaciente_bp
from .editarPaciente import editarPaciente_bp
from .eliminarPaciente import eliminarPaciente_bp

pacientes_bps = [
    agregarPaciente_bp,
    editarPaciente_bp,
    eliminarPaciente_bp
]

__all__ = ["pacientes_bps"]
