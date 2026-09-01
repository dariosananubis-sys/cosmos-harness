#!/usr/bin/env python3
"""Reorganiza galaxia/ al mapa de oficios de spec/UNIVERSO.md.

Solo mueve nodos y reescribe su 'padre'. No inventa pueblos ni cambia resúmenes:
el contenido ya pasó la regla de admisión en las tandas 1 y 2.

Se ejecuta una vez y se borra. Vive en el repo el tiempo que dura el cambio para
que la reorganización sea auditable en el diff, no un montón de ficheros movidos
a mano sin rastro de por qué.
"""
from __future__ import annotations
import re, shutil, sys
from pathlib import Path

RAIZ = Path(__file__).parent / "galaxia"

# --- Nichos que se van, y adónde va cada pueblo suyo -------------------------
# La decisión de cada destino está en el parte de reorganización; aquí solo el mapa.
DESTINO = {
    # datos -> ingenieria-datos (el pipeline) + analitica (la lectura de negocio)
    "dbt-core": "ingenieria-datos/transformacion",
    "pandera": "ingenieria-datos/validacion",
    "duckdb": "ingenieria-datos/motor",
    "polars": "ingenieria-datos/motor",
    "streamlit": "analitica/cuadros-de-mando",
    "evidence": "analitica/cuadros-de-mando",
    "statsforecast": "analitica/prevision",
    "gspread": "analitica/hojas-de-calculo",
    # agentes -> agentes-ia (construirlos) + modelos-locales (servir IA propia)
    "claude-agent-sdk": "agentes-ia/construccion",
    "agent-browser": "agentes-ia/herramientas",
    "openclaw": "agentes-ia/herramientas",
    "mem0": "agentes-ia/memoria",
    "claude-mem": "agentes-ia/memoria",
    "mlflow": "agentes-ia/evaluacion",
    "ollama": "modelos-locales/servir",
    "mlx-lm": "modelos-locales/servir",
    "sentence-transformers": "modelos-locales/recuperacion",
    "lancedb": "modelos-locales/recuperacion",
    # medios -> audiovisual (lo temporal) + documentos (lo paginado) + web (imagen de sitio)
    "ffmpeg": "audiovisual/video",
    "whisper-cpp": "audiovisual/voz",
    "kokoro": "audiovisual/voz",
    "rembg": "web/imagenes",
    "sharp": "web/imagenes",
    "pandoc": "documentos/conversion",
    "markitdown": "documentos/conversion",
    "weasyprint": "documentos/generacion",
    # conocimiento -> documentos
    "mkdocs-material": "documentos/sitios",
    "openapi-generator": "documentos/desde-el-codigo",
    "context7": "documentos/referencia",
    "d2": "documentos/diagramas",
    "mermaid": "documentos/diagramas",
    # sistemas -> rendimiento; tree-sitter no es de rendimiento, es de parseo
    "rr": "rendimiento/depuracion",
    "samply": "rendimiento/perfilado",
    "tokio": "rendimiento/concurrencia",
    "tree-sitter": "extraccion/parseo",
    # negocio -> se reparte: facturar es de producto, el resto es automatizar la oficina
    "gobl": "saas/facturacion",
    "docuseal": "automatizacion/firma",
    "twenty": "automatizacion/clientes",
    "openproject": "automatizacion/proyectos",
    # legal -> cumplimiento
    "fossology": "cumplimiento/licencias",
    "ort": "cumplimiento/licencias",
    "presidio": "cumplimiento/datos-personales",
    "arx": "cumplimiento/datos-personales",
}

# Nichos que solo cambian de nombre: todo lo que colgaba de ellos se reapunta.
RENOMBRA = {"mercados": "trading"}

# --- Nichos nuevos y sus países ---------------------------------------------
NICHOS_NUEVOS = {
    "ingenieria-datos": "Un pipeline que valida antes de cargar y avisa cuando se rompe.",
    "analitica": "Cuadros de mando y metricas de negocio en los que se puede confiar.",
    "agentes-ia": "Agentes que hacen trabajo real, con herramientas, memoria y evaluacion.",
    "modelos-locales": "IA que corre en tu maquina: privacidad, coste cero por uso, sin depender de nadie.",
    "audiovisual": "Video y voz a escala: cortar, subtitular, transcribir, doblar y sintetizar.",
    "documentos": "Entregables paginados: informes, manuales, diagramas y documentacion que se genera sola.",
    "rendimiento": "Que vaya rapido y se pueda depurar: perfilado, concurrencia, trazas.",
    "cumplimiento": "RGPD, accesibilidad legal y licencias: lo que evita la multa.",
}

