"""Interfaz de línea de comandos de COSMOS."""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from dataclasses import replace
from pathlib import Path

from .compilar import ErrorCompilacion, compilar_arbol, formatear_compilacion
from .generar import escribir_indice, generar_mapa
from .guardarrailes import (
    ErrorEnganche,
    ErrorSalto,
    Salto,
    ahora_utc,
    analizar_duracion,
    anotar_salida,
    desenganchar,
    enganchar,
    estado_saltos,
    normalizar_codigo,
    registrar_salto,
    ruta_saltos,
    sufijo_saltos,
)
from .estado import estado_json, formatear as formatear_estado, inventariar
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

    estado = base("estado", "inventario del árbol: qué hay, qué falta, qué no agrupa")
    estado.add_argument("--json", action="store_true", help="emite JSON")

    validar = base("validar", "comprueba las invariantes E00-E19")
    validar.add_argument("--json", action="store_true", help="emite JSON")
    validar.add_argument("--indice", type=Path, help="ruta del índice que se compara")
    validar.add_argument("--nicho", action="append", help="nicho activo; anula [nichos] activos")

    medir = base("medir", "mide el contexto de entrada y el árbol")
    medir.add_argument("--metodo", choices=("aprox", "exacto"), help="solo inspección; validar usa cosmos.toml")
    medir.add_argument("--detalle", action="store_true")
    medir.add_argument("--json", action="store_true", help="emite JSON")
    seleccion = medir.add_mutually_exclusive_group()
    seleccion.add_argument("--nicho", action="append", help="nicho activo; anula [nichos] activos")
    seleccion.add_argument("--combinacion", help="nichos simultáneos separados por comas")

    generar = base("generar", "regenera el índice de galaxia")
    generar.add_argument("--salida", "--indice", dest="salida", type=Path, help="ruta de salida")

    compilar = base("compilar", "genera la vista plana de ciudades y pueblos")
    compilar.add_argument("--modo", choices=("symlink", "copia"))
    compilar.add_argument("--destino", type=Path)
    compilar.add_argument("--seco", action="store_true", help="describe cambios sin escribir")
    compilar.add_argument("--nicho", help="aplana solo las skills del nicho indicado")

    arrancar = base("arrancar", "deja un clon recién bajado en verde: compila la vista y valida")
    arrancar.add_argument("--modo", choices=("symlink", "copia"))
    arrancar.add_argument("--destino", type=Path)
    arrancar.add_argument("--nicho", help="aplana solo las skills del nicho indicado")

    base("mapa", "muestra el árbol completo para inspección")

    engancha = subparsers.add_parser("enganchar", help="instala el gate de pre-commit en este repositorio")
    engancha.add_argument("--config", type=Path, default=Path("cosmos.toml"), help="ruta de cosmos.toml")
    engancha.add_argument("--sin-pruebas", action="store_true", help="el hook omitirá las suites de tests")

    desengancha = subparsers.add_parser("desenganchar", help="quita el gate de pre-commit")
    desengancha.add_argument("--config", type=Path, default=Path("cosmos.toml"), help="ruta de cosmos.toml")

    saltar = subparsers.add_parser("saltar", help="válvula de escape acotada, con motivo y caducidad")
    saltar.add_argument("codigo", nargs="?", help="código concreto a saltar (E00..E19)")
    saltar.add_argument("--config", type=Path, default=Path("cosmos.toml"), help="ruta de cosmos.toml")
    saltar.add_argument("--motivo", help="obligatorio: por qué se salta")
    saltar.add_argument("--caduca", help="obligatorio: días de vigencia, como '7d' (máximo 30d)")
    saltar.add_argument("--listar", action="store_true", help="muestra los saltos vivos y los vencidos")
    return parser


def _configuracion(args: argparse.Namespace) -> Configuracion:
    config = cargar_configuracion(args.config)
    raiz = getattr(args, "raiz", None)
    if raiz is None:
        return config
    resuelta = raiz.resolve()
    return replace(config, arbol=resuelta, indice=resuelta / "COSMOS.md")


