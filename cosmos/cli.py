"""Interfaz de línea de comandos de COSMOS."""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import sys
import tomllib
from dataclasses import replace
from pathlib import Path

from . import __version__
from .compilar import ErrorCompilacion, compilar_arbol, compilar_runtime, formatear_compilacion, manifiesto_runtime
from .generar import escribir_indice, generar_mapa
from .guardarrailes import (
    CODIGOS_GATE,
    CODIGOS_SESION,
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
from .buscar import buscar_nodos, busqueda_json, formatear_busqueda
from .juez import ErrorJuez
from .acertar import (Contraste, ErrorEncargos, Puntuacion, _lineas_del_catalogo, cargar_encargos,
                      formatear as formatear_acierto, formatear_contraste, leer_sello, puntuacion_json, puntuar,
                      ruta_sello, sellar, sello_vigente)
from .estado import (estado_json, formatear as formatear_estado, formatear_maquina, inventariar,
                     inventariar_maquina, maquina_json)
from .holdout import (cobertura, comprobar_procedencia, compromiso_del_sello, esta_dentro, esta_versionado,
                      ruta_por_defecto, solape_examen_catalogo)
from .medir import (MetodoNoDisponible, casos_json, formatear_casos, medir_casos,
                    veredicto_de_presupuesto)
from .modelo import (Arbol, Configuracion, ErrorConfiguracion, ErrorNicho, cargar_arbol, cargar_configuracion,
                     nombres_nichos, normalizar_nichos)
from .validar import (INVARIANTE_PRESUPUESTO, formatear_validacion, rango_comprobado,
                      validacion_json, validar_arbol)

# El sello del holdout real se versiona aquí; el holdout, no (spec/NUCLEO.md §11).
SELLO_POR_DEFECTO = Path("pruebas/encargos-validacion.SELLO")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cosmos", description="Organiza y valida contexto con carga perezosa.")
    # Un harness que escribe un bloque marcado en el CLAUDE.md de repositorios ajenos tiene que
    # poder decir qué versión lo escribió (revisión B-08).
    parser.add_argument("--version", action="version", version=f"cosmos {__version__}")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    def base(nombre: str, ayuda: str) -> argparse.ArgumentParser:
        sub = subparsers.add_parser(nombre, help=ayuda)
        sub.add_argument("raiz", nargs="?", type=Path, help="raíz del árbol; por defecto usa cosmos.toml")
        sub.add_argument("--config", type=Path, default=Path("cosmos.toml"), help="ruta de cosmos.toml")
        return sub

    abrir_cmd = base("abrir", "carga un nodo: su cuerpo, su estrella y por dónde seguir")
    abrir_cmd.add_argument("ruta", help="ruta cosmográfica o nombre, p.ej. 'trading/estrategia/backtesting' o solo 'backtesting'")
    abrir_cmd.add_argument(
        "--tocando",
        metavar="FICHERO",
        help="ruta del fichero que se va a tocar: lista el agua que lo moja de verdad",
    )
    abrir_cmd.add_argument("--json", action="store_true", help="emite JSON")

    # Sin el posicional `raiz` de base(): con dos posicionales, la primera palabra de la
    # consulta se leia como raiz del arbol y la busqueda corria sobre un directorio inventado.
    buscar_cmd = subparsers.add_parser("buscar", help="encuentra el nodo por intención: el mismo motor con el que se mide el acierto")
    buscar_cmd.add_argument("consulta", nargs="+", help="lo que se busca, en lenguaje natural, sin comillas")
    buscar_cmd.add_argument("--config", type=Path, default=Path("cosmos.toml"), help="ruta de cosmos.toml")
    buscar_cmd.add_argument("--limite", type=int, default=5, help="cuántos resultados (por defecto 5)")
    buscar_cmd.add_argument("--json", action="store_true", help="emite JSON")

    acertar_cmd = base("acertar", "¿el catálogo lleva a la herramienta correcta? La contra-métrica")
    acertar_cmd.add_argument("--encargos", type=Path, default=Path("pruebas/encargos.json"))
    acertar_cmd.add_argument(
        "--validacion",
        type=Path,
        default=None,
        help="encargos que NO guían decisiones: la cifra honesta sale de aquí. Vive FUERA del "
             "repositorio (por defecto ~/.cosmos/holdout/encargos-validacion.json o $COSMOS_HOLDOUT): "
             "quien tiene el repo no puede tener el examen",
    )
    acertar_cmd.add_argument(
        "--sello", type=Path, default=None,
        help="el .SELLO versionado que ata el holdout (por defecto pruebas/encargos-validacion.SELLO; "
             "con --validacion explícita, el .SELLO al lado del fichero)",
    )
    acertar_cmd.add_argument("--detalle", action="store_true")
    acertar_cmd.add_argument("--json", action="store_true")
    acertar_cmd.add_argument("--sellar", action="store_true",
                             help="sella el conjunto de validación: su detalle por encargo deja de enseñarse")
    acertar_cmd.add_argument("--procedencia", default="",
                             help="con --sellar: quién escribió el examen y en qué condiciones (obligatorio)")
    acertar_cmd.add_argument("--juez", metavar="MODELO",
                             help="puntúa con un modelo local ya servido por ollama (no arranca ninguno)")
    acertar_cmd.add_argument("--servidor", default="http://localhost:11434",
                             help="URL del servidor de modelos (por defecto, ollama local)")

    estado = base("estado", "inventario del árbol: qué hay, qué falta, qué no agrupa; --maquina: qué falta en ESTA máquina")
    estado.add_argument("--json", action="store_true", help="emite JSON")
    estado.add_argument("--maquina", action="store_true",
                        help="inventario de la máquina, trivalente (ok / falta / no_comprobado): python3, git, claude, "
                             "tmux, llavero, perfil, credenciales, autonomía, vigilante de modelos, lanzador")

    validar = base("validar", f"comprueba las invariantes {rango_comprobado()}")
    validar.add_argument("--json", action="store_true", help="emite JSON")
    validar.add_argument("--indice", type=Path, help="ruta del índice que se compara")
    validar.add_argument("--nicho", action="append", help="nicho activo; anula [nichos] activos")

    medir = base("medir", "mide el contexto de entrada y el árbol")
    medir.add_argument("--metodo", choices=("aprox", "exacto"), help="solo inspección; validar usa cosmos.toml")
    medir.add_argument("--detalle", action="store_true")
    medir.add_argument("--json", action="store_true", help="emite JSON")
    medir.add_argument("--delta", action="store_true",
                       help="compara con el árbol de HEAD: qué contenido se retiró o creció para que el veredicto sea el que es (R-05)")
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
    compilar.add_argument("--detalle", action="store_true", help="lista cada entrada (sin esto, solo el resumen)")
    compilar.add_argument("--quiet", "-q", action="store_true", help="sin salida si todo va bien; solo el código de salida")
    compilar.add_argument("--todos", action="store_true",
                          help="aplana TODOS los pueblos aunque el destino sea un directorio que el runtime escanea (A-02)")

    arrancar = base("arrancar", "deja un árbol nuevo o recién clonado en verde: compila, genera lo que falte y valida")
    arrancar.add_argument("--modo", choices=("symlink", "copia"))
    arrancar.add_argument("--destino", type=Path)
    arrancar.add_argument("--nicho", help="aplana solo las skills del nicho indicado")
    arrancar.add_argument("--detalle", action="store_true", help="lista cada entrada compilada (sin esto, solo el resumen)")
    arrancar.add_argument("--quiet", "-q", action="store_true", help="sin salida si todo va bien; solo el código de salida")
    arrancar.add_argument("--todos", action="store_true",
                          help="aplana TODOS los pueblos aunque el destino sea un directorio que el runtime escanea (A-02)")

    base("mapa", "muestra el árbol completo para inspección. CARO: cuesta más que el recorrido guiado entero "
                 "('cosmos medir' da la cifra de hoy); para navegar usa 'buscar' y 'abrir'")

    proyectar = subparsers.add_parser(
        "proyectar",
        help="lleva los oficios elegidos a un repositorio ajeno: iniciar → planeta.toml → sincronizar → comprobar",
        add_help=False,
    )

    configurar = subparsers.add_parser(
        "configurar",
        help="el alta: qué oficios usas, qué herramientas de cada uno, y las credenciales que hacen falta "
             "(perfil y claves FUERA del repositorio, en ~/.cosmos)",
    )
    configurar.add_argument("--config", type=Path, default=Path("cosmos.toml"), help="ruta de cosmos.toml")
    configurar.add_argument("--oficios", help="oficios activos separados por comas (sin esto se pregunta)")
    configurar.add_argument("--herramientas", help="herramientas separadas por comas (sin esto se pregunta por oficio)")
    configurar.add_argument("--directorio", type=Path, default=None,
                            help="dónde viven el perfil y las credenciales (por defecto ~/.cosmos)")
    configurar.add_argument("--no-abrir", action="store_true", help="no abrir el fichero de credenciales en el editor")
    configurar.add_argument("--comprobar", action="store_true",
                            help="segunda vuelta: lee credenciales.txt, dice qué falta o parece un marcador, y se lo queda")
    configurar.add_argument("--llavero", action="store_true",
                            help="pasa las credenciales al llavero de macOS (security add-generic-password) y vacía el txt")
    configurar.add_argument("--seco", action="store_true",
                            help="con --llavero, --autonomia o --modelos: enseña lo que haría sin escribir nada")
    # Las tres caras de MÁQUINA del alta (ajustes de usuario del runtime, no del repositorio).
    configurar.add_argument("--autonomia", nargs="?", const="estado", choices=("estado", "auto", "libre", "manual"),
                            metavar="GRADO",
                            help="fija en los ajustes de USUARIO cómo arranca el runtime: 'auto' (sin preguntas, con "
                                 "clasificador), 'libre' (sin comprobación ninguna) o 'manual' (deshace y deja el fichero "
                                 "como estaba); sin valor, dice el grado vigente")
    configurar.add_argument("--modelos", choices=("instalar", "estado", "quitar"), metavar="ACCION",
                            help="el vigilante que mantiene todos los modelos en el selector del runtime: "
                                 "instalar | estado | quitar (solo escribe en ~/.cosmos, ~/.local/bin y, en macOS, "
                                 "~/Library/LaunchAgents)")
    configurar.add_argument("--lanzador", nargs="?", const="instalar", choices=("instalar", "quitar"), metavar="ACCION",
                            help="pone 'cosmos' en el PATH (~/.local/bin/cosmos apuntando a este clon) o lo quita")
    configurar.add_argument("--forzar", action="store_true",
                            help="con --modelos instalar o --lanzador: pisa un fichero ajeno con el mismo nombre")

    instalar = subparsers.add_parser(
        "instalar",
        help="todo el alta de un Mac nuevo en un comando: arrancar + configurar (+ --autonomia, --modelos, "
             "--lanzador) y el inventario de la máquina al final",
    )
    instalar.add_argument("--config", type=Path, default=Path("cosmos.toml"), help="ruta de cosmos.toml")
    instalar.add_argument("--oficios", help="oficios activos separados por comas (sin esto se pregunta)")
    instalar.add_argument("--herramientas", help="herramientas separadas por comas (sin esto se pregunta por oficio)")
    instalar.add_argument("--directorio", type=Path, default=None, help="dónde viven perfil y credenciales (por defecto ~/.cosmos)")
    instalar.add_argument("--no-abrir", action="store_true", help="no abrir el fichero de credenciales en el editor")
    instalar.add_argument("--autonomia", choices=("auto", "libre"), metavar="GRADO",
                          help="además, fija el grado de autonomía de la máquina (auto | libre)")
    instalar.add_argument("--modelos", action="store_true", help="además, instala el vigilante de modelos")
    instalar.add_argument("--lanzador", action="store_true", help="además, pone 'cosmos' en el PATH")
    instalar.add_argument("--forzar", action="store_true", help="pisa un maxcode/ultracode/cosmos ajeno")
    instalar.add_argument("--seco", action="store_true", help="enseña lo que haría en la máquina sin escribir")

    engancha = subparsers.add_parser("enganchar", help="instala el gate de pre-commit y el escaneo de secretos de pre-push en este repositorio")
    engancha.add_argument("--config", type=Path, default=Path("cosmos.toml"), help="ruta de cosmos.toml")
    engancha.add_argument("--sin-pruebas", action="store_true", help="el hook omitirá las suites de tests")
    engancha.add_argument(
        "--sesion",
        action="store_true",
        help="además, cablea los guardarraíles de sesión (SessionStart, Stop, PreToolUse...)",
    )

    desengancha = subparsers.add_parser("desenganchar", help="quita el gate de pre-commit, el pre-push y el cableado de sesión")
    desengancha.add_argument("--config", type=Path, default=Path("cosmos.toml"), help="ruta de cosmos.toml")

    saltar = subparsers.add_parser("saltar", help="válvula de escape acotada, con motivo y caducidad")
    # Los tres grupos de códigos se componen desde la fuente (revisión B-06: la ayuda decía
    # «G01..G05» con P01/P02 existiendo, igual que antes dijo «E00-E19» con E20 viva).
    saltar.add_argument(
        "codigo", nargs="?",
        help=f"código concreto a saltar ({rango_comprobado()}, {CODIGOS_SESION[0]}..{CODIGOS_SESION[-1]}, "
             f"{', '.join(CODIGOS_GATE)})",
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
    """Lee `[nichos] activos` de un `cosmos.toml`. Lista vacía o sección ausente: `None`.

    Delegado en `modelo.cargar_configuracion` (ciclo 2): había DOS lectores del mismo TOML con
    validación distinta, y el de la librería no leía la sección. Se conserva la función porque
    los tests y el CLI la usan por nombre.
    """

    if ruta is None or not Path(ruta).is_file():
        return None
    return list(cargar_configuracion(ruta).nichos or ()) or None


def _perfil_local() -> dict:
    """El perfil de `cosmos configurar` (~/.cosmos/perfil.toml, o COSMOS_PERFIL), si existe."""

    from .configurar import PERFIL, leer_perfil

    ruta = Path(os.environ["COSMOS_PERFIL"]).expanduser() if os.environ.get("COSMOS_PERFIL") else PERFIL
    return leer_perfil(ruta) or {}


def _nichos(explicitos: list[str] | None, config: Configuracion) -> list[str] | None:
    if explicitos:
        return explicitos
    del_toml = nichos_de_configuracion(config.ruta)
    if del_toml:
        return del_toml
    # Sin nichos en cosmos.toml, mandan los oficios del alta: el resto duerme (encargo B).
    oficios = [o for o in _perfil_local().get("oficios", []) if isinstance(o, str)]
    return oficios or None


def _herramientas_del_perfil() -> tuple[str, ...] | None:
    elegidas = [h for h in _perfil_local().get("herramientas", []) if isinstance(h, str)]
    return tuple(elegidas) or None


def _nichos_medicion(args: argparse.Namespace) -> list[str] | None:
    if args.nicho:
        return args.nicho
    if not args.combinacion:
        return None
    partes = [parte.strip() for parte in args.combinacion.split(",")]
    if not partes or any(not parte for parte in partes):
        raise ErrorNicho("--combinacion exige nombres no vacíos separados por comas")
    return partes


def _delta_frente_a_head(arbol: Arbol, config: Configuracion, ahora) -> str:
    """Mide el árbol tal como está en HEAD y publica la diferencia con el de trabajo.

    Revisión R-05: los 91 tokens de holgura del ciclo 1 eran los 109 que se cortaron de un
    océano, y el veredicto no lo decía. Un «cabe» que no declara qué se retiró para caber es
    la misma clase de dato que `medir` persigue. Se exporta HEAD a un temporal con
    `git archive` (sin tocar el árbol de trabajo) y se mide con el mismo medidor.
    """

    import tarfile
    import tempfile

    from .medir import contar_estructura
    from .modelo import cuerpo

    base = _base_repositorio(config)
    try:
        rel_arbol = config.arbol.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return "\n  Delta vs HEAD .. no_medido (el árbol no está dentro del repositorio)\n"
    exportado = subprocess.run(["git", "-C", str(base), "archive", "HEAD", rel_arbol], capture_output=True, check=False)
    if exportado.returncode:
        return "\n  Delta vs HEAD .. no_medido (sin HEAD o sin git)\n"
    with tempfile.TemporaryDirectory(prefix="cosmos-delta-") as tmp:
        with tarfile.open(fileobj=io.BytesIO(exportado.stdout)) as tar:
            tar.extractall(tmp, filter="data")
        antes_arbol = cargar_arbol(Path(tmp) / rel_arbol)
        antes = medir_casos(antes_arbol, metodo=config.metodo, presupuesto=config.entrada,
                            solo_anfitrion=config.vista_compilacion == "anfitrion")
        oceanos_antes = {n.nombre: contar_estructura(cuerpo(n)) for n in antes_arbol.nodos if n.cosmos == "oceano"}
    oceanos_ahora = {n.nombre: contar_estructura(cuerpo(n)) for n in arbol.nodos if n.cosmos == "oceano"}
    pueblos_antes = sum(1 for n in antes_arbol.nodos if n.cosmos == "pueblo")
    pueblos_ahora = sum(1 for n in arbol.nodos if n.cosmos == "pueblo")
    lineas = ["", "  Delta vs HEAD .. (lo que cambió para que el veredicto sea el que es)",
              f"    entrada base      {antes.base.entrada:>6} -> {ahora.base.entrada:<6} ({ahora.base.entrada - antes.base.entrada:+d})",
              f"    peor con agua     {antes.peor.entrada_con_agua:>6} -> {ahora.peor.entrada_con_agua:<6} ({ahora.peor.entrada_con_agua - antes.peor.entrada_con_agua:+d})",
              f"    pueblos           {pueblos_antes:>6} -> {pueblos_ahora:<6} ({pueblos_ahora - pueblos_antes:+d})"]
    for nombre in sorted(set(oceanos_antes) | set(oceanos_ahora)):
        a, b = oceanos_antes.get(nombre, 0), oceanos_ahora.get(nombre, 0)
        if a != b:
            lineas.append(f"    oceano/{nombre:<12} {a:>5} -> {b:<5} ({b - a:+d} tokens en TODA sesión)")
    return "\n".join(lineas) + "\n"


def _vista_compilada(arbol: Arbol, config: Configuracion) -> dict[str, object]:
    """Lo que paga un runtime que escanee el destino de la vista plana: nombre + resumen por entrada.

    Era el único gasto grande que ninguna cifra publicada veía: `arrancar` materializaba 247
    entradas (≈6.100 tokens, 1,5× el presupuesto) en un directorio que el medidor mandaba al
    saco `no_medido` (auditoría A-02). Se lee el manifiesto, no el árbol: se mide lo que HAY
    compilado, y si no hay manifiesto se dice `no_medido`, nunca cero.
    """

    from .compilar import rutas_compilacion
    from .medir import contar_generado

    destino, manifiesto = rutas_compilacion(arbol, config.destino_compilacion, config.manifiesto_compilacion, config.ruta)
    try:
        datos = json.loads(manifiesto.read_text(encoding="utf-8"))
        entradas = list(datos.get("entradas", {}))
    except (OSError, ValueError, AttributeError):
        return {"tokens": "no_medido", "entradas": 0, "destino": str(destino), "motivo": "sin manifiesto: no hay vista compilada"}
    resumenes = {n.nombre: n.resumen for n in arbol.nodos if n.cosmos == "pueblo"}
    texto = "\n".join(f"{nombre}: {resumenes.get(nombre, '')}" for nombre in entradas)
    return {"tokens": contar_generado(texto) if entradas else 0, "entradas": len(entradas), "destino": str(destino),
            "motivo": "los paga un runtime que escanee ese directorio; fuera de E16"}


def _linea_vista_compilada(vista: dict[str, object]) -> str:
    tokens = vista["tokens"]
    cifra = tokens if isinstance(tokens, str) else f"{tokens:,}".replace(",", ".") + " tokens"
    return (f"\n  Vista compilada . {cifra}   ({vista['entradas']} entradas en {vista['destino']}; "
            f"{vista['motivo']})\n")


def _configurar(args: argparse.Namespace, config: Configuracion, arbol: Arbol) -> int:
    """El alta de COSMOS en una máquina (encargo de Darío, 2026-09-03).

    1. Qué oficios se usan de verdad → esos nichos quedan activos en el perfil; el resto duerme.
    2. Por cada oficio, qué herramientas → solo esas entran en el catálogo del usuario.
    3. `~/.cosmos/credenciales.txt` con las variables que esas herramientas necesitan, ya
       puestas y vacías, cada una con la pista de dónde se saca, y se abre en el editor.
    4. `--comprobar`: se lee, se dice qué falta o parece un marcador, y se marca en el perfil.
    5. Nace con 600 en un directorio 700, FUERA del repositorio. En el repo, solo la plantilla.
    6. `--llavero`: `security add-generic-password` por cada valor y el txt se vacía.
    """

    from . import configurar as cfg

    directorio = args.directorio or cfg.DIRECTORIO
    perfil = directorio / cfg.PERFIL.name
    credenciales = directorio / cfg.CREDENCIALES.name
    oficios_disponibles = list(nombres_nichos(arbol))
    pueblos = {n.nombre: n for n in arbol.nodos if n.cosmos == "pueblo"}

    # Las caras de MÁQUINA del alta: no tocan el perfil ni las credenciales.
    if getattr(args, "autonomia", None):
        return _autonomia(args.autonomia, directorio, seco=args.seco)
    if getattr(args, "modelos", None):
        return _modelos(args.modelos, perfil, seco=args.seco, forzar=args.forzar)
    if getattr(args, "lanzador", None):
        return _lanzador(args.lanzador, config, forzar=args.forzar)

    if args.comprobar or args.llavero:
        datos = cfg.leer_perfil(perfil) or {}
        herramientas = [h for h in datos.get("herramientas", []) if isinstance(h, str)]
        oficios = [o for o in datos.get("oficios", []) if isinstance(o, str)]
        if not herramientas and not oficios:
            print(f"COSMOS  configurar  rojo\n\nno hay perfil en {perfil}: ejecuta primero 'cosmos configurar'", file=sys.stderr)
            return 2
        esperadas = cfg.credenciales_de(arbol, herramientas)
        leidas = cfg.leer_credenciales(credenciales)
        faltan, sospechosas = cfg.comprobar_credenciales(esperadas, leidas)
        if args.llavero:
            ordenes = cfg.ordenes_llavero({k: v for k, v in leidas.items() if k in {c.variable for c in esperadas}},
                                          os.environ.get("USER", "cosmos"))
            if not ordenes:
                print("COSMOS  configurar  llavero\n\nno hay ningún valor que pasar al llavero", file=sys.stderr)
                return 1
            for orden in ordenes:
                visible = orden[:-2] + ["********", orden[-1]]  # el valor nunca se imprime
                if args.seco:
                    print(" ".join(visible))
                else:
                    resultado = subprocess.run(orden, capture_output=True, check=False)
                    if resultado.returncode:
                        print(f"COSMOS  configurar  rojo\n\nno se pudo guardar {orden[5]} en el llavero", file=sys.stderr)
                        return 1
            if not args.seco:
                vaciadas = cfg.vaciar_valores(credenciales)
                print(f"COSMOS  configurar  llavero\n\n{len(ordenes)} credencial(es) en el llavero de macOS "
                      f"(servicio cosmos/<VARIABLE>); {vaciadas} valor(es) vaciados de {credenciales}.")
            return 0
        lineas = ["COSMOS  configurar  comprobar", ""]
        for variable in faltan:
            lineas.append(f"  FALTA      {variable}")
        for variable in sospechosas:
            lineas.append(f"  SOSPECHOSA {variable}   (parece un marcador o es demasiado corta)")
        completas = len({c.variable for c in esperadas}) - len(faltan) - len(sospechosas)
        lineas.append(f"  {completas} completa(s), {len(faltan)} falta(n), {len(sospechosas)} sospechosa(s) de {len({c.variable for c in esperadas})}")
        cfg.escribir_privado(perfil, cfg.perfil_toml(oficios, herramientas, comprobadas=not faltan and not sospechosas,
                                                     modelos=cfg.leer_modelos(perfil)))
        lineas.append(f"  Perfil guardado en {perfil}: no se vuelve a preguntar."
                      + (" Cuando quieras: 'cosmos configurar --llavero'." if not faltan and not sospechosas else ""))
        sys.stdout.write("\n".join(lineas) + "\n")
        return 0 if not faltan and not sospechosas else 1

    # Primera vuelta
    if args.oficios:
        oficios = [o.strip() for o in args.oficios.split(",") if o.strip()]
    else:
        print("¿Qué oficios usas de verdad? (números, nombres o 'todos'; el resto duerme)")
        oficios = cfg.elegir(oficios_disponibles, "> ")
    desconocidos = sorted(set(oficios) - set(oficios_disponibles))
    if desconocidos:
        raise ErrorNicho(f"oficio desconocido: {', '.join(desconocidos)}; disponibles: {', '.join(oficios_disponibles)}")
    if not oficios:
        print("COSMOS  configurar  rojo\n\nsin oficios no hay nada que activar", file=sys.stderr)
        return 1
    if args.herramientas:
        herramientas = [h.strip() for h in args.herramientas.split(",") if h.strip()]
    else:
        herramientas = []
        for oficio in oficios:
            de_este = sorted(n.nombre for n in pueblos.values() if (n.datos.get("padre") or "").split("/")[0] == oficio)
            if not de_este:
                continue
            print(f"\nHerramientas de {oficio} que usas (números, nombres o 'todos'):")
            herramientas.extend(cfg.elegir(de_este, "> "))
    desconocidas = sorted(set(herramientas) - set(pueblos))
    if desconocidas:
        raise ErrorEncargos(f"herramienta desconocida: {', '.join(desconocidas)}")
    fuera = sorted(h for h in herramientas if (pueblos[h].datos.get("padre") or "").split("/")[0] not in oficios)
    if fuera:
        raise ErrorEncargos(f"herramienta de un oficio que no activaste: {', '.join(fuera)}")

    cfg.escribir_privado(perfil, cfg.perfil_toml(oficios, herramientas, comprobadas=False, modelos=cfg.leer_modelos(perfil)))
    esperadas = cfg.credenciales_de(arbol, herramientas)
    if credenciales.is_file() and cfg.leer_credenciales(credenciales):
        # No se pisa un fichero con valores: se dice y se para.
        print(f"COSMOS  configurar\n\n{credenciales} ya tiene valores: no se sobrescribe. "
              "Comprueba con 'cosmos configurar --comprobar'.")
        return 0
    cfg.escribir_privado(credenciales, cfg.plantilla_credenciales(esperadas))
    lineas = [
        "COSMOS  configurar  verde", "",
        f"  Oficios activos ....... {', '.join(oficios)} ({len(oficios)} de {len(oficios_disponibles)}; el resto duerme)",
        f"  Herramientas .......... {len(herramientas)} elegidas",
        f"  Perfil ................ {perfil}  (600, fuera del repositorio)",
        f"  Credenciales .......... {credenciales}  ({len(esperadas)} variable(s) vacía(s), con su pista)",
    ]
    if esperadas:
        abierto = False if args.no_abrir else cfg.abrir_en_editor(credenciales)
        lineas.append("  Rellénalas de una sentada y vuelve con: cosmos configurar --comprobar"
                      + ("" if abierto or args.no_abrir else "   (no se pudo abrir el editor: ábrelo tú)"))
    else:
        lineas.append("  Ninguna de las herramientas elegidas pide credenciales.")
    sys.stdout.write("\n".join(lineas) + "\n")

    # Solo en el alta INTERACTIVA se pregunta por la máquina. Con --oficios/--herramientas (un
    # script) no se toca ningún ajuste de usuario sin un --autonomia explícito: un sistema que
    # se engancha sin que se lo pidan se arranca de raíz a la primera molestia.
    if not args.oficios and not args.herramientas:
        grado, detalle = cfg.grado_vigente()
        print(f"\n¿Esta máquina trabaja sin pedir permiso? Hoy: {grado} ({detalle}).")
        respuesta = input("  auto (recomendado) / libre / no [Enter = auto]: ").strip().lower()
        elegido = {"": "auto", "auto": "auto", "libre": "libre"}.get(respuesta)
        if elegido:
            _autonomia(elegido, directorio, seco=False)
        else:
            print("  Se deja como está.")
        respuesta = input("¿Instalar el vigilante que mantiene todos los modelos en /model? [s/N]: ").strip().lower()
        if respuesta in {"s", "si", "sí"}:
            _modelos("instalar", perfil, seco=False, forzar=False)
    return 0


def _autonomia(grado: str, directorio: Path, *, seco: bool) -> int:
    """El grado de autonomía de la máquina, en los ajustes de USUARIO del runtime (A §2)."""

    from . import configurar as cfg

    ruta = cfg.ajustes_usuario()
    respaldo = directorio / cfg.RESPALDO_AUTONOMIA.name
    ambito = "CLAUDE_CONFIG_DIR" if os.environ.get("CLAUDE_CONFIG_DIR") else "ámbito usuario; CLAUDE_CONFIG_DIR sin definir"
    vigente, detalle = cfg.grado_vigente(ruta)
    ruta_corta, respaldo_corto = cfg.abreviar_home(ruta), cfg.abreviar_home(respaldo)
    if grado == "estado":
        sys.stdout.write(f"COSMOS  configurar  autonomia  {vigente}\n\n  {ruta_corta}  ({ambito})\n  {cfg.abreviar_home(detalle)}\n")
        if vigente in ("manual", "desconocido"):
            sys.stdout.write("  Para que no pida permiso: cosmos configurar --autonomia auto   (o libre)\n")
        return 0
    if grado == "manual":
        estado, ajenas = cfg.retirar_autonomia(ruta, respaldo)
        explicacion = {
            "ausente": "COSMOS no había escrito nada aquí: nada que deshacer",
            "restaurado": "devuelto byte a byte al estado anterior",
            "eliminado": "eliminado: no existía antes de fijar la autonomía",
            "podado": "sin las claves de COSMOS (el resto lo había cambiado alguien, se conserva)",
            "ilegible": "no es JSON legible; NO se ha tocado",
        }[estado]
        sys.stdout.write(f"COSMOS  configurar  autonomia  manual\n\n  {ruta_corta}: {explicacion}\n")
        for clave in ajenas:
            sys.stdout.write(f"  {clave}: alguien la cambió a mano después; no se toca\n")
        return 0
    claves = cfg.GRADOS[grado]
    if seco:
        sys.stdout.write(f"COSMOS  configurar  autonomia  {grado}  (seco)\n\n  Escribiría en {ruta_corta} ({ambito}):\n")
        sys.stdout.write("".join(f"    {clave} = {json.dumps(valor)}\n" for clave, valor in claves.items()))
        sys.stdout.write("  Por sesión, sin tocar ajustes: claude --permission-mode "
                         f"{'bypassPermissions' if grado == 'libre' else 'auto'}\n")
        return 0
    try:
        informe = cfg.fijar_autonomia(grado, ruta, respaldo)
    except ValueError as exc:
        print(f"COSMOS  configurar  rojo\n\n{exc}", file=sys.stderr)
        return 1
    lineas = [f"COSMOS  configurar  autonomia  {grado}", "", f"  Escrito en {ruta_corta}  ({ambito})"]
    for clave, valor, estado in informe:
        nota = "   (clave no documentada del runtime)" if clave == "skipDangerousModePermissionPrompt" else ""
        lineas.append(f"    {clave:<34} = {json.dumps(valor):<20} ({estado}){nota}")
    lineas.append(f"  Respaldo del fichero anterior en {respaldo_corto}")
    lineas.append("  Vuelta atrás: cosmos configurar --autonomia manual")
    if grado == "libre":
        lineas.append("  Ojo: bypassPermissions apaga también el clasificador que revisa `rm` en rutas críticas.")
    lineas.append("  La primera sesión interactiva en una carpeta nueva sigue pidiendo confianza: eso no se escribe por debajo.")
    sys.stdout.write("\n".join(lineas) + "\n")
    return 0


def _modelos(accion: str, perfil: Path, *, seco: bool, forzar: bool) -> int:
    """El vigilante de modelos (puente/modelos.py): instalar | estado | quitar."""

    from puente import modelos as mod
    from . import configurar as cfg

    tabla = cfg.leer_modelos(perfil)
    if accion == "estado":
        filas = mod.estado(perfil=tabla)
        sys.stdout.write(f"COSMOS  configurar  modelos  estado\n\n{mod.formatear(filas)}\n")
        return 0
    if accion == "quitar":
        lineas = mod.quitar()
        sys.stdout.write("COSMOS  configurar  modelos  quitar\n\n" + "\n".join(lineas) + "\n")
        return 0
    try:
        lineas = mod.instalar(perfil=tabla, seco=seco, forzar=forzar)
    except ValueError as exc:
        print(f"COSMOS  configurar  rojo\n\n{exc}", file=sys.stderr)
        return 1
    titulo = "COSMOS  configurar  modelos  instalar" + ("  (seco)" if seco else "")
    sys.stdout.write(f"{titulo}\n\n" + "\n".join(lineas) + "\n")
    if not seco:
        sys.stdout.write("  Se quita todo con: cosmos configurar --modelos quitar\n")
    return 0


def _lanzador(accion: str, config: Configuracion, *, forzar: bool) -> int:
    from . import configurar as cfg

    if accion == "quitar":
        ruta, estado = cfg.quitar_lanzador()
        texto = {"ausente": "no había lanzador", "ajeno": f"{ruta} no es nuestro: no se toca", "eliminado": f"{ruta} eliminado"}[estado]
        sys.stdout.write(f"COSMOS  configurar  lanzador  quitar\n\n  {texto}\n")
        return 0
    raiz = _base_repositorio(config).resolve()
    ruta, estado = cfg.instalar_lanzador(raiz, forzar=forzar)
    if estado == "ajeno":
        print(f"COSMOS  configurar  lanzador  aviso\n\n  {cfg.abreviar_home(ruta)} existe y no es nuestro: no se toca (--forzar para pisarlo)", file=sys.stderr)
        return 1
    lineas = [f"COSMOS  configurar  lanzador  {estado}", "", f"  {cfg.abreviar_home(ruta)} -> python3 -m cosmos en {cfg.abreviar_home(raiz)}"]
    if not cfg.en_el_path(ruta):
        lineas.append(f"  Ojo: {cfg.abreviar_home(ruta.parent)} no está en el PATH de esta terminal; añádelo a tu shell.")
    lineas.append("  Se quita con: cosmos configurar --lanzador quitar")
    sys.stdout.write("\n".join(lineas) + "\n")
    return 0


def _instalar(args: argparse.Namespace, config: Configuracion, arbol: Arbol) -> int:
    """Todo el alta de una máquina nueva en un comando, delegando en los verbos que ya existen.

    `git clone` y luego esto: nada de `curl | bash`. Lo que se ejecuta está en disco y ha pasado
    por el índice, el escáner y el gate (GOAL §5: cero red en el camino crítico).
    """

    from . import configurar as cfg

    sys.stdout.write("== 1/4  arrancar: vista plana e índice ==\n")
    if args.seco:
        sys.stdout.write("  (seco) python3 -m cosmos arrancar\n")
    else:
        args_arrancar = argparse.Namespace(modo=None, destino=None, nicho=None, detalle=False, quiet=False, todos=False)
        codigo = _arrancar(args_arrancar, config, arbol)
        if codigo:
            sys.stdout.write("\nCOSMOS  instalar  rojo  (arrancar no dejó el árbol en verde; se para aquí)\n")
            return codigo
    sys.stdout.write("\n== 2/4  configurar: oficios, herramientas y credenciales ==\n")
    if args.seco:
        sys.stdout.write("  (seco) python3 -m cosmos configurar  (pregunta oficios y herramientas; abre ~/.cosmos/credenciales.txt)\n")
    else:
        args_cfg = argparse.Namespace(directorio=args.directorio, no_abrir=args.no_abrir, comprobar=False, llavero=False,
                                      seco=False, oficios=args.oficios or "", herramientas=args.herramientas or "",
                                      autonomia=None, modelos=None, lanzador=None, forzar=False)
        # Con oficios por bandera el alta es no interactiva y no pregunta por la máquina: eso lo
        # deciden los flags de instalar. Sin banderas, `configurar` pregunta lo suyo y también por
        # la máquina, y entonces los flags no se repiten.
        codigo = _configurar(args_cfg, config, arbol)
        if codigo:
            return codigo
    directorio = args.directorio or cfg.DIRECTORIO
    perfil = directorio / cfg.PERFIL.name
    interactivo = not args.oficios and not args.herramientas
    sys.stdout.write("\n== 3/4  la máquina: autonomía, modelos, lanzador ==\n")
    if args.autonomia and not (interactivo and not args.seco):
        _autonomia(args.autonomia, directorio, seco=args.seco)
    if args.modelos and not (interactivo and not args.seco):
        _modelos("instalar", perfil, seco=args.seco, forzar=args.forzar)
    if args.lanzador:
        if args.seco:
            sys.stdout.write(f"  (seco) lanzador en {cfg.LANZADOR}\n")
        else:
            _lanzador("instalar", config, forzar=args.forzar)
    if not (args.autonomia or args.modelos or args.lanzador):
        sys.stdout.write("  Nada pedido (--autonomia, --modelos, --lanzador): la máquina se queda como está.\n")
    sys.stdout.write("\n== 4/4  estado de la máquina ==\n")
    filas = inventariar_maquina(arbol, directorio=directorio, raiz_clon=_base_repositorio(config).resolve())
    sys.stdout.write(formatear_maquina(filas))
    return 0


def _base_repositorio(config: Configuracion) -> Path:
    return config.ruta.parent if config.ruta is not None else config.arbol


def _contrastar(arbol: Arbol, ajuste: Puntuacion, validacion: Path, sello: Path | None, raiz: Path,
                config_arbol: Path | None = None) -> Contraste:
    """Arma el contraste con todo lo que decide si la cifra de validación vale.

    Cuatro comprobaciones, y ninguna es cosmética (auditoría B-01..B-07):
    · el holdout existe y se lee, o se dice por qué no — nunca se sustituye por el ajuste;
    · **no está versionado** en este repositorio ni sus consultas aparecen en la historia
      git de ningún `.json`: un examen que viaja con el sistema que evalúa —aunque sea en
      un commit borrado— lo tiene cualquiera que clone, y eso es un ejercicio resuelto;
    · el sello está vigente (o se dice si está roto o nunca se puso) y declara procedencia;
    · la cobertura de oficios y de profundidad se publica junto a la cifra.
    """

    if not validacion.is_file():
        return Contraste(ajuste=ajuste, validacion=None,
                         ausente=f"no existe {validacion} (fuera del repositorio a propósito; "
                                 "COSMOS_HOLDOUT o --validacion para otra ruta)")
    encargos = cargar_encargos(validacion)
    val = puntuar(arbol, encargos)
    marca = validacion.with_suffix(".QUEMADO")
    quemado = marca.read_text(encoding="utf-8") if marca.is_file() else None
    # Trivalente (R-17): fuera del repositorio no hay nada que versionar (False, sabido);
    # dentro, lo dice git; y si git no contesta, `None`, que se publica como tal.
    versionado: bool | None = esta_versionado(raiz, validacion) if esta_dentro(raiz, validacion) else False
    datos_sello = leer_sello(validacion, sello)
    vigente = sello_vigente(validacion, sello)
    lineas = dict(_lineas_del_catalogo(arbol))
    return Contraste(
        ajuste=ajuste,
        validacion=val,
        quemado=quemado or None,
        sellado=vigente,
        sello_roto=datos_sello is not None and not vigente,
        procedencia=comprobar_procedencia(raiz, [e.peticion for e in encargos]),
        cobertura=cobertura(nombres_nichos(arbol), [e.espera for e in encargos]),
        declarada=str((datos_sello or {}).get("procedencia") or ""),
        compromiso=(compromiso_del_sello(raiz, ruta_sello(validacion, sello), str(datos_sello.get("sha256", "")), config_arbol)
                    if datos_sello else None),
        calcado=solape_examen_catalogo((e.peticion, lineas.get(e.espera, "")) for e in encargos),
        calcado_ajuste=solape_examen_catalogo((r.encargo.peticion, lineas.get(r.encargo.espera, "")) for r in ajuste.resultados),
        versionado=versionado,
        candidatos=len(lineas),
    )


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
    # E22 (runtime generado) es lo otro que este comando repara: tampoco puede bloquearle antes.
    previo = validar_arbol(arbol, configuracion=config_efectiva, omitir_codigos=ajenas | {"E19", "E22"})
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
        todos=True if getattr(args, "todos", False) else None,
        herramientas=config.herramientas,
        solo_anfitrion=config.vista_compilacion == "anfitrion",
    )
    if not getattr(args, "quiet", False):
        sys.stdout.write(anotar_salida(
            formatear_compilacion(compilacion, detalle=bool(getattr(args, "detalle", False))), _saltos(config)[0]
        ))
    # Los otros ficheros de runtime (reglas, agentes, comandos), solo si cosmos.toml los declara.
    for tipo, destino_runtime in (("rules", config.rules_compilacion), ("agentes", config.agentes_compilacion),
                                  ("comandos", config.comandos_compilacion)):
        if destino_runtime is None:
            continue
        resultado_runtime = compilar_runtime(arbol, tipo, destino_runtime, manifiesto_runtime(config, tipo), seco=seco)
        if not getattr(args, "quiet", False):
            sys.stdout.write(
                f"  {tipo:<9} {os.path.relpath(destino_runtime)}: "
                f"creadas {resultado_runtime.creadas}; actualizadas {resultado_runtime.actualizadas}; "
                f"iguales {resultado_runtime.iguales}; adoptadas {resultado_runtime.adoptadas}; "
                f"ajenas respetadas {resultado_runtime.ajenas}; obsoletas eliminadas {resultado_runtime.eliminadas}; "
                f"preservadas {resultado_runtime.preservadas}.\n"
            )
    if nichos is None and not seco and not getattr(args, "quiet", False):
        # `nichos=None` aquí significa TODOS los pueblos (NUCLEO §5), al revés que en el
        # catálogo de entrada, donde significa ninguno (NUCLEO §2). Se dice cada vez que se
        # materializa la vista completa: si un runtime escanea `destino`, paga el resumen de
        # cada entrada, y eso no lo mide E16 (auditoría A-02 / A-04).
        cuantos = compilacion.creadas + compilacion.actualizadas + compilacion.iguales + compilacion.adoptadas
        sys.stdout.write(
            f"(vista COMPLETA: {cuantos} pueblos de todos los nichos; acótala con --nicho o "
            "[nichos] activos si un runtime escanea el destino)\n"
        )
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

    # Un árbol recién creado no tiene galaxia, y sin ella E05 deja `arrancar` en rojo
    # cuando NUCLEO §6 promete que «es el único que deja un árbol nuevo en verde de una
    # vez» (auditoría E-08). Una galaxia que no existe no puede mentir, como el índice:
    # se escribe la mínima, con el nombre del directorio, y se dice. Si hay nodos pero
    # ninguna galaxia, no se inventa nada: ese árbol tiene un problema que E05 debe decir.
    if not arbol.nodos and config.arbol.is_dir() and not any(config.arbol.rglob("*.md")):
        nombre = re.sub(r"[^a-z0-9-]+", "-", config.arbol.resolve().name.lower()).strip("-") or "galaxia"
        galaxia = config.arbol / "galaxia.md"
        galaxia.write_text(
            f"---\ncosmos: galaxia\nnombre: {nombre}\nresumen: Nada se carga hasta entrar en ello.\n---\n\n"
            "El indice nombra a los hijos; no los describe. Cada oficio es un sistema solar con "
            "`padre: \"\"`.\n",
            encoding="utf-8",
        )
        sys.stdout.write(f"Galaxia creada en {galaxia} (no existía): edita su nombre y su resumen\n\n")
        arbol = cargar_arbol(config.arbol, excluir=config.indice,
                             excluir_directorios=(config.destino_compilacion,),
                             tambien=(config.registro,) if config.registro else ())
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
    argumentos = list(sys.argv[1:] if argv is None else argv)
    if argumentos and argumentos[0] == "proyectar":
        # El mecanismo que cumple GOAL §1 («clonar sobre cualquier proyecto») no era un
        # verbo y no salía en el README: solo se descubría hurgando en `galaxia/agua/`
        # (auditoría E-04). Delega entero en `puente.proyectar`, `--help` incluido.
        from puente.proyectar import main as proyectar_main

        return proyectar_main(argumentos[1:])
    args = _parser().parse_args(argumentos)
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
        # La guarda de «la raíz del árbol no existe» se escribió para `medir` y `buscar`
        # y `estado`/`mapa` seguían dando verde con un inventario vacío sobre un árbol que
        # no está (auditoría D-05). Aquí, para los cuatro; `validar` ya lo dice con E00.
        if not config.arbol.is_dir():
            # UNA guarda para todos los verbos que cargan el árbol (R-44): `acertar` publicaba «lo
            # ganado generaliza» sobre cero nodos, y `medir`/`buscar` tenían cada uno su copia
            # («arreglar el que se ve y dejar al hermano»). `validar` lo dice con E00.
            # `--config` fuera del repo resuelve `arbol` contra el directorio del propio fichero:
            # medir cero nodos y publicar «OK, quedan 4.000» era el veredicto tranquilizador.
            if args.comando != "validar":
                print(f"COSMOS  {args.comando}  rojo\n\nla raíz del árbol no existe: {config.arbol}", file=sys.stderr)
                return 1
        if args.comando == "configurar":
            return _configurar(args, config, arbol)
        if args.comando == "instalar":
            return _instalar(args, config, arbol)
        if args.comando == "validar":
            return _validar(args, config, arbol)
        if args.comando == "medir":
            nichos = normalizar_nichos(arbol, _nichos(_nichos_medicion(args), config))
            resultado_medicion = medir_casos(arbol, metodo=args.metodo or config.metodo, presupuesto=config.entrada,
                                             nichos=nichos, herramientas=_herramientas_del_perfil(),
                                             solo_anfitrion=config.vista_compilacion == "anfitrion")
            vista = _vista_compilada(arbol, config)
            if args.json:
                datos = json.loads(casos_json(resultado_medicion))
                datos["vista_compilada"] = vista
                sys.stdout.write(json.dumps(datos, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
            else:
                sys.stdout.write(formatear_casos(resultado_medicion, detalle=args.detalle))
                sys.stdout.write(_linea_vista_compilada(vista))
                if args.delta:
                    sys.stdout.write(_delta_frente_a_head(arbol, config, resultado_medicion))
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
        if args.comando == "buscar":
            consulta = " ".join(args.consulta)
            hallazgos = buscar_nodos(arbol, consulta, limite=args.limite)
            sys.stdout.write(busqueda_json(hallazgos, consulta) if args.json else formatear_busqueda(hallazgos, consulta))
            # Sin resultados no es un error del comando, pero sí una búsqueda que no
            # encontró: salida 1, para que un guion que dependa del hallazgo se entere.
            return 0 if hallazgos else 1
        if args.comando == "abrir":
            ap = abrir(arbol, args.ruta, tocando=args.tocando)
            sys.stdout.write(apertura_json(ap) if args.json else formatear_apertura(ap))
            return 0
        if args.comando == "acertar":
            explicita = args.validacion is not None
            validacion = args.validacion if explicita else ruta_por_defecto()
            sello = args.sello if args.sello is not None else (
                None if explicita else SELLO_POR_DEFECTO
            )
            if args.sellar:
                if not args.procedencia.strip():
                    raise ErrorEncargos(
                        "--sellar exige --procedencia: quién escribió el examen y en qué condiciones "
                        "(el primero lo escribió quien ajusta el árbol, con el árbol delante, y solo "
                        "se supo leyendo el registro)"
                    )
                datos = sellar(validacion, sello, procedencia=args.procedencia)
                print(
                    f"COSMOS  acertar  holdout sellado\n\n"
                    f"{validacion}: {datos['encargos']} encargos, sha256 {datos['sha256'][:12]}…\n"
                    f"sello en {ruta_sello(validacion, sello)}\n"
                    "Desde ahora su detalle por encargo no se enseña. Editar el fichero invalida el\n"
                    "sello; romperlo es borrar el .SELLO, y ese gesto queda en git."
                )
                return 0
            if args.juez:
                from .juez import formatear_juicio, juzgar

                encargos_ajuste = cargar_encargos(args.encargos)
                juicio = juzgar(arbol, encargos_ajuste, modelo=args.juez, servidor=args.servidor)
                sys.stdout.write(formatear_juicio(juicio, puntuar(arbol, encargos_ajuste), args.juez))
                return 0
            pun = puntuar(arbol, cargar_encargos(args.encargos))
            contraste = _contrastar(arbol, pun, validacion, sello, _base_repositorio(config), config.arbol)

            if args.json:
                sys.stdout.write(
                    json.dumps(contraste.como_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
                )
            elif args.detalle:
                # El detalle solo enseña el AJUSTE: el de validación es lo que quema.
                sys.stdout.write(formatear_acierto(pun, detalle=True))
            else:
                sys.stdout.write(formatear_contraste(contraste))

            # No hay `--minimo` (auditoría R-01): un listón sobre una cifra que describe al
            # que escribió el examen y no al árbol es un listón que se aprueba escribiendo el
            # examen. Cuando exista un compromiso previo verificable, se reabrirá aquí.
            return 0
        if args.comando == "estado":
            if args.maquina:
                filas = inventariar_maquina(arbol, raiz_clon=_base_repositorio(config).resolve())
                sys.stdout.write(maquina_json(filas) if args.json else formatear_maquina(filas))
                return 0
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
    except ErrorJuez as exc:
        print(f"COSMOS  acertar  sin juez\n\n{exc}", file=sys.stderr)
        return 2
    except (MetodoNoDisponible, ErrorCompilacion, ErrorNicho, ErrorSalto, ErrorEnganche) as exc:
        print(f"COSMOS  {args.comando}  rojo\n\n{exc}", file=sys.stderr)
        return 1
    return 2


def main() -> None:
    raise SystemExit(ejecutar())


if __name__ == "__main__":
    main()
