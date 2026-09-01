"""Puente: piezas migradas desde <agencia>-Harness y adaptadas a COSMOS.

Cuatro herramientas que el árbol cosmográfico no traía y que ya estaban resueltas:
proyectar sobre un repo ajeno, escanear secretos sobre el índice Git, verificar
sobre una instantánea del índice y consultar la lluvia sin traerse su cuerpo.
"""

from .etiquetas import etiqueta_de_ruta

__all__ = ["etiqueta_de_ruta"]
