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
    desenganchar_sesion,
    enganchar,
    enganchar_sesion,
    estado_saltos,
    normalizar_codigo,
    registrar_salto,
    ruta_saltos,
    sufijo_saltos,
)
from .abrir import NodoNoEncontrado, abrir, apertura_json, formatear as formatear_apertura
from .acertar import (Contraste, ErrorEncargos, cargar_encargos, formatear as formatear_acierto,
                      formatear_contraste, puntuacion_json, puntuar)
from .estado import estado_json, formatear as formatear_estado, inventariar
from .medir import (MetodoNoDisponible, casos_json, formatear_casos, medir_casos,
                    veredicto_de_presupuesto)
from .modelo import Configuracion, ErrorConfiguracion, ErrorNicho, cargar_arbol, cargar_configuracion, normalizar_nichos
from .validar import (INVARIANTE_PRESUPUESTO, formatear_validacion, rango_comprobado,
                      validacion_json, validar_arbol)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cosmos", description="Organiza y valida contexto con carga perezosa.")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    def base(nombre: str, ayuda: str) -> argparse.ArgumentParser:
        sub = subparsers.add_parser(nombre, help=ayuda)
        sub.add_argument("raiz", nargs="?", type=Path, help="raíz del árbol; por defecto usa cosmos.toml")
        sub.add_argument("--config", type=Path, default=Path("cosmos.toml"), help="ruta de cosmos.toml")
        return sub

    abrir_cmd = base("abrir", "carga un nodo: su cuerpo, su estrella y por dónde seguir")
    abrir_cmd.add_argument("ruta", help="ruta cosmográfica o nombre, p.ej. 'trading/backtesting'")
    abrir_cmd.add_argument(
        "--tocando",
        metavar="FICHERO",
        help="ruta del fichero que se va a tocar: lista el agua que lo moja de verdad",
    )
    abrir_cmd.add_argument("--json", action="store_true", help="emite JSON")

    acertar_cmd = base("acertar", "¿el catálogo lleva a la herramienta correcta? La contra-métrica")
    acertar_cmd.add_argument("--encargos", type=Path, default=Path("pruebas/encargos.json"))
    acertar_cmd.add_argument(
        "--validacion",
        type=Path,
        default=Path("pruebas/encargos-validacion.json"),
        help="encargos que NO guían decisiones: la cifra honesta sale de aquí",
    )
    acertar_cmd.add_argument("--minimo", type=int, default=0,
                             help="falla si se acierta menos de esto (en %%), medido en validación")
    acertar_cmd.add_argument("--detalle", action="store_true")
    acertar_cmd.add_argument("--json", action="store_true")

    estado = base("estado", "inventario del árbol: qué hay, qué falta, qué no agrupa")
    estado.add_argument("--json", action="store_true", help="emite JSON")

    validar = base("validar", f"comprueba las invariantes {rango_comprobado()}")
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

    compilar = base("compilar", "genera la vista plana de los pueblos")
    compilar.add_argument("--modo", choices=("symlink", "copia"))
    compilar.add_argument("--destino", type=Path)
    compilar.add_argument("--seco", action="store_true", help="describe cambios sin escribir")
    compilar.add_argument("--nicho", help="aplana solo las skills del nicho indicado")

    arrancar = base("arrancar", "deja un árbol nuevo o recién clonado en verde: compila, genera lo que falte y valida")
    arrancar.add_argument("--modo", choices=("symlink", "copia"))
    arrancar.add_argument("--destino", type=Path)
    arrancar.add_argument("--nicho", help="aplana solo las skills del nicho indicado")

    base("mapa", "muestra el árbol completo para inspección")

    engancha = subparsers.add_parser("enganchar", help="instala el gate de pre-commit en este repositorio")
    engancha.add_argument("--config", type=Path, default=Path("cosmos.toml"), help="ruta de cosmos.toml")
    engancha.add_argument("--sin-pruebas", action="store_true", help="el hook omitirá las suites de tests")
    engancha.add_argument(
        "--sesion",
        action="store_true",
        help="además, cablea los guardarraíles de sesión (SessionStart, Stop, PreToolUse...)",
    )

    desengancha = subparsers.add_parser("desenganchar", help="quita el gate de pre-commit")
    desengancha.add_argument("--config", type=Path, default=Path("cosmos.toml"), help="ruta de cosmos.toml")

    saltar = subparsers.add_parser("saltar", help="válvula de escape acotada, con motivo y caducidad")
    saltar.add_argument(
        "codigo", nargs="?",
        help=f"código concreto a saltar ({rango_comprobado()}, G01..G05)",
    )
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
) -> int:
    destino = args.destino.resolve() if args.destino else config.destino_compilacion
    modo = args.modo or config.modo_compilacion
    explicitos = [args.nicho] if args.nicho else None
    nichos = normalizar_nichos(arbol, _nichos(explicitos, config))
    config_efectiva = replace(config, destino_compilacion=destino, modo_compilacion=modo, nichos=nichos)
    # La válvula también vale aquí: si no, un salto legítimo dejaría el árbol en
    # verde para `validar` y en rojo para `compilar`, y el gate corre `arrancar`.
    saltados = _codigos_saltados(_saltos(config)[0])
    # E19 es lo que este comando repara; E15 es lo que NO puede reparar —`compilar`
    # no escribe el índice— y por eso no puede bloquearle ni antes ni después
    # (NUCLEO §6). Exigirla en el paso posterior era la otra mitad del
    # interbloqueo de F11: `compilar` mandaba a `generar` por E15 y `generar`
    # mandaba a `compilar` por E19. `validar` sigue exigiéndolas las dos.
    ajenas = frozenset({"E15"}) | saltados
    previo = validar_arbol(arbol, configuracion=config_efectiva, omitir_codigos=ajenas | {"E19"})
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
    posterior = validar_arbol(arbol, configuracion=config_efectiva, omitir_codigos=ajenas)
    if not posterior.valido:
        sys.stdout.write(_informe(posterior, config))
        return 1
    return 0


