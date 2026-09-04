"""Puente: piezas migradas desde el arnés de origen y adaptadas a COSMOS.

Cinco herramientas que el árbol cosmográfico no traía y que ya estaban resueltas:
proyectar sobre un repo ajeno, escanear secretos sobre el índice Git, verificar
sobre una instantánea del índice, consultar la lluvia sin traerse su cuerpo y
guardar la SESIÓN mientras el agente trabaja (`sesion.py`), que es lo único que
no miran ni el pre-commit ni el CI.
"""

from .etiquetas import etiqueta_de_ruta

__all__ = ["etiqueta_de_ruta"]
