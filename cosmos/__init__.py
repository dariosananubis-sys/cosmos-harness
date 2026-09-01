"""COSMOS: taxonomía y guardarraíles de contexto para agentes."""

from .modelo import Arbol, Nodo, cargar_arbol
from .validar import ResultadoValidacion, validar_arbol

__all__ = ["Arbol", "Nodo", "ResultadoValidacion", "cargar_arbol", "validar_arbol"]
__version__ = "0.1.0"
