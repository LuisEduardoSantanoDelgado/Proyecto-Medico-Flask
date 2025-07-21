from .agregarMedico import agregarMedico_bp
from .editarMedico import editarMedico_bp
from .eliminarMedico import eliminarMedico_bp

medicos_bps = [
    agregarMedico_bp,
    editarMedico_bp,
    eliminarMedico_bp
]

__all__ = ["medicos_bps"]
