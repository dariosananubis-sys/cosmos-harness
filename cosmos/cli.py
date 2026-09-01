"""Interfaz de línea de comandos de COSMOS."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

from .compilar import ErrorCompilacion, compilar_arbol, formatear_compilacion
from .generar import escribir_indice, generar_mapa
from .medir import MetodoNoDisponible, casos_json, formatear_casos, medir_casos
from .modelo import Configuracion, ErrorConfiguracion, ErrorNicho, cargar_arbol, cargar_configuracion, normalizar_nichos
from .validar import formatear_validacion, validacion_json, validar_arbol


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cosmos", description="Organiza y valida contexto con carga perezosa.")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    def base(nombre: str, ayuda: str) -> argparse.ArgumentParser:
        sub = subparsers.add_parser(nombre, help=ayuda)
        sub.add_argument("raiz", nargs="?", type=Path, help="raíz del árbol; por defecto usa cosmos.toml")
        sub.add_argument("--config", type=Path, default=Path("cosmos.toml"), help="ruta de cosmos.toml")
        return sub

    validar = base("validar", "comprueba las invariantes E00-E19")
    validar.add_argument("--json", action="store_true", help="emite JSON")
    validar.add_argument("--indice", type=Path, help="ruta del índice que se compara")
    validar.add_argument("--nicho", action="append", help="nicho activo; se puede repetir")

    medir = base("medir", "mide el contexto de entrada y el árbol")
    medir.add_argument("--metodo", choices=("aprox", "exacto"), help="solo inspección; validar usa cosmos.toml")
    medir.add_argument("--detalle", action="store_true")
    medir.add_argument("--json", action="store_true", help="emite JSON")
    seleccion = medir.add_mutually_exclusive_group()
    seleccion.add_argument("--nicho", action="append", help="nicho activo; se puede repetir")
    seleccion.add_argument("--combinacion", help="nichos simultáneos separados por comas")

    generar = base("generar", "regenera el índice de galaxia")
    generar.add_argument("--salida", "--indice", dest="salida", type=Path, help="ruta de salida")

    compilar = base("compilar", "genera la vista plana de ciudades y pueblos")
    compilar.add_argument("--modo", choices=("symlink", "copia"))
    compilar.add_argument("--destino", type=Path)
    compilar.add_argument("--seco", action="store_true", help="describe cambios sin escribir")
    compilar.add_argument("--nicho", help="aplana solo las skills del nicho indicado")

    base("mapa", "muestra el árbol completo para inspección")
    return parser


def _configuracion(args: argparse.Namespace) -> Configuracion:
    config = cargar_configuracion(args.config)
    if args.raiz is None:
        return config
    raiz = args.raiz.resolve()
    return replace(config, arbol=raiz, indice=raiz / "COSMOS.md")


def _nichos_medicion(args: argparse.Namespace) -> list[str] | None:
    if args.nicho:
        return args.nicho
    if not args.combinacion:
        return None
    partes = [parte.strip() for parte in args.combinacion.split(",")]
    if not partes or any(not parte for parte in partes):
        raise ErrorNicho("--combinacion exige nombres no vacíos separados por comas")
    return partes


def ejecutar(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        config = _configuracion(args)
    except ErrorConfiguracion as exc:
        print(f"COSMOS  error de configuración\n\nE00  {exc}", file=sys.stderr)
        return 2

    arbol = cargar_arbol(config.arbol, excluir=config.indice, excluir_directorios=(config.destino_compilacion,))
    try:
        if args.comando == "validar":
            indice = args.indice.resolve() if args.indice else config.indice
            nichos = normalizar_nichos(arbol, args.nicho)
            config_efectiva = replace(config, nichos=nichos)
            resultado = validar_arbol(arbol, configuracion=config_efectiva, indice=indice)
            sys.stdout.write(validacion_json(resultado) if args.json else formatear_validacion(resultado))
            return resultado.codigo_salida
        if args.comando == "medir":
            nichos = normalizar_nichos(arbol, _nichos_medicion(args))
            resultado_medicion = medir_casos(arbol, metodo=args.metodo or config.metodo, presupuesto=config.entrada, nichos=nichos)
            sys.stdout.write(casos_json(resultado_medicion) if args.json else formatear_casos(resultado_medicion, detalle=args.detalle))
            return 0 if resultado_medicion.evaluada.entrada <= config.entrada else 1
        if args.comando == "generar":
            destino = args.salida.resolve() if args.salida else config.indice
            previo = validar_arbol(arbol, configuracion=config, indice=destino, omitir_codigos=frozenset({"E15"}))
            if not previo.valido:
                sys.stdout.write(formatear_validacion(previo))
                return 1
            escribir_indice(arbol, destino)
            posterior = validar_arbol(arbol, configuracion=config, indice=destino)
            if not posterior.valido:
                sys.stdout.write(formatear_validacion(posterior))
                return 1
            print(f"COSMOS  generar  verde\n\nÍndice escrito en {destino}")
            return 0
        if args.comando == "compilar":
            destino = args.destino.resolve() if args.destino else config.destino_compilacion
            modo = args.modo or config.modo_compilacion
            nichos = normalizar_nichos(arbol, [args.nicho] if args.nicho else None)
            config_efectiva = replace(config, destino_compilacion=destino, modo_compilacion=modo, nichos=nichos)
            previo = validar_arbol(arbol, configuracion=config_efectiva, omitir_codigos=frozenset({"E19"}))
            if not previo.valido:
                sys.stdout.write(formatear_validacion(previo))
                return 1
            compilacion = compilar_arbol(
                arbol,
                destino=destino,
                manifiesto=config.manifiesto_compilacion,
                modo=modo,
                seco=args.seco,
                nichos=nichos,
                config_path=config.ruta,
            )
            sys.stdout.write(formatear_compilacion(compilacion))
            if args.seco:
                return 0
            posterior = validar_arbol(arbol, configuracion=config_efectiva)
            if not posterior.valido:
                sys.stdout.write(formatear_validacion(posterior))
                return 1
            return 0
        if args.comando == "mapa":
            sys.stdout.write(generar_mapa(arbol))
            return 0
    except (MetodoNoDisponible, ErrorCompilacion, ErrorNicho) as exc:
        print(f"COSMOS  {args.comando}  rojo\n\n{exc}", file=sys.stderr)
        return 1
    return 2


def main() -> None:
    raise SystemExit(ejecutar())


if __name__ == "__main__":
    main()
