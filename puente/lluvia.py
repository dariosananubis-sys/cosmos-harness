#!/usr/bin/env python3
"""Consulta el registro por BM25 y devuelve dónde mirar, nunca el cuerpo."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from cosmos.modelo import parsear_frontmatter

REGISTRO = "registro"
CARPETAS = ("commits", "lluvia", "informes", "decisiones")
MAX_CUERPO = 256_000
MAX_SALIDA = 4_000
MIN_SALIDA = 256
LIMITE_RESUMEN = 120
PESOS = {
    "nombre": 6.0,
    "nicho": 4.0,
    "resumen": 2.0,
    "carpeta": 1.0,
    "ruta": 1.0,
    "cuerpo": 1.0,
}
# Campos que salen. El cuerpo no está y no puede estar: es la única razón de ser
# de esta pieza. Proyectar campo a campo, y no el registro entero, impide que un
# campo nuevo se cuele en la salida sin que nadie lo decida.
CAMPOS_PUBLICOS = ("ruta", "nombre", "resumen", "carpeta", "nicho")
K1 = 1.2
B = 0.75
SALTOS = 3
PESO_SALTO = 0.12


@dataclass(frozen=True)
class Entrada:
    ruta: str
    nombre: str
    resumen: str
    carpeta: str
    nicho: str
    cuerpo: str
    motivos: tuple[str, ...] = ()

    def publico(self) -> dict[str, str]:
        return {campo: getattr(self, campo) for campo in CAMPOS_PUBLICOS}


def normalizar(texto: str) -> list[str]:
    plano = unicodedata.normalize("NFKD", texto.lower())
    plano = "".join(caracter for caracter in plano if not unicodedata.combining(caracter))
    return re.findall(r"[a-z0-9]{2,}", plano)


def _sin_frontmatter(texto: str) -> str:
    return re.sub(r"^---\s*\n.*?\n---\s*", "", texto, count=1, flags=re.DOTALL).strip()


def _resumen_deducido(cuerpo: str) -> str:
    for linea in cuerpo.splitlines():
        limpia = linea.strip().lstrip("#").strip()
        if limpia:
            return limpia[:LIMITE_RESUMEN]
    return ""


def _frontmatter_del_anfitrion(texto: str) -> dict[str, str]:
    """`name` y `description` de una memoria del anfitrión, leídos con tolerancia.

    La memoria de Claude Code lleva `metadata:` con un mapa anidado y a veces una descripción
    con comillas a medias: no es un nodo y no pasa por el parser normativo. Solo se sacan las
    dos claves que sirven para encontrarla; el cuerpo no se carga en el resultado.
    """

    datos: dict[str, str] = {}
    if not texto.startswith("---"):
        return datos
    cabecera = texto.split("\n---", 1)[0]
    for clave in ("name", "description"):
        coincidencia = re.search(rf"^{clave}:\s*(.+?)\s*$", cabecera, re.M)
        if coincidencia:
            valor = coincidencia.group(1).strip()
            if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
                valor = valor[1:-1]
            datos[clave] = valor
    return datos


def _memoria_del_anfitrion(directorio: Path, etiqueta: str) -> list[Entrada]:
    """Las memorias de `memory/` (u otro directorio declarado en `[raiz] memoria`), sin moverlas."""

    entradas: list[Entrada] = []
    if not directorio.is_dir():
        return entradas
    for ruta in sorted(directorio.glob("*.md")):
        if ruta.is_symlink() or not ruta.is_file() or ruta.name.upper() == "MEMORY.MD":
            continue
        try:
            with ruta.open("rb") as manejador:
                crudo = manejador.read(MAX_CUERPO)
        except OSError:
            continue
        texto = crudo.decode("utf-8", errors="replace")
        datos = _frontmatter_del_anfitrion(texto)
        cuerpo = _sin_frontmatter(texto)
        nombre = datos.get("name") or ruta.stem
        entradas.append(Entrada(
            ruta=f"{etiqueta}/{ruta.name}",
            nombre=nombre,
            resumen=(datos.get("description") or _resumen_deducido(cuerpo))[:LIMITE_RESUMEN * 3],
            carpeta="lluvia",
            nicho=nombre.split("-", 1)[0] if "-" in nombre else "",
            cuerpo=cuerpo,
        ))
    return entradas


def indexar(raiz: str | Path | None = None, memoria: str | Path | None = None) -> list[Entrada]:
    """Construye el índice leyendo el registro; no hay artefacto que sincronizar.

    El original exigía un index.json previo y fallaba pidiendo un paso de arranque.
    Aquí las entradas SON los ficheros, así que una memoria escrita hace un segundo
    ya se encuentra, y una borrada deja de encontrarse. `memoria` añade el directorio de
    memoria del anfitrión (`[raiz] memoria` en `cosmos.toml`): se indexa donde está.
    """

    base = Path(raiz or Path(__file__).resolve().parent.parent)
    registro = (base / REGISTRO).resolve()
    entradas: list[Entrada] = []
    if memoria is not None:
        ruta_memoria = Path(memoria)
        etiqueta = ruta_memoria.name if ruta_memoria.is_absolute() else ruta_memoria.as_posix()
        entradas.extend(_memoria_del_anfitrion(ruta_memoria if ruta_memoria.is_absolute() else base / ruta_memoria, etiqueta))
    if not registro.is_dir():
        return entradas
    for ruta in sorted(registro.rglob("*.md")):
        if ruta.is_symlink() or not ruta.is_file():
            continue
        resuelta = ruta.resolve()
        if not resuelta.is_relative_to(registro):
            continue
        try:
            with ruta.open("rb") as manejador:
                crudo = manejador.read(MAX_CUERPO)
        except OSError:
            continue
        texto = crudo.decode("utf-8", errors="replace")
        relativa = resuelta.relative_to(registro).as_posix()
        partes = relativa.split("/")
        carpeta = partes[0] if partes[0] in CARPETAS else ""
        nicho = partes[1] if len(partes) > 2 and carpeta else ""
        datos: dict[str, object] = {}
        if texto.startswith("---"):
            try:
                datos, _ = parsear_frontmatter(texto, relativa)
            except ValueError:
                datos = {}
        cuerpo = _sin_frontmatter(texto)
        nombre = datos.get("nombre") if isinstance(datos.get("nombre"), str) else ""
        resumen = datos.get("resumen") if isinstance(datos.get("resumen"), str) else ""
        entradas.append(
            Entrada(
                ruta=f"{REGISTRO}/{relativa}",
                nombre=nombre or resuelta.stem,
                resumen=resumen or _resumen_deducido(cuerpo),
                carpeta=carpeta,
                nicho=nicho,
                cuerpo=cuerpo,
            )
        )
    return entradas


def _campos(entrada: Entrada) -> dict[str, list[str]]:
    return {campo: normalizar(getattr(entrada, campo)) for campo in PESOS}


def ordenar(consulta: str, entradas: list[Entrada]) -> list[tuple[float, Entrada]]:
    """BM25 por campos, más un salto por nicho desde las entradas más fuertes."""

    terminos = list(dict.fromkeys(normalizar(consulta)))
    if not terminos or not entradas:
        return []

    documentos = [_campos(entrada) for entrada in entradas]
    frecuencia_documental: Counter[str] = Counter()
    longitudes: dict[str, list[int]] = defaultdict(list)
    for campos in documentos:
        vistos: set[str] = set()
        for tokens in campos.values():
            vistos.update(tokens)
        frecuencia_documental.update(vistos)
        for campo, tokens in campos.items():
            longitudes[campo].append(len(tokens))

    medias = {
        campo: (sum(valores) / len(valores) if any(valores) else 1.0)
        for campo, valores in longitudes.items()
    }
    total = len(entradas)
    frase = " ".join(normalizar(consulta))
    directas: dict[str, float] = {}
    motivos: dict[str, set[str]] = defaultdict(set)

    for entrada, campos in zip(entradas, documentos, strict=True):
        puntuacion = 0.0
        for campo, tokens in campos.items():
            cuenta = Counter(tokens)
            longitud = max(1, len(tokens))
            for termino in terminos:
                frecuencia = cuenta[termino]
                if not frecuencia:
                    continue
                en_documentos = frecuencia_documental[termino]
                inversa = math.log(1 + (total - en_documentos + 0.5) / (en_documentos + 0.5))
                normalizada = (
                    frecuencia * (K1 + 1)
                    / (frecuencia + K1 * (1 - B + B * longitud / medias[campo]))
                )
                puntuacion += PESOS[campo] * inversa * normalizada
                motivos[entrada.ruta].add(campo)
        nombre_buscable = " ".join(normalizar(entrada.nombre))
        resumen_buscable = " ".join(normalizar(entrada.resumen))
        if frase and frase in nombre_buscable:
            puntuacion += 8.0
            motivos[entrada.ruta].add("frase")
        elif frase and frase in resumen_buscable:
            puntuacion += 4.0
            motivos[entrada.ruta].add("frase")
        if puntuacion:
            directas[entrada.ruta] = puntuacion

    por_ruta = {entrada.ruta: entrada for entrada in entradas}
    puntuaciones = dict(directas)
    fuertes = sorted(directas.items(), key=lambda item: (-item[1], item[0]))[:SALTOS]
    for ruta_origen, puntuacion_origen in fuertes:
        nicho = por_ruta[ruta_origen].nicho
        if not nicho:
            continue
        for entrada in entradas:
            if entrada.nicho != nicho or entrada.ruta == ruta_origen:
                continue
            puntuaciones[entrada.ruta] = (
                puntuaciones.get(entrada.ruta, 0.0) + puntuacion_origen * PESO_SALTO
            )
            motivos[entrada.ruta].add(f"nicho:{nicho}")

    ordenadas = [
        (
            round(puntuacion, 6),
            Entrada(
                **{
                    campo: getattr(por_ruta[ruta], campo)
                    for campo in ("ruta", "nombre", "resumen", "carpeta", "nicho", "cuerpo")
                },
                motivos=tuple(sorted(motivos[ruta])),
            ),
        )
        for ruta, puntuacion in puntuaciones.items()
    ]
    return sorted(
        ordenadas,
        key=lambda item: (item[1].ruta not in directas, -item[0], item[1].ruta),
    )


def como_texto(
    resultados: list[tuple[float, Entrada]], maximo: int, *, explicar: bool = False
) -> str:
    """Una línea por entrada, dentro del presupuesto de bytes y sin cuerpo."""

    lineas: list[str] = []
    usado = 0
    for puntuacion, entrada in resultados:
        publico = entrada.publico()
        explicacion = f" | motivos={','.join(entrada.motivos)}" if explicar else ""
        linea = (
            f"{publico['ruta']} | {publico['nombre']} | {publico['resumen']} | "
            f"{publico['carpeta'] or 'registro'}/{publico['nicho'] or 'sin-nicho'} | "
            f"puntuacion={puntuacion:.3f}{explicacion}"
        )
        tamano = len((linea + "\n").encode("utf-8"))
        if usado + tamano > maximo:
            break
        lineas.append(linea)
        usado += tamano
    return "\n".join(lineas)


def como_json(resultados: list[tuple[float, Entrada]], maximo: int) -> str:
    carga = [
        entrada.publico() | {"puntuacion": puntuacion} for puntuacion, entrada in resultados
    ]
    while carga:
        rendido = json.dumps(carga, ensure_ascii=False, separators=(",", ":"))
        if len((rendido + "\n").encode("utf-8")) <= maximo:
            return rendido
        carga.pop()
    return "[]"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("consulta", help="términos del problema, nicho o decisión")
    parser.add_argument("--limite", type=int, default=5)
    parser.add_argument("--max-bytes", type=int, default=MAX_SALIDA)
    parser.add_argument("--explicar", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--raiz", default=None)
    args = parser.parse_args(argv)

    if args.max_bytes < MIN_SALIDA:
        parser.error(f"--max-bytes debe ser al menos {MIN_SALIDA}")
    memoria = None
    try:
        from cosmos.modelo import cargar_configuracion

        config = cargar_configuracion(Path(args.raiz or ".") / "cosmos.toml")
        memoria = config.memoria if config.encontrada else None
    except Exception:  # noqa: BLE001 — sin cosmos.toml legible, solo el registro
        memoria = None
    entradas = indexar(args.raiz, memoria=memoria)
    if not entradas:
        print("ERROR: el registro está vacío o no existe", file=sys.stderr)
        return 1
    resultados = ordenar(args.consulta, entradas)[: max(1, min(args.limite, 10))]
    if args.json:
        print(como_json(resultados, args.max_bytes))
    elif not resultados:
        print("sin memorias relevantes")
    else:
        rendido = como_texto(resultados, args.max_bytes, explicar=args.explicar)
        print(rendido or "sin resultados dentro del presupuesto")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