PAISES = {
    "ingenieria-datos": {"transformacion": "Modelar y transformar datos con linaje y pruebas.",
                          "validacion": "Rechazar el dato malo antes de que entre.",
                          "motor": "Consultar mucho dato sin levantar un servidor."},
    "analitica": {"cuadros-de-mando": "Publicar lo que se mide para que otro lo lea.",
                  "prevision": "Estimar lo que viene con intervalos, no con una cifra suelta.",
                  "hojas-de-calculo": "Leer y escribir lo que el negocio ya tiene en hojas."},
    "agentes-ia": {"construccion": "Armar el agente: bucle, herramientas, permisos.",
                   "herramientas": "Darle manos: navegador, consola, ficheros.",
                   "memoria": "Que recuerde entre sesiones sin arrastrar todo el historial.",
                   "evaluacion": "Medir si el agente mejora o solo cambia."},
    "modelos-locales": {"servir": "Levantar un modelo en la maquina y hablarle por API.",
                        "recuperacion": "Buscar por significado sobre datos propios."},
    "audiovisual": {"video": "Cortar, convertir y componer imagen en movimiento por lotes.",
                    "voz": "Pasar voz a texto y texto a voz, con doblaje y subtitulos."},
    "documentos": {"conversion": "Pasar de un formato a otro sin perder estructura.",
                   "generacion": "Producir el PDF final con maquetacion controlada.",
                   "sitios": "Publicar documentacion navegable desde ficheros de texto.",
                   "desde-el-codigo": "Generar la referencia desde el contrato, no a mano.",
                   "diagramas": "Dibujar desde texto para que el diagrama viva en el repo.",
                   "referencia": "Consultar documentacion de terceros al dia."},
    "rendimiento": {"perfilado": "Medir donde se va el tiempo antes de tocar nada.",
                    "depuracion": "Reproducir el fallo raro las veces que haga falta.",
                    "concurrencia": "Hacer varias cosas a la vez sin corromper nada."},
    "cumplimiento": {"licencias": "Saber que licencias entran con las dependencias y si chocan.",
                     "datos-personales": "Encontrar y anonimizar lo personal antes de que salga."},
    "web": {"imagenes": "Dejar la foto lista para el sitio: peso, formato y recorte."},
    "extraccion": {"parseo": "Convertir texto o codigo en estructura consultable."},
    "saas": {"facturacion": "Emitir facturas validas donde toque y con el impuesto correcto."},
    "automatizacion": {"firma": "Firmar documentos con validez y sin plataforma de pago.",
                       "clientes": "Seguir a quien te compra sin ceder los datos a un tercero.",
                       "proyectos": "Coordinar trabajo con API, no con capturas de pantalla."},
}

VECINOS = {
    "web": ["saas", "visibilidad", "cumplimiento"],
    "saas": ["web", "cumplimiento", "infraestructura"],
    "trading": ["ingenieria-datos", "infraestructura"],
    "agentes-ia": ["modelos-locales", "extraccion"],
    "modelos-locales": ["agentes-ia"],
    "ingenieria-datos": ["analitica", "extraccion"],
    "analitica": ["ingenieria-datos"],
    "extraccion": ["ingenieria-datos", "cumplimiento"],
    "ciberseguridad": ["infraestructura", "cumplimiento"],
    "moviles": ["saas", "web"],
    "juegos": ["audiovisual", "rendimiento"],
    "audiovisual": ["documentos"],
    "documentos": ["audiovisual"],
    "automatizacion": ["saas", "infraestructura"],
    "infraestructura": ["ciberseguridad", "rendimiento"],
    "visibilidad": ["web", "documentos"],
    "blockchain": ["ciberseguridad"],
    "embebidos": ["rendimiento"],
    "cientifico": ["ingenieria-datos", "rendimiento"],
    "rendimiento": ["ciberseguridad"],
    "cumplimiento": ["web", "extraccion"],
}


