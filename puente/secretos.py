#!/usr/bin/env python3
"""Escanea los blobs del índice Git sin mostrar valores ni seguir enlaces."""

from __future__ import annotations

import argparse
import csv
import os
import re
import subprocess
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from cosmos.guardarrailes import clave_hallazgo

from .etiquetas import etiqueta_de_ruta

# Rutas que COSMOS genera o que son locales por definición: si aparecen en el
# índice, alguien versionó un artefacto o una configuración de su máquina.
DIRECTORIOS_RAIZ_PROHIBIDOS = {".cosmos"}
RUTAS_EXACTAS_PROHIBIDAS = {
    ".claude/settings.local.json",
    ".mcp.json",
    "cosmos.local.toml",
}
SUFIJO_COPIA_PRIVADA = re.compile(r"(?:~|\.(?:bak|backup|old|orig|save|tmp)(?:\.\d+)?)$")
PREFIJOS_PROHIBIDOS = (b".agents/skills/", b".claude/skills/")
NOMBRES_PROHIBIDOS = (
    re.compile(rb"^\.env(?:\..+)?$", re.IGNORECASE),
    re.compile(rb".*\.(?:pem|p12|pfx|key)$", re.IGNORECASE),
    re.compile(rb"^(?:credentials|service-account).*\.json$", re.IGNORECASE),
    re.compile(rb".*\.(?:jsonl|log)$", re.IGNORECASE),
)
NOMBRES_PERMITIDOS = {b".env.example"}
TROZO = 64 * 1024
SOLAPE = 4096
LIMITE_PREFIJO_TABLA = 64 * 1024

# Dominios reservados por la RFC 2606 y .invalid: un repo público-limpio los usa
# en su documentación y no son datos de nadie.
# Reservados por la RFC 6761 (.test, .example, .invalid, .localhost) y la RFC 2606
# (example.com/org/net) precisamente para documentación y pruebas: no son de nadie.
DOMINIOS_DE_EJEMPLO = (
    b".invalid", b".test", b".example", b".localhost",
    b"example.com", b"example.org", b"example.net",
    b"ejemplo.com", b"dominio.com",
)

