"""Interfaz de línea de comandos de COSMOS."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

from .generar import escribir_indice, generar_mapa
from .medir import MetodoNoDisponible, formatear_medicion, medicion_json, medir_arbol
from .modelo import Configuracion, ErrorConfiguracion, cargar_arbol, cargar_configuracion
from .validar import formatear_validacion, validacion_json, validar_arbol


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cosmos", description="Organiza y valida contexto con carga perezosa.")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    def base(nombre: str, ayuda: str) -> argparse.ArgumentParser:
        sub = subparsers.add_parser(nombre, help=ayuda)
        sub.add_argument("raiz", nargs="?", type=Path, help="raíz del árbol; por defecto usa cosmos.toml")
        sub.add_argument("--config", type=Path, default=Path("cosmos.toml"), help="ruta de cosmos.toml")
        return sub

    validar = base("validar", "comprueba las invariantes E00-E18")
    validar.add_argument("--json", action="store_true", help="emite JSON")
    validar.add_argument("--indice", type=Path, help="ruta del índice que se compara")

    medir = base("medir", "mide el contexto de entrada y el árbol")
    medir.add_argument("--metodo", choices=("auto", "aprox", "exacto"), default="auto")
    medir.add_argument("--detalle", action="store_true")
    medir.add_argument("--json", action="store_true", help="emite JSON")

    generar = base("generar", "regenera el índice de galaxia")
    generar.add_argument("--salida", "--indice", dest="salida", type=Path, help="ruta de salida")

    base("mapa", "muestra el árbol completo para inspección")
    return parser


def _configuracion(args: argparse.Namespace) -> Configuracion:
    config = cargar_configuracion(args.config)
    if args.raiz is None:
        return config
    raiz = args.raiz.resolve()
    return replace(config, arbol=raiz, indice=raiz / "COSMOS.md")


def ejecutar(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        config = _configuracion(args)
    except ErrorConfiguracion as exc:
        print(f"COSMOS  error de configuración\n\nE00  {exc}", file=sys.stderr)
        return 2

    arbol = cargar_arbol(config.arbol, excluir=config.indice)
    if args.comando == "validar":
        indice = args.indice.resolve() if args.indice else config.indice
        resultado = validar_arbol(arbol, configuracion=config, indice=indice)
        sys.stdout.write(validacion_json(resultado) if args.json else formatear_validacion(resultado))
        return resultado.codigo_salida
    if args.comando == "medir":
        try:
            resultado_medicion = medir_arbol(arbol, metodo=args.metodo, presupuesto=config.entrada)
        except MetodoNoDisponible as exc:
            print(f"COSMOS  medir  rojo\n\n{exc}", file=sys.stderr)
            return 1
        sys.stdout.write(medicion_json(resultado_medicion) if args.json else formatear_medicion(resultado_medicion, detalle=args.detalle))
        return 0 if resultado_medicion.entrada <= config.entrada else 1
    if args.comando == "generar":
        destino = args.salida.resolve() if args.salida else config.indice
        escribir_indice(arbol, destino)
        print(f"COSMOS  generar  verde\n\nÍndice escrito en {destino}")
        return 0
    if args.comando == "mapa":
        sys.stdout.write(generar_mapa(arbol))
        return 0
    return 2


def main() -> None:
    raise SystemExit(ejecutar())


if __name__ == "__main__":
    main()
