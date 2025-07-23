from .citasLista import citasLista_bp
from .medico import medico_bp
from .medicoAdmin import medicoAdmin_bp

vistasPrincipales_bps = [
    citasLista_bp,
    medico_bp,
    medicoAdmin_bp
]

__all__ = ["vistasPrincipales_bps"]