PATRON_CORREO = re.compile(
    rb"(?i)(?<![A-Z0-9._%+-])[A-Z0-9._%+-]{1,64}@[A-Z0-9.-]+\.[A-Z]{2,63}(?![A-Z0-9._%+-])"
)
PATRON_TELEFONO = re.compile(
    rb"(?<![0-9A-Za-z])(?:"
    rb"\+[1-9][0-9]{0,2}(?:[ .()\-]*[0-9]){7,14}"
    rb"|(?:\+?34[ .-]?)?[6789](?:[ .-]?[0-9]){8}"
    rb")(?![0-9])"
)
SECRETO_ASIGNADO = "secreto asignado"
PATRONES = (
    ("clave privada", re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("token GitHub", re.compile(rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})")),
    ("clave OpenAI", re.compile(rb"sk-(?:proj-)?[A-Za-z0-9_-]{30,}")),
    ("clave Anthropic", re.compile(rb"sk-ant-[A-Za-z0-9_-]{30,}")),
    ("clave AWS", re.compile(rb"AKIA[0-9A-Z]{16}")),
    (
        "clave secreta AWS",
        re.compile(
            rb"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*['\"]?"
            rb"(?!example|change[_-]?me|vault:|\$\{)[A-Za-z0-9/+=]{32,}"
        ),
    ),
    (
        "token de API común",
        re.compile(
            rb"(?:AIza[0-9A-Za-z_-]{35}|xox[baprs]-[0-9A-Za-z-]{10,}|"
            rb"glpat-[0-9A-Za-z_-]{20,}|npm_[0-9A-Za-z]{30,}|"
            rb"(?:sk|rk)_(?:live|test)_[0-9A-Za-z]{16,})"
        ),
    ),
    (
        SECRETO_ASIGNADO,
        re.compile(
            rb"(?i)\b(?:[a-z][a-z0-9]*[_-])*(?:token|api[_-]?key|access[_-]?token|"
            rb"auth[_-]?token|password|passwd|secret(?:[_-]?(?:access[_-]?key|key))?|"
            rb"private[_-]?key|encryption[_-]?key|signing[_-]?key)"
            rb"\s*[:=]\s*['\"]?(?!example|change[_-]?me|replace[_-]?me|placeholder|"
            rb"vault:|\$\{)(?P<valor>[A-Za-z0-9_./+\-=]{20,})"
        ),
    ),
    (
        "URI con credencial",
        re.compile(
            rb"(?i)\b[a-z][a-z0-9+.-]{1,20}://[A-Za-z0-9._~-]{0,128}:"
            rb"(?!(?:example|change[_-]?me|password|passwd|secret|placeholder)@)"
            rb"[^\s'\"@{}<>$]{8,}@[^\s/'\"<>]{1,255}"
        ),
    ),
    (
        "identificador fiscal asignado",
        re.compile(
            rb"(?i)\b(?:[a-z][a-z0-9]*[_-])*(?:dni|nie|nif)\s*[:=]\s*['\"]?"
            rb"(?:[0-9]{8}[A-Z]|[XYZ][0-9]{7}[A-Z]|[A-Z][0-9]{7}[A-Z0-9])\b"
        ),
    ),
    (
        "IBAN asignado",
        re.compile(
            rb"(?i)\b(?:[a-z][a-z0-9]*[_-])*iban\s*[:=]\s*['\"]?"
            rb"[A-Z]{2}[0-9]{2}(?:[ ]?[A-Z0-9]){11,30}\b"
        ),
    ),
    ("correo electrónico", PATRON_CORREO),
    ("teléfono", PATRON_TELEFONO),
)
CABECERAS_PERSONALES = {
    "address",
    "apellidos",
    "cliente",
    "correo",
    "correo electronico",
    "customer",
    "direccion",
    "dni",
    "email",
    "fecha de nacimiento",
    "movil",
    "name",
    "nie",
    "nif",
    "nombre",
    "phone",
    "surname",
    "telefono",
}

# Formas que un lenguaje de programación produce y un generador de secretos no:
# 'os.environ.get', 'obtener_clave_del_entorno', 'GITHUB_TOKEN_DE_CI'.
_CAMELLO_O_RUTA = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+")
_SERPIENTE = re.compile(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)+")
_GRITO = re.compile(r"[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+")


class ErrorEscaneo(RuntimeError):
    pass


@dataclass(frozen=True)
class EntradaGit:
    ruta_cruda: bytes
    modo: str
    oid: str
    fase: int


def raiz_git(inicio: str | Path | None = None) -> Path:
    """Raíz del repositorio, preguntada a Git en vez de deducida de este fichero."""

    base = Path(inicio) if inicio is not None else Path.cwd()
    resultado = subprocess.run(
        ["git", "-C", str(base), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if resultado.returncode or not resultado.stdout.strip():
        raise ErrorEscaneo("no hay repositorio Git donde escanear")
    return Path(resultado.stdout.strip()).resolve()


def _git(raiz: Path, argumentos: list[str]) -> tuple[bool, bytes]:
    resultado = subprocess.run(
        ["git", "-C", str(raiz), *argumentos], capture_output=True, check=False
    )
    return resultado.returncode == 0, resultado.stdout


def _entradas_del_indice(raiz: Path) -> tuple[bool, list[EntradaGit]]:
    correcto, salida = _git(raiz, ["ls-files", "--stage", "-z"])
    if not correcto:
        return False, []
    entradas = []
    for elemento in salida.split(b"\0"):
        if not elemento or b"\t" not in elemento:
            continue
        metadatos, ruta_cruda = elemento.split(b"\t", 1)
        campos = metadatos.split()
        if len(campos) != 3:
            continue
        try:
            entradas.append(
                EntradaGit(
                    ruta_cruda=ruta_cruda,
                    modo=campos[0].decode("ascii"),
                    oid=campos[1].decode("ascii"),
                    fase=int(campos[2]),
                )
            )
        except (UnicodeDecodeError, ValueError):
            continue
    return True, sorted(entradas, key=lambda e: (e.ruta_cruda, e.fase, e.oid))


def _candidatas(raiz: Path, modo: str) -> list[EntradaGit] | None:
    correcto, entradas = _entradas_del_indice(raiz)
    if not correcto:
        return None
    if modo != "indice":
        return entradas
    cambiado_ok, salida = _git(
        raiz, ["diff", "--cached", "--name-only", "--diff-filter=ACMRTU", "-z"]
    )
    if not cambiado_ok:
        return None
    cambiadas = {elemento for elemento in salida.split(b"\0") if elemento}
    return [entrada for entrada in entradas if entrada.ruta_cruda in cambiadas]


def _hallazgo(ruta_cruda: bytes, descripcion: str, linea: int | None = None) -> str:
    lugar = etiqueta_de_ruta(ruta_cruda)
    if linea is not None:
        lugar = f"{lugar}:{linea}"
    return f"{lugar}: {descripcion}"


def _es_expresion(valor: bytes) -> bool:
    """Distingue un secreto de un trozo de código que se llama como uno.

    El patrón de 'secreto asignado' solo mira que a la derecha del '=' haya veinte
    caracteres de un alfabeto amplio, así que 'obtener_clave_del_entorno' le vale.
    Es la clase de ruido que acaba con la herramienta desactivada, y el desactivado
    no encuentra secretos.
    """

    try:
        texto = valor.decode("ascii")
    except UnicodeDecodeError:
        return False
    return any(
        patron.fullmatch(texto) for patron in (_CAMELLO_O_RUTA, _SERPIENTE, _GRITO)
    )


def _permitida(etiqueta: str, coincidencia: re.Match[bytes]) -> bool:
    if etiqueta == "correo electrónico":
        dominio = coincidencia.group(0).rsplit(b"@", 1)[-1].lower()
        return any(dominio.endswith(ejemplo) for ejemplo in DOMINIOS_DE_EJEMPLO) or (
            coincidencia.group(0).lower() in CORREOS_DE_EJEMPLO
        )
    if etiqueta == SECRETO_ASIGNADO:
        return _es_expresion(coincidencia.group("valor"))
    if etiqueta == "teléfono" and _es_decimal(coincidencia.group(0)):
        return True
    if etiqueta in ETIQUETAS_CON_VALOR_FICTICIO:
        return _es_valor_de_ejemplo(coincidencia.group(0))
    return False


def _es_valor_de_ejemplo(valor: bytes) -> bool:
    """Reconoce el dato de relleno que todo el mundo escribe en una cadena de ayuda.

    Sin esto, la cadena `--nif 12345678Z --telefono 600000000` de un `--help` obliga
    a poner el fichero en una lista de excepciones. Y una lista de excepciones que
    crece acaba tapando el hallazgo de verdad: la respuesta a un falso positivo es
    enseñar al escáner, no callarlo.

    Solo pasa lo que es reconociblemente ficticio: una secuencia trivial, un mismo
    dígito repetido, o un valor de la lista corta de convenciones.
    """

    # El patrón captura el prefijo (`nif = 12345678Z`, `--telefono 600000000`):
    # el valor es la cola, tras el último separador o espacio.
    cola = re.split(rb"[:=\s]", valor)[-1]
    if _es_contador(valor):
        return True
    limpio = re.sub(rb"[^A-Za-z0-9]", b"", cola).upper()
    entero = re.sub(rb"[^A-Za-z0-9]", b"", valor).upper()
    if limpio in VALORES_DE_EJEMPLO or entero in VALORES_DE_EJEMPLO:
        return True
    digitos = re.sub(rb"[^0-9]", b"", limpio)
    if len(digitos) < 6:
        return False
    if len(set(digitos)) == 1:                       # 000000000, 666666666
        return True
    primero = digitos[0] - 48                        # byte ASCII -> dígito
    ascendente = bytes(48 + (primero + i) % 10 for i in range(len(digitos)))
    return digitos == ascendente                      # 12345678, 0123456789


def _es_decimal(valor: bytes) -> bool:
    """Un número con parte decimal es una cifra, no un teléfono.

    Caso real: `price_to_precision("BTC/USDT", 63123.4567)` disparaba el patrón,
    porque el punto decimal encaja como separador de grupos. Ningún teléfono lleva
    un punto seguido de tres o más dígitos: eso es una fracción.
    """

    return re.fullmatch(rb"[0-9]{1,7}[.,][0-9]{3,}", valor) is not None


def _es_contador(valor: bytes) -> bool:
    """Una lista de enteros crecientes es un bucle, no un teléfono.

    Caso real que lo motivó: `for i in 1 2 3 4 5 6 7 8 9 10 11 ...` disparaba el
    patrón de teléfono. Un falso positivo así es peor que perder un hallazgo, porque
    empuja a poner el fichero en una lista de excepciones — y una lista que crece
    acaba tapando el dato real.
    """

    piezas = valor.split()
    if len(piezas) < 4 or not all(p.isdigit() for p in piezas):
        return False
    numeros = [int(p) for p in piezas]
    return all(b == a + 1 for a, b in zip(numeros, numeros[1:]))


# Convenciones de relleno: lo que aparece en un `--help`, nunca en un dato real.
VALORES_DE_EJEMPLO = frozenset({
    b"12345678Z", b"00000000T", b"11111111H", b"X1234567L",
    b"B00000000", b"A00000000", b"B12345678",   # CIF: letra de forma juridica + 8
    b"600000000", b"666666666", b"900000000", b"555555555",
})
CORREOS_DE_EJEMPLO = frozenset({
    b"correo@dominio.com", b"email@dominio.com", b"tu@dominio.com",
    b"ejemplo@dominio.com", b"usuario@ejemplo.com", b"nombre@empresa.com",
})
ETIQUETAS_CON_VALOR_FICTICIO = frozenset({
    "identificador fiscal asignado", "teléfono",
})


def _primera_sensible(
    patron: re.Pattern[bytes], etiqueta: str, datos: bytes
) -> re.Match[bytes] | None:
    for coincidencia in patron.finditer(datos):
        if not _permitida(etiqueta, coincidencia):
            return coincidencia
    return None


def _hallazgos_de_ruta(ruta_cruda: bytes) -> list[str]:
    hallazgos = []
    partes = [parte.lower() for parte in ruta_cruda.split(b"/")]
    ruta_baja = b"/".join(partes)
    nombre = partes[-1] if partes else b""

    if partes and os.fsdecode(partes[0]) in DIRECTORIOS_RAIZ_PROHIBIDOS:
        hallazgos.append(_hallazgo(ruta_cruda, "ruta local prohibida versionada"))
    decodificada = os.fsdecode(ruta_baja)
    if decodificada in RUTAS_EXACTAS_PROHIBIDAS or any(
        decodificada == f"{privada}~"
        or (
            decodificada.startswith(f"{privada}.")
            and SUFIJO_COPIA_PRIVADA.search(decodificada[len(privada) :])
        )
        for privada in RUTAS_EXACTAS_PROHIBIDAS
    ):
        hallazgos.append(_hallazgo(ruta_cruda, "ruta local prohibida versionada"))
    if any(ruta_baja.startswith(prefijo) for prefijo in PREFIJOS_PROHIBIDOS):
        hallazgos.append(_hallazgo(ruta_cruda, "vista plana generada, no versionable"))
    if nombre not in NOMBRES_PERMITIDOS and any(
        patron.fullmatch(nombre) for patron in NOMBRES_PROHIBIDOS
    ):
        hallazgos.append(_hallazgo(ruta_cruda, "nombre de archivo sensible o local"))

    for etiqueta, patron in PATRONES:
        if _primera_sensible(patron, etiqueta, ruta_cruda) is not None:
            hallazgos.append(_hallazgo(ruta_cruda, f"posible {etiqueta} en la ruta"))
    return hallazgos


def _cabecera_normalizada(valor: str) -> str:
    descompuesta = unicodedata.normalize("NFKD", valor.strip().strip("\"'").lower())
    return " ".join(
        "".join(c for c in descompuesta if not unicodedata.combining(c)).split()
    )


def _parece_tabla_personal(ruta_cruda: bytes, prefijo: bytes) -> bool:
    sufijo = ruta_cruda.rsplit(b"/", 1)[-1].lower()
    if not sufijo.endswith((b".csv", b".tsv")):
        return False
    texto = prefijo.decode("utf-8-sig", errors="ignore")
    lineas = [linea for linea in texto.splitlines() if linea.strip()][:10]
    if len(lineas) < 2:
        return False
    separador = max(("\t", ";", ","), key=lineas[0].count)
    if lineas[0].count(separador) == 0:
        return False
    try:
        filas = list(csv.reader(lineas, delimiter=separador))
    except csv.Error:
        return False
    if len(filas) < 2:
        return False
    columnas = [
        indice
        for indice, valor in enumerate(filas[0])
        if _cabecera_normalizada(valor) in CABECERAS_PERSONALES
    ]
    if len(columnas) < 2:
        return False
    return any(
        indice < len(fila) and fila[indice].strip()
        for fila in filas[1:]
        for indice in columnas
    )


def escanear_flujo(flujo: BinaryIO, ruta_cruda: bytes) -> list[str]:
    hallazgos = []
    reportadas: set[str] = set()
    prefijo = bytearray()
    cola = b""
    saltos = 0

    try:
        while True:
            trozo = flujo.read(TROZO)
            if not trozo:
                break
            if len(prefijo) < LIMITE_PREFIJO_TABLA:
                prefijo.extend(trozo[: LIMITE_PREFIJO_TABLA - len(prefijo)])
            datos = cola + trozo
            saltos_previos = saltos - cola.count(b"\n")
            for etiqueta, patron in PATRONES:
                if etiqueta in reportadas:
                    continue
                coincidencia = _primera_sensible(patron, etiqueta, datos)
                if coincidencia is None:
                    continue
                linea = saltos_previos + datos.count(b"\n", 0, coincidencia.start()) + 1
                hallazgos.append(_hallazgo(ruta_cruda, f"posible {etiqueta}", linea))
                reportadas.add(etiqueta)
            saltos += trozo.count(b"\n")
            cola = datos[-SOLAPE:]
    except OSError as exc:
        hallazgos.append(_hallazgo(ruta_cruda, f"no se pudo leer ({exc.__class__.__name__})"))

    if _parece_tabla_personal(ruta_cruda, bytes(prefijo)):
        hallazgos.append(_hallazgo(ruta_cruda, "posible tabla con datos personales"))
    return hallazgos


def _escanear_entrada(raiz: Path, entrada: EntradaGit) -> list[str]:
    hallazgos = _hallazgos_de_ruta(entrada.ruta_cruda)
    if entrada.modo == "160000":
        hallazgos.append(_hallazgo(entrada.ruta_cruda, "submódulo no permitido"))
        return hallazgos
    if entrada.modo == "120000":
        hallazgos.append(_hallazgo(entrada.ruta_cruda, "enlace simbólico versionado no permitido"))
        return hallazgos
    if not re.fullmatch(r"[0-9a-fA-F]{40,64}", entrada.oid) or set(entrada.oid) == {"0"}:
        hallazgos.append(_hallazgo(entrada.ruta_cruda, "no se pudo resolver el blob versionado"))
        return hallazgos
    try:
        proceso = subprocess.Popen(
            ["git", "-C", str(raiz), "cat-file", "blob", entrada.oid],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except OSError as exc:
        hallazgos.append(
            _hallazgo(entrada.ruta_cruda, f"no se pudo leer ({exc.__class__.__name__})")
        )
        return hallazgos
    assert proceso.stdout is not None
    hallazgos.extend(escanear_flujo(proceso.stdout, entrada.ruta_cruda))
    proceso.stdout.close()
    if proceso.wait() != 0:
        hallazgos.append(_hallazgo(entrada.ruta_cruda, "no se pudo leer el blob versionado"))
    return hallazgos


def escanear(modo: str = "todo", *, raiz: str | Path | None = None) -> list[str]:
    """Hallazgos ordenados sobre los blobs del índice; nunca sobre el árbol sucio."""

    raiz_path = raiz_git(raiz)
    entradas = _candidatas(raiz_path, modo)
    if entradas is None:
        return ["índice Git: no se pudieron enumerar los blobs; escaneo bloqueado"]
    hallazgos: list[str] = []
    for entrada in entradas:
        hallazgos.extend(_escanear_entrada(raiz_path, entrada))
    return sorted(set(hallazgos))


NOMBRE_CONOCIDOS = "secretos-conocidos.txt"


def leer_conocidos(ruta: str | Path | None) -> set[str]:
    """Deuda ya inventariada. Una línea por hallazgo aceptado, sin número de línea."""

    if ruta is None:
        return set()
    camino = Path(ruta)
    if not camino.is_file():
        return set()
    conocidos = set()
    for linea in camino.read_text(encoding="utf-8").splitlines():
        limpia = linea.strip()
        if limpia and not limpia.startswith("#"):
            conocidos.add(clave_hallazgo(limpia))
    return conocidos


def separar_conocidos(hallazgos: list[str], conocidos: set[str]) -> tuple[list[str], list[str]]:
    """Divide en (nuevos, ya inventariados). Solo los nuevos bloquean."""

    nuevos, viejos = [], []
    for hallazgo in hallazgos:
        (viejos if clave_hallazgo(hallazgo) in conocidos else nuevos).append(hallazgo)
    return nuevos, viejos


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--indice", action="store_true", help="solo los blobs que cambian en el índice")
    grupo.add_argument("--todo", action="store_true", help="todos los blobs versionados")
    parser.add_argument("--raiz", default=None, help="repositorio a escanear")
    parser.add_argument(
        "--conocidos",
        default=None,
        help=f"inventario de hallazgos aceptados; por defecto {NOMBRE_CONOCIDOS} en la raíz",
    )
    parser.add_argument("--sin-conocidos", action="store_true", help="ignora el inventario y falla con todo")
    args = parser.parse_args(argv)
    try:
        raiz = raiz_git(args.raiz)
        hallazgos = escanear("indice" if args.indice else "todo", raiz=raiz)
    except ErrorEscaneo as exc:
        print(f"ERROR: {exc}")
        return 1
    inventario = None if args.sin_conocidos else (args.conocidos or raiz / NOMBRE_CONOCIDOS)
    nuevos, viejos = separar_conocidos(hallazgos, leer_conocidos(inventario))
    for hallazgo in viejos:
        print(f"CONOCIDO: {hallazgo}")
    for hallazgo in nuevos:
        print(f"ERROR: {hallazgo}")
    if nuevos:
        cola = f"; {len(viejos)} ya inventariado(s)" if viejos else ""
        print(f"secretos: {len(nuevos)} hallazgo(s) nuevo(s){cola}; valores y rutas ocultos")
        return 1
    if viejos:
        print(f"secretos: limpio de nuevos; {len(viejos)} hallazgo(s) inventariado(s) en {NOMBRE_CONOCIDOS}")
        return 0
    print("secretos: limpio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
