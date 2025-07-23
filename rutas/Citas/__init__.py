from .agregarCita import agregarCita_bp
from .editarCita import editarCita_bp
from .eliminarCita import eliminarCita_bp
from .consultarCita import consultarCita_bp

citas_bps = [
    agregarCita_bp,
    editarCita_bp,
    eliminarCita_bp,
    consultarCita_bp
]

__all__ = ["citas_bps"]