def _arrancar(args: argparse.Namespace, config: Configuracion, arbol) -> int:
    """Bootstrap de un árbol nuevo o de un clon recién bajado.

    La vista plana es un artefacto generado y no se versiona, así que un clon
    limpio la tiene ausente y E19 lo canta. Esto la construye y vuelve a validar,
    que es todo lo que le faltaba al repositorio para no parecer roto (H01).

    En un árbol creado desde cero falta además el índice, y ahí `arrancar` también
    lo escribe: los dos son artefactos generados, y ninguno de los dos existe.
    """

    # `compilar` ignora E15 porque no la puede reparar; la validación final de
    # aquí sí la exige entera, así que un índice que miente sigue saliendo en rojo.
    codigo = _compilar(args, config, arbol)
    if codigo:
        sys.stdout.write("\nCOSMOS  arrancar  rojo\n")
        return codigo
    # Un índice que NO existe no puede mentir, así que escribirlo no tapa nada: es
    # el otro artefacto generado que un árbol recién creado no tiene. Sin esto,
    # `arrancar` prometía dejar el árbol en verde y terminaba en rojo por E15 en el
    # único caso que GOAL §1 vende —clonar COSMOS sobre un proyecto cualquiera—
    # (F11). Si el índice ya está, no se toca: ahí E15 sigue siendo un rojo real.
    if not config.indice.exists():
        escribir_indice(arbol, config.indice)
        sys.stdout.write(f"\nÍndice creado en {config.indice} (no existía)\n")
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
    base = _base_repositorio(config)
    ruta, estado = enganchar(base, con_pruebas=not args.sin_pruebas)
    sys.stdout.write(
        f"COSMOS  enganchar  verde\n\nHook de pre-commit {estado} en {ruta}\n"
        "Cada commit correrá 'puente.gate' sobre la instantánea del índice.\n"
    )
    if args.sesion:
        ajustes, estado_sesion = enganchar_sesion(base)
        sys.stdout.write(
            f"\nGuardarraíles de sesión {estado_sesion} en {ajustes}\n"
            "Durante la sesión: entrada medida al arrancar, no se cierra en rojo, y no se\n"
            "escribe a mano sobre las rutas de veredicto. Válvula: 'cosmos saltar G0x'.\n"
        )
    sys.stdout.write("\nSe quita todo con 'cosmos desenganchar'.\n")
    return 0