def campo(texto: str, clave: str) -> str | None:
    m = re.search(rf"^{clave}: *\"?([^\"\n]+)\"?$", texto, re.M)
    return m.group(1).strip() if m else None


def escribir_nodo(ruta: Path, datos: dict[str, str], cuerpo: str = "") -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    lineas = ["---"]
    for k, v in datos.items():
        lineas.append(f"{k}:" if v is None else f"{k}: {v}")
    lineas += ["---", ""]
    if cuerpo:
        lineas.append(cuerpo)
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main() -> int:
    if not RAIZ.exists():
        print("no encuentro galaxia/", file=sys.stderr)
        return 1

    nodos = {}
    for f in RAIZ.rglob("*.md"):
        t = f.read_text(encoding="utf-8")
        nivel, nombre = campo(t, "cosmos"), campo(t, "nombre")
        if nivel and nombre:
            nodos[f] = (nivel, nombre, campo(t, "padre"), t)

    # 1. Crear nichos nuevos con sus vecinos
    for nombre, resumen in NICHOS_NUEVOS.items():
        destino = RAIZ / "sistemas" / f"{nombre}.md"
        if destino.exists():
            continue
        d = {"cosmos": "sistema-solar", "nombre": nombre, "padre": '""', "resumen": resumen}
        escribir_nodo(destino, d)
        print(f"  nicho nuevo: {nombre}")

    # 2. Crear países que hagan falta
    for nicho, paises in PAISES.items():
        for pais, resumen in paises.items():
            destino = RAIZ / "paises" / f"{nicho}--{pais}.md"
            if destino.exists():
                continue
            escribir_nodo(destino, {"cosmos": "pais", "nombre": pais,
                                    "padre": nicho, "resumen": resumen})

    # 3. Reapuntar pueblos
    movidos = 0
    for f, (nivel, nombre, padre, t) in nodos.items():
        nuevo = DESTINO.get(nombre)
        if not nuevo and padre:
            raiz_padre = padre.split("/")[0]
            if raiz_padre in RENOMBRA:
                nuevo = padre.replace(raiz_padre, RENOMBRA[raiz_padre], 1)
        if nuevo and nuevo != padre:
            t2 = re.sub(r"^padre: *\"?[^\"\n]*\"?$", f"padre: {nuevo}", t, count=1, flags=re.M)
            f.write_text(t2, encoding="utf-8")
            movidos += 1

    # 4. Renombrar el nicho 'mercados' -> 'trading'
    for f, (nivel, nombre, padre, t) in nodos.items():
        if nombre in RENOMBRA and nivel == "sistema-solar":
            t2 = re.sub(r"^nombre: .*$", f"nombre: {RENOMBRA[nombre]}", t, count=1, flags=re.M)
            f.write_text(t2, encoding="utf-8")
            f.rename(f.with_name(f"{RENOMBRA[nombre]}.md"))
            print(f"  renombrado: {nombre} -> {RENOMBRA[nombre]}")

    # 5. Borrar los nichos que salen (sus pueblos ya están reapuntados)
    for f, (nivel, nombre, padre, t) in list(nodos.items()):
        if nivel in ("sistema-solar", "estrella") and nombre in {"datos", "agentes", "medios",
                                                                 "sistemas", "conocimiento",
                                                                 "negocio", "legal"}:
            f.unlink(missing_ok=True)
            print(f"  fuera: {nivel}/{nombre}")

    # 6. Añadir 'usa:' a cada nicho
    for f in (RAIZ / "sistemas").glob("*.md"):
        t = f.read_text(encoding="utf-8")
        nombre = campo(t, "nombre")
        vecinos = VECINOS.get(nombre)
        if not vecinos or "usa:" in t:
            continue
        bloque = "usa:\n" + "".join(f"  - {v}\n" for v in vecinos)
        t = re.sub(r"^---\s*$", bloque + "---", t, count=1, flags=re.M) if False else \
            t.replace("\n---\n", "\n" + bloque + "---\n", 1)
        f.write_text(t, encoding="utf-8")

    print(f"\npueblos reapuntados: {movidos}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