def nichos_de_configuracion(ruta: Path | None) -> list[str] | None:
    """Lee `[nichos] activos`. Lista vacía o sección ausente significa «todos»."""

    if ruta is None or not Path(ruta).is_file():
        return None
    try:
        datos = tomllib.loads(Path(ruta).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ErrorConfiguracion(f"no se puede leer {ruta}: {exc}") from exc
    seccion = datos.get("nichos", {})
    if not isinstance(seccion, dict):
        raise ErrorConfiguracion("[nichos] debe ser una tabla TOML")
    activos = seccion.get("activos", [])
    if not isinstance(activos, list) or any(not isinstance(valor, str) for valor in activos):
        raise ErrorConfiguracion("[nichos].activos debe ser una lista de nombres")
    return activos or None


def _nichos(explicitos: list[str] | None, config: Configuracion) -> list[str] | None:
    return explicitos if explicitos else nichos_de_configuracion(config.ruta)


def _nichos_medicion(args: argparse.Namespace) -> list[str] | None:
    if args.nicho:
        return args.nicho
    if not args.combinacion:
        return None
    partes = [parte.strip() for parte in args.combinacion.split(",")]
    if not partes or any(not parte for parte in partes):
        raise ErrorNicho("--combinacion exige nombres no vacíos separados por comas")
    return partes


def _base_repositorio(config: Configuracion) -> Path:
    return config.ruta.parent if config.ruta is not None else config.arbol


def _salida_validacion(
    resultado, activos: list[Salto], caducados: list[Salto], *, como_json: bool
) -> str:
    momento = ahora_utc()
    if not como_json:
        return anotar_salida(formatear_validacion(resultado), activos, caducados, ahora=momento)
    datos = json.loads(validacion_json(resultado))
    datos["saltos_activos"] = [
        dict(salto.como_dict(), dias_restantes=salto.dias_restantes(momento)) for salto in activos
    ]
    datos["saltos_caducados"] = [salto.como_dict() for salto in caducados]
    return json.dumps(datos, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _saltos(config: Configuracion) -> tuple[list[Salto], list[Salto]]:
    return estado_saltos(ruta_saltos(_base_repositorio(config)))


def _codigos_saltados(activos: list[Salto]) -> frozenset[str]:
    return frozenset(salto.codigo for salto in activos)


def _informe(resultado, config: Configuracion) -> str:
    """Formatea una validación intermedia respetando la válvula, como la final."""

    activos, caducados = _saltos(config)
    return anotar_salida(formatear_validacion(resultado), activos, caducados)


def _validar(args: argparse.Namespace, config: Configuracion, arbol) -> int:
    indice = args.indice.resolve() if getattr(args, "indice", None) else config.indice
    nichos = normalizar_nichos(arbol, _nichos(args.nicho, config))
    activos, caducados = _saltos(config)
    resultado = validar_arbol(
        arbol,
        configuracion=replace(config, nichos=nichos),
        indice=indice,
        omitir_codigos=_codigos_saltados(activos),
    )
    sys.stdout.write(_salida_validacion(resultado, activos, caducados, como_json=args.json))
    return resultado.codigo_salida


def _compilar(
    args: argparse.Namespace,
    config: Configuracion,
    arbol,
    *,
    seco: bool = False,
    omitir_previo: frozenset[str] = frozenset({"E19"}),
) -> int:
    destino = args.destino.resolve() if args.destino else config.destino_compilacion
    modo = args.modo or config.modo_compilacion
    explicitos = [args.nicho] if args.nicho else None
    nichos = normalizar_nichos(arbol, _nichos(explicitos, config))
    config_efectiva = replace(config, destino_compilacion=destino, modo_compilacion=modo, nichos=nichos)
    # La válvula también vale aquí: si no, un salto legítimo dejaría el árbol en
    # verde para `validar` y en rojo para `compilar`, y el gate corre `arrancar`.
    saltados = _codigos_saltados(_saltos(config)[0])
    previo = validar_arbol(arbol, configuracion=config_efectiva, omitir_codigos=omitir_previo | saltados)
    if not previo.valido:
        sys.stdout.write(_informe(previo, config))
        return 1
    compilacion = compilar_arbol(
        arbol,
        destino=destino,
        manifiesto=config.manifiesto_compilacion,
        modo=modo,
        seco=seco,
        nichos=nichos,
        config_path=config.ruta,
    )
    sys.stdout.write(anotar_salida(formatear_compilacion(compilacion), _saltos(config)[0]))
    if seco:
        return 0
    posterior = validar_arbol(arbol, configuracion=config_efectiva, omitir_codigos=saltados)
    if not posterior.valido:
        sys.stdout.write(_informe(posterior, config))
        return 1
    return 0


def _arrancar(args: argparse.Namespace, config: Configuracion, arbol) -> int:
    """Bootstrap de un clon recién bajado.

    La vista plana es un artefacto generado y no se versiona, así que un clon
    limpio la tiene ausente y E19 lo canta. Esto la construye y vuelve a validar,
    que es todo lo que le faltaba al repositorio para no parecer roto (H01).
    """

    # E15 se omite solo en el paso previo: sin vista plana no se puede haber
    # generado el índice todavía, y compilar no lo toca. Se vuelve a exigir entero
    # en la validación final, así que un índice que miente sigue saliendo en rojo:
    # arrancar hace que la vista exista, nunca fabrica el índice por su cuenta.
    codigo = _compilar(args, config, arbol, omitir_previo=frozenset({"E15", "E19"}))
    if codigo:
        sys.stdout.write("\nCOSMOS  arrancar  rojo\n")
        return codigo
    args_validar = argparse.Namespace(indice=None, nicho=None, json=False)
    codigo = _validar(args_validar, config, arbol)
    destino = args.destino.resolve() if args.destino else config.destino_compilacion
    if codigo == 0:
        cierre = anotar_salida("COSMOS  arrancar  verde", _saltos(config)[0])
        sys.stdout.write(f"\n{cierre}\n\nVista compilada en {destino}\n")
    else:
        sys.stdout.write(
            f"\nCOSMOS  arrancar  rojo\n\nVista compilada en {destino}, pero el árbol no valida.\n"
            "Si falta o miente el índice, regenéralo con 'cosmos generar'.\n"
        )
    return codigo


def _saltar(args: argparse.Namespace, config: Configuracion) -> int:
    log = ruta_saltos(_base_repositorio(config))
    if args.listar or not args.codigo:
        momento = ahora_utc()
        activos, caducados = estado_saltos(log, ahora=momento)
        if not activos and not caducados:
            sys.stdout.write(f"COSMOS  saltar  sin saltos registrados en {log}\n")
            return 0
        sys.stdout.write(f"COSMOS  saltar{sufijo_saltos(activos, momento)}\n")
        for salto in activos:
            sys.stdout.write(
                f"\nACTIVO    {salto.codigo}  caduca el {salto.caduca.date().isoformat()}"
                f" ({salto.dias_restantes(momento)} d)\n          «{salto.motivo}»\n"
            )
        for salto in caducados:
            sys.stdout.write(
                f"\nCADUCADO  {salto.codigo}  venció el {salto.caduca.date().isoformat()}"
                f"\n          «{salto.motivo}»\n"
            )
        return 0
    if not args.motivo or not args.caduca:
        raise ErrorSalto(
            "un salto exige --motivo y --caduca. Sin motivo no se sabe qué se aceptó, "
            "y sin caducidad la excepción se vuelve costumbre."
        )
    codigo = normalizar_codigo(args.codigo)
    duracion = analizar_duracion(args.caduca)
    salto = registrar_salto(log, codigo, args.motivo, duracion)
    sys.stdout.write(
        f"COSMOS  saltar  {salto.codigo} saltado hasta el {salto.caduca.date().isoformat()}"
        f" ({salto.dias_restantes(ahora_utc())} d)\n\n"
        f"Motivo: «{salto.motivo}»\nRegistrado en {log}\n"
        "Mientras dure, ninguna salida de 'cosmos validar' dirá «verde» a secas.\n"
    )
    return 0


def _enganchar(args: argparse.Namespace, config: Configuracion) -> int:
    ruta, estado = enganchar(_base_repositorio(config), con_pruebas=not args.sin_pruebas)
    sys.stdout.write(
        f"COSMOS  enganchar  verde\n\nHook de pre-commit {estado} en {ruta}\n"
        "Cada commit correrá 'puente.gate' sobre la instantánea del índice.\n"
        "Se quita con 'cosmos desenganchar'.\n"
    )
    return 0


def _desenganchar(args: argparse.Namespace, config: Configuracion) -> int:
    ruta, estado = desenganchar(_base_repositorio(config))
    if estado == "ausente":
        sys.stdout.write(f"COSMOS  desenganchar  verde\n\nNo había hook en {ruta}; nada que quitar.\n")
        return 0
    sys.stdout.write(f"COSMOS  desenganchar  verde\n\nHook {estado} de {ruta}\n")
    return 0


def ejecutar(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        config = _configuracion(args)
    except ErrorConfiguracion as exc:
        print(f"COSMOS  error de configuración\n\nE00  {exc}", file=sys.stderr)
        return 2

    try:
        if args.comando == "saltar":
            return _saltar(args, config)
        if args.comando == "enganchar":
            return _enganchar(args, config)
        if args.comando == "desenganchar":
            return _desenganchar(args, config)

        arbol = cargar_arbol(config.arbol, excluir=config.indice, excluir_directorios=(config.destino_compilacion,))
        if args.comando == "validar":
            return _validar(args, config, arbol)
        if args.comando == "medir":
            nichos = normalizar_nichos(arbol, _nichos(_nichos_medicion(args), config))
            resultado_medicion = medir_casos(arbol, metodo=args.metodo or config.metodo, presupuesto=config.entrada, nichos=nichos)
            sys.stdout.write(casos_json(resultado_medicion) if args.json else formatear_casos(resultado_medicion, detalle=args.detalle))
            return 0 if resultado_medicion.evaluada.entrada <= config.entrada else 1
        if args.comando == "generar":
            destino = args.salida.resolve() if args.salida else config.indice
            saltados = _codigos_saltados(_saltos(config)[0])
            previo = validar_arbol(
                arbol, configuracion=config, indice=destino, omitir_codigos=frozenset({"E15"}) | saltados
            )
            if not previo.valido:
                sys.stdout.write(_informe(previo, config))
                return 1
            escribir_indice(arbol, destino)
            posterior = validar_arbol(arbol, configuracion=config, indice=destino, omitir_codigos=saltados)
            if not posterior.valido:
                sys.stdout.write(_informe(posterior, config))
                return 1
            cabecera = anotar_salida("COSMOS  generar  verde", _saltos(config)[0])
            print(f"{cabecera}\n\nÍndice escrito en {destino}")
            return 0
        if args.comando == "compilar":
            return _compilar(args, config, arbol, seco=args.seco)
        if args.comando == "arrancar":
            return _arrancar(args, config, arbol)
        if args.comando == "mapa":
            sys.stdout.write(generar_mapa(arbol))
            return 0
        if args.comando == "estado":
            inv = inventariar(arbol)
            sys.stdout.write(estado_json(inv) if args.json else formatear_estado(inv))
            return 0
    except ErrorConfiguracion as exc:
        print(f"COSMOS  error de configuración\n\nE00  {exc}", file=sys.stderr)
        return 2
    except (MetodoNoDisponible, ErrorCompilacion, ErrorNicho, ErrorSalto, ErrorEnganche) as exc:
        print(f"COSMOS  {args.comando}  rojo\n\n{exc}", file=sys.stderr)
        return 1
    return 2


def main() -> None:
    raise SystemExit(ejecutar())


if __name__ == "__main__":
    main()