def _desenganchar(args: argparse.Namespace, config: Configuracion) -> int:
    base = _base_repositorio(config)
    ruta, estado = desenganchar(base)
    if estado == "ausente":
        sys.stdout.write(f"COSMOS  desenganchar  verde\n\nNo había hook en {ruta}; nada que quitar.\n")
    else:
        sys.stdout.write(f"COSMOS  desenganchar  verde\n\nHook {estado} de {ruta}\n")
    ajustes, estado_sesion = desenganchar_sesion(base)
    if estado_sesion == "ausente":
        return 0
    explicacion = {
        "restaurado": "devuelto byte a byte al estado anterior",
        "eliminado": "eliminado: no existía antes de enganchar",
        "podado": "sin las entradas de COSMOS (el resto lo había cambiado alguien, se conserva)",
        "ilegible": "no es JSON legible; NO se ha tocado",
    }[estado_sesion]
    sys.stdout.write(f"Cableado de sesión: {ajustes} {explicacion}\n")
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

        arbol = cargar_arbol(
            config.arbol,
            excluir=config.indice,
            excluir_directorios=(config.destino_compilacion,),
            tambien=(config.registro,) if config.registro else (),
        )
        if args.comando == "validar":
            return _validar(args, config, arbol)
        if args.comando == "medir":
            # `--config` fuera del repo resuelve `arbol` contra el directorio del propio
            # fichero: si el resultado no existe, medir cero nodos y publicar «OK, quedan
            # 4.000» era el veredicto tranquilizador sobre un árbol que no está.
            # `puente.sesion.decidir` ya rechazaba este caso; el comando, no.
            if not config.arbol.is_dir():
                print(f"COSMOS  medir  rojo\n\nla raíz del árbol no existe: {config.arbol}", file=sys.stderr)
                return 1
            nichos = normalizar_nichos(arbol, _nichos(_nichos_medicion(args), config))
            resultado_medicion = medir_casos(arbol, metodo=args.metodo or config.metodo, presupuesto=config.entrada, nichos=nichos)
            sys.stdout.write(casos_json(resultado_medicion) if args.json else formatear_casos(resultado_medicion, detalle=args.detalle))
            # El codigo de salida tiene que reflejar LO QUE LA SALIDA DECLARA en rojo.
            # Antes comparaba `entrada` mientras el texto declaraba rojo por
            # `entrada_con_agua`: imprimia «ROJO, excede en 283 tokens» y devolvia 0.
            # Un aviso que no para es lo que este proyecto existe para evitar (F05).
            # `is True` porque el veredicto es trivalente: `None` («no había nada que
            # medir») también sale 1 — un veredicto sobre nada no es un verde.
            # Y consulta la válvula, como hace `validar`. Sin esto, la misma puerta
            # quedaba abierta en un comando y cerrada en el otro: con un salto E16 vivo,
            # `cosmos validar` salía 0 diciendo «verde (1 salto activo)» y `cosmos medir`
            # salía 1 sobre el mismo árbol. Un código de salida que ignora la salida
            # acotada es una puerta sin salida, y de esas se sale rodeándolas.
            cabe = veredicto_de_presupuesto(resultado_medicion, config.entrada).cabe is True
            if not cabe:
                activos, _ = _saltos(config)
                if any(salto.codigo == INVARIANTE_PRESUPUESTO for salto in activos):
                    sys.stdout.write(
                        f"\n  Salto activo sobre {INVARIANTE_PRESUPUESTO}: el presupuesto no para "
                        f"esta ejecución. Caduca, y mientras tanto se dice aquí.\n"
                    )
                    return 0
            return 0 if cabe else 1
        if args.comando == "generar":
            destino = args.salida.resolve() if args.salida else config.indice
            saltados = _codigos_saltados(_saltos(config)[0])
            # E15 es lo que este comando repara; E19 es lo que NO puede reparar
            # —`generar` no toca la vista plana— y por eso tampoco puede bloquearle
            # (NUCLEO §6). Exigírsela cerraba el árbol nuevo en un interbloqueo:
            # `generar` mandaba a `compilar` por E19 y `compilar` mandaba a
            # `generar` por E15, y nadie llegaba nunca a verde (F11).
            propias = frozenset({"E15", "E19"}) | saltados
            previo = validar_arbol(arbol, configuracion=config, indice=destino, omitir_codigos=propias)
            if not previo.valido:
                sys.stdout.write(_informe(previo, config))
                return 1
            escribir_indice(arbol, destino)
            # Revalidar después NO es ceremonia: es lo que impide declarar verde un
            # índice que se acaba de escribir y sigue sin cuadrar con el árbol.
            posterior = validar_arbol(
                arbol, configuracion=config, indice=destino, omitir_codigos=frozenset({"E19"}) | saltados
            )
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
        if args.comando == "abrir":
            ap = abrir(arbol, args.ruta, tocando=args.tocando)
            sys.stdout.write(apertura_json(ap) if args.json else formatear_apertura(ap))
            return 0
        if args.comando == "acertar":
            pun = puntuar(arbol, cargar_encargos(args.encargos))
            val = (
                puntuar(arbol, cargar_encargos(args.validacion))
                if args.validacion and args.validacion.exists()
                else None
            )
            marca = args.validacion.with_suffix(".QUEMADO") if args.validacion else None
            contraste = Contraste(
                ajuste=pun,
                validacion=val,
                quemado=marca.read_text(encoding="utf-8") if marca and marca.exists() else None,
            )

            if args.json:
                sys.stdout.write(
                    json.dumps(contraste.como_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
                )
            elif args.detalle or val is None:
                sys.stdout.write(formatear_acierto(pun, detalle=args.detalle))
            else:
                sys.stdout.write(formatear_contraste(contraste))

            # El mínimo se exige sobre la validación: cobrar el listón con el conjunto que
            # se mira al trabajar es dejar que el examinando escriba su propio examen.
            #
            # Y si el juez no está, NO se sustituye por el otro. Antes, `--validacion` con
            # una ruta mal escrita hacía justo lo que estas líneas prohíben, en silencio:
            # el fallback tranquilizador por defecto. Un examen que no aparece no se
            # aprueba por incomparecencia.
            if args.minimo:
                if val is None:
                    print(
                        f"\n--minimo exige un conjunto de validación y no se pudo leer "
                        f"{args.validacion}. Cobrarlo sobre los encargos de ajuste sería "
                        f"dejar que el examinando escriba su propio examen.",
                        file=sys.stderr,
                    )
                    return 2
                if not val.total:
                    print(
                        f"\n--minimo exige un conjunto de validación con encargos y "
                        f"{args.validacion} está vacío.",
                        file=sys.stderr,
                    )
                    return 2
                logrado = 100 * val.aciertos / val.total
                if logrado < args.minimo:
                    print(f"\nacierto {logrado:.0f} % < mínimo exigido {args.minimo} %", file=sys.stderr)
                    return 1
            return 0
        if args.comando == "estado":
            inv = inventariar(arbol)
            sys.stdout.write(estado_json(inv) if args.json else formatear_estado(inv))
            return 0
    except ErrorConfiguracion as exc:
        print(f"COSMOS  error de configuración\n\nE00  {exc}", file=sys.stderr)
        return 2
    except NodoNoEncontrado as exc:
        print(f"COSMOS  abrir  rojo\n\n{exc}", file=sys.stderr)
        return 1
    except ErrorEncargos as exc:
        # El mismo código de salida que el examen ausente de `--minimo`: un fichero
        # de encargos que no está o no cumple su esquema es un error de uso (2), no
        # un rojo de la métrica (1) — y nunca un traceback.
        print(f"COSMOS  acertar  rojo\n\n{exc}", file=sys.stderr)
        return 2
    except (MetodoNoDisponible, ErrorCompilacion, ErrorNicho, ErrorSalto, ErrorEnganche) as exc:
        print(f"COSMOS  {args.comando}  rojo\n\n{exc}", file=sys.stderr)
        return 1
    return 2


def main() -> None:
    raise SystemExit(ejecutar())


if __name__ == "__main__":
    main()
