"""Abrir páginas con agent-browser sin medir la que no es.

Existe porque el mismo fallo puede aparecer dos veces: reutilizar una sesión que
otro trabajo tenía abierta en otra URL, y medir esa otra página creyendo que es
la propia. El informe sale entero y es mentira. Aquí vive el abrir-y-comprobar,
para que ningún script futuro tenga que acordarse.

    from navegador_seguro import abrir, sesion_para, cerrar_si_es_mia, ejecutar

    sesion, mia = sesion_para("mi-tarea")
    if abrir(sesion, url, 1440):
        datos = ejecutar(sesion, "document.title")
    cerrar_si_es_mia(sesion, mia)
"""
import json
import os
import subprocess
import time

# El tope depende de la RAM de la máquina, no de una regla universal: se ajusta sin tocar el guion.
TOPE_SESIONES = int(os.environ.get("AGENT_BROWSER_TOPE_SESIONES", "3"))


def _cli(sesion, *orden, espera=240):
    return subprocess.run(["agent-browser", "--session", sesion, *orden],
                          capture_output=True, text=True, timeout=espera)


def sesiones_abiertas():
    hecho = subprocess.run(["agent-browser", "session", "list"],
                           capture_output=True, text=True, timeout=60)
    return [l.strip() for l in hecho.stdout.splitlines() if l.startswith("  ") and l.strip()]


def sesion_para(nombre, avisar=None):
    """Devuelve (sesion, es_mia): la del nombre si ya existe, o una propia.

    NUNCA se cuelga de la sesión de otro trabajo. Con el tope alcanzado, apropiarse
    de la sesión de otro acaba midiendo su página y pisando su trabajo: abrir una
    sesión de más es un coste de RAM, robar la ajena corrompe dos cosas.
    Si se pasa del tope se avisa, y si quedaron sesiones 'auto-' huérfanas se cierran antes.
    """
    abiertas = sesiones_abiertas()
    if nombre in abiertas:
        return nombre, False

    propia = f"auto-{nombre}"
    if propia in abiertas:
        return propia, True

    huerfanas = [s for s in abiertas if s.startswith("auto-")]
    if len(abiertas) >= TOPE_SESIONES and huerfanas:
        _cli(huerfanas[0], "close")            # una propia vieja: esa sí se puede cerrar
    elif len(abiertas) >= TOPE_SESIONES and avisar:
        avisar(f"  aviso: ya hay {len(abiertas)} sesiones de navegador "
               f"({', '.join(abiertas)}); abro '{propia}' igualmente para no pisar otro trabajo")
    return propia, True


def cerrar_si_es_mia(sesion, es_mia):
    """Nunca cerrar la sesión de otro trabajo: puede estar a medias."""
    if es_mia:
        _cli(sesion, "close")


def ejecutar(sesion, js):
    """Evalúa JS y devuelve el valor ya desenvuelto.

    agent-browser serializa el resultado, así que un JS con JSON.stringify llega
    envuelto en comillas y hay que abrirlo DOS veces. Sin esto se recibe una cadena
    donde se esperaba un objeto y el script revienta con 'str has no attribute get'.
    """
    crudo = _cli(sesion, "eval", js).stdout.strip()
    if not crudo:
        return None
    try:
        valor = json.loads(crudo)
    except (json.JSONDecodeError, ValueError):
        return crudo.strip('"')
    if isinstance(valor, str):
        try:
            return json.loads(valor)
        except (json.JSONDecodeError, ValueError):
            return valor
    return valor


def abrir(sesion, url, ancho, alto=900, avisar=print):
    """Abre, fija el ancho y COMPRUEBA las dos cosas. Devuelve si es fiable medir."""
    _cli(sesion, "set", "viewport", str(ancho), str(alto))
    _cli(sesion, "open", f"{url}?cb={int(time.time()*1000)}")
    time.sleep(2)

    ruta_pedida = url.split("://", 1)[-1].split("/", 1)[-1].rstrip("/")
    ruta_pedida = "/" + ruta_pedida if not ruta_pedida.startswith("/") else ruta_pedida

    # `open` puede agotar su espera y volver ANTES de que el documento exista: entonces
    # location.pathname es "blank" y el aborto es falso — la página sí acaba cargando.
    cargada = ""
    for _ in range(6):
        cargada = str(ejecutar(sesion, "location.pathname") or "")
        if cargada and cargada != "blank":
            break
        time.sleep(3)
    if ruta_pedida and not cargada.rstrip("/").endswith(ruta_pedida.rstrip("/")):
        avisar(f"  ABORTO: pedí {ruta_pedida} y el navegador tiene {cargada}")
        return False

    # El viewport se pierde al navegar: sin refijarlo se compara 1440 contra 1920.
    _cli(sesion, "set", "viewport", str(ancho), str(alto))
    time.sleep(1)
    real = ejecutar(sesion, "document.documentElement.clientWidth")
    try:
        if abs(int(real) - ancho) > 2:
            avisar(f"  ABORTO: pedí {ancho}px de ancho y el navegador está a {real}px")
            return False
    except (TypeError, ValueError):
        avisar(f"  ABORTO: no he podido confirmar el ancho (devolvió {real!r})")
        return False
    return True
