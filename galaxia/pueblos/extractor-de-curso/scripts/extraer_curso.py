#!/usr/bin/env python3
"""Extrae el contenido de un curso online a Markdown usando agent-browser.

Lee. No marca lecciones como completadas, no envía formularios, no responde
exámenes, no simula interacción humana. La navegación va con la sesión real
del usuario (su propio login).

Uso:
    extraer_curso.py <url> --salida progress/curso-x --descubrir
    extraer_curso.py <url> --salida progress/curso-x --solo-indice
    extraer_curso.py <url> --salida progress/curso-x --capturas
    extraer_curso.py <url> --salida progress/curso-x --seguir   # sin índice
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

# Patrones de URL habituales en LMS (Moodle, LearnDash, Teachable, Docebo, FUNDAE...)
PISTAS_LECCION = re.compile(
    r"/(leccion|lecciones|lesson|lessons|topic|topics|unidad|unit|units|modulo|"
    r"module|modules|tema|temas|capitulo|chapter|clase|class|curso/[^/]+/|"
    r"mod/(page|book|scorm|resource|lesson|quiz)|content|activity)/",
    re.I,
)

RUIDO_URL = re.compile(
    r"/(logout|salir|desconectar|perfil|profile|ajustes|settings|cuenta|account|"
    r"ayuda|help|soporte|support|contacto|contact|aviso|legal|privacidad|cookies)\b",
    re.I,
)

# Nunca seguir enlaces que disparen progreso/evaluación en el LMS.
ETIQUETA_PROHIBIDA = re.compile(
    r"(complet|finaliz|marcar|terminar|finish|submit|enviar|entregar|examen|exam|"
    r"evaluaci|test\s+final|quiz|calific|certificad)",
    re.I,
)

SEL_CONTENIDO = [
    ".lesson-content", ".ld-tabs-content", ".learndash_content", ".lesson_content",
    ".elementor-widget-theme-post-content", ".entry-content",
    "#region-main .content", "#region-main", ".course-content__body",
    ".scorm-content", "#scormpage", ".activity-content",
    "article .body", "[role=main] article", "main article", "article",
    "[role=main]", "main", "#content", ".content",
]

SEL_INDICE = [
    ".ld-item-list", ".ld-table-list", ".learndash-course-content",
    ".course-outline", ".curriculum", ".course-content", ".chapter-list",
    "#course-index", ".course_sesskey", "#region-main",
    "main", "[role=main]",
]

JS_CONTENIDO = r"""
const CANDIDATOS = __SEL__;
let nodo = null;
for (const sel of CANDIDATOS) {
  const el = document.querySelector(sel);
  if (el && (el.innerText || '').trim().length > 200) { nodo = el; break; }
}
if (!nodo) nodo = document.body;

const clon = nodo.cloneNode(true);
clon.querySelectorAll(
  'nav, header, footer, aside, script, style, noscript, form, ' +
  '[role=navigation], [role=banner], [role=contentinfo], [aria-hidden=true], ' +
  '.sphinxsidebar, .toc, .toctree-wrapper, .breadcrumb, .breadcrumbs, ' +
  '.pagination, .prev-next, .skip-link, .screen-reader-text, .ld-course-navigation'
).forEach(n => n.remove());

const texto = (clon.innerText || '')
  .replace(/[ \t]+\n/g, '\n').replace(/\n{3,}/g, '\n\n').trim();
JSON.stringify({
  texto,
  selector: nodo.tagName + (nodo.className ? '.' + String(nodo.className).split(' ')[0] : ''),
});
"""

# Distingue "no hay contenido" de "no hay sesión". Sin esto el script llenaría
# la carpeta de copias de la pantalla de login sin que nadie se entere.
JS_AUTENTICACION = r"""
const url = location.href.toLowerCase();
const texto = (document.body.innerText || '').toLowerCase();
const hayPassword = !!document.querySelector('input[type=password]');
const urlLogin = /\/(login|signin|acceso|entrar|auth|sso)\b/.test(url);
const textoLogin = /(iniciar sesi|inicia sesi|log ?in|sign ?in|acceder|contrase|usuario y contrase)/.test(
  texto.slice(0, 1500)
);
const muro = hayPassword || (urlLogin && textoLogin);
JSON.stringify({ muro, hayPassword, urlLogin, url: location.href,
                 titulo: document.title || '' });
"""

JS_MEDIA = r"""
const media = [];
for (const v of document.querySelectorAll('video')) {
  const pistas = Array.from(v.querySelectorAll('track')).map(t => ({
    tipo: t.kind, idioma: t.srclang, src: t.src }));
  media.push({ tipo: 'video', src: v.currentSrc || v.src || '(blob/streaming)',
               duracion: Number.isFinite(v.duration) ? Math.round(v.duration) : null,
               pistas });
}
for (const f of document.querySelectorAll('iframe')) {
  const s = f.getAttribute('src') || '';
  if (/youtube|vimeo|wistia|player|kaltura|panopto|brightcove|jwplayer/i.test(s)) {
    media.push({ tipo: 'iframe', src: new URL(s, location.href).href,
                 duracion: null, pistas: [] });
  }
}
for (const a of document.querySelectorAll(
       'a[href$=".pdf"], a[href$=".pptx"], a[href$=".docx"], a[href*="pluginfile"]')) {
  media.push({ tipo: 'adjunto', src: a.href, duracion: null, pistas: [] });
}
JSON.stringify(media);
"""

# Muchos cursos ponen la transcripción del vídeo en un panel plegado: es la
# mejor materia prima de estudio y el texto plano de la lección no la incluye.
JS_TRANSCRIPCION = r"""
const SEL = ['.transcript', '.transcripcion', '#transcript', '[class*=transcript]',
             '[id*=transcript]', '.vjs-text-track-display', '.subtitulos',
             '[aria-label*=ranscri]', '[data-purpose*=transcript]'];
let mejor = '';
for (const sel of SEL) {
  for (const el of document.querySelectorAll(sel)) {
    const t = (el.innerText || '').trim();
    if (t.length > mejor.length) mejor = t;
  }
}
JSON.stringify({ texto: mejor.slice(0, 200000) });
"""

JS_ENLACES = r"""
const RAICES = __SEL__;
let raiz = null;
for (const sel of RAICES) {
  const el = document.querySelector(sel);
  if (el && el.querySelectorAll('a[href]').length >= 2) { raiz = el; break; }
}
if (!raiz) raiz = document.body;

const vistos = new Set(); const salida = [];
for (const a of raiz.querySelectorAll('a[href]')) {
  let href;
  try { href = new URL(a.getAttribute('href'), location.href).href; } catch { continue; }
  if (!href.startsWith(location.origin)) continue;
  const limpia = href.split('#')[0];
  if (vistos.has(limpia)) continue;
  const titulo = (a.innerText || a.textContent || '').trim().replace(/\s+/g, ' ');
  if (!titulo) continue;
  vistos.add(limpia);
  salida.push({ titulo: titulo.slice(0, 200), url: limpia });
}
JSON.stringify(salida);
"""

# Para cursos sin índice navegable: seguir el enlace "siguiente". Solo <a href>,
# nunca botones, y descartando cualquier etiqueta que suene a marcar progreso
# o entregar un examen.
JS_SIGUIENTE = r"""
const PROHIBIDO = /(complet|finaliz|marcar|terminar|finish|submit|enviar|entregar|examen|exam|evaluaci|quiz|calific|certificad)/i;
const candidatos = [];
const rel = document.querySelector('a[rel=next][href], link[rel=next][href]');
if (rel) candidatos.push(rel);
for (const a of document.querySelectorAll('a[href]')) {
  const t = ((a.innerText || '') + ' ' + (a.getAttribute('aria-label') || '')).trim();
  if (/^(siguiente|next|continuar|continue|adelante|siguiente lecci|next lesson)/i.test(t)) {
    candidatos.push(a);
  }
}
let elegido = null;
for (const a of candidatos) {
  const etiqueta = ((a.innerText || '') + ' ' + (a.getAttribute('aria-label') || '')).trim();
  if (PROHIBIDO.test(etiqueta)) continue;
  let href;
  try { href = new URL(a.getAttribute('href'), location.href).href; } catch { continue; }
  if (!href.startsWith(location.origin)) continue;
  if (href.split('#')[0] === location.href.split('#')[0]) continue;
  elegido = { url: href.split('#')[0], etiqueta: etiqueta.slice(0, 120) };
  break;
}
JSON.stringify(elegido);
"""

# Modo --descubrir: propone selectores reales en vez de que el usuario los busque a mano.
JS_DESCUBRIR = r"""
const conteo = new Map();
for (const a of document.querySelectorAll('a[href]')) {
  if (!a.getAttribute('href') || !(a.innerText || '').trim()) continue;
  const padre = a.parentElement;
  if (!padre) continue;
  const clases = String(a.className || '').trim().split(/\s+/).filter(Boolean);
  const sel = clases.length ? 'a.' + clases[0]
            : (String(padre.className || '').trim().split(/\s+/)[0]
                ? '.' + String(padre.className).trim().split(/\s+/)[0] + ' a'
                : padre.tagName.toLowerCase() + ' a');
  conteo.set(sel, (conteo.get(sel) || 0) + 1);
}
const orden = Array.from(conteo.entries())
  .filter(([, n]) => n >= 2).sort((a, b) => b[1] - a[1]).slice(0, 12);
JSON.stringify(orden.map(([selector, n]) => ({ selector, enlaces: n })));
"""


class ErrorNavegador(RuntimeError):
    pass


class MuroLogin(RuntimeError):
    pass


# Con CDP la sesión viva la manda: --restore recargaría un estado guardado
# anterior al login y tiraría las cookies recién obtenidas.
RESTAURAR = False


def ab(args: list[str], sesion: str, stdin: str | None = None,
       timeout: int = 90, restore: bool | None = None) -> str:
    cmd = ["agent-browser", "--session", sesion]
    if RESTAURAR if restore is None else restore:
        cmd.append("--restore")
    cmd += args
    proc = subprocess.run(cmd, input=stdin, capture_output=True, text=True,
                          timeout=timeout)
    if proc.returncode != 0:
        raise ErrorNavegador(
            f"agent-browser {' '.join(args[:2])} falló ({proc.returncode}): "
            f"{(proc.stderr or proc.stdout).strip()[:400]}"
        )
    return proc.stdout


def eval_js(js: str, sesion: str, selectores: list[str] | None = None):
    if selectores is not None:
        js = js.replace("__SEL__", json.dumps(selectores))
    # agent-browser reutiliza el contexto JS entre evals: sin aislar, un `const`
    # de un script colisiona con el del siguiente ("Identifier already declared").
    cuerpo = js.strip()
    corte = cuerpo.rfind("JSON.stringify")
    if corte != -1:
        cuerpo = cuerpo[:corte] + "return " + cuerpo[corte:]
    js = "(() => {\n" + cuerpo + "\n})()"

    salida = ab(["eval", "--stdin"], sesion, stdin=js).strip()
    if not salida:
        return None
    for intento in (salida, salida[salida.find("{"):], salida[salida.find("["):]):
        if not intento or intento.startswith("-1"):
            continue
        try:
            valor = json.loads(intento)
        except json.JSONDecodeError:
            continue
        if isinstance(valor, str):
            try:
                return json.loads(valor)
            except json.JSONDecodeError:
                return valor
        return valor
    return None


def con_reintentos(fn, intentos: int = 3, espera: float = 2.0):
    """Los LMS fallan de forma intermitente bajo carga; un fallo != lección rota."""
    ultimo = None
    for n in range(1, intentos + 1):
        try:
            return fn()
        except (ErrorNavegador, subprocess.TimeoutExpired) as exc:
            ultimo = exc
            if n < intentos:
                time.sleep(espera * n)
    raise ultimo


def abrir(url: str, sesion: str, espera_ms: int) -> None:
    con_reintentos(lambda: ab(["open", url], sesion))
    try:
        ab(["wait", "--load", "networkidle"], sesion, timeout=45)
    except (ErrorNavegador, subprocess.TimeoutExpired):
        pass  # networkidle no llega en SPAs con polling; seguimos igual
    if espera_ms:
        time.sleep(espera_ms / 1000)


def comprobar_sesion(sesion: str) -> None:
    estado = eval_js(JS_AUTENTICACION, sesion)
    if isinstance(estado, dict) and estado.get("muro"):
        raise MuroLogin(
            f"La página pide login ({estado.get('titulo') or estado.get('url')}).\n"
            "Inicia sesión tú en el Chrome que está conectado por CDP y reintenta.\n"
            "Este script no introduce credenciales."
        )


def slug(texto: str, limite: int = 60) -> str:
    s = re.sub(r"[^\w\s-]", "", texto, flags=re.UNICODE).strip().lower()
    s = re.sub(r"[\s_-]+", "-", s)
    return (s[:limite] or "sin-titulo").strip("-")


def descubrir_selectores(url: str, sesion: str, espera_ms: int) -> list[dict]:
    abrir(url, sesion, espera_ms)
    comprobar_sesion(sesion)
    return eval_js(JS_DESCUBRIR, sesion) or []


def descubrir_lecciones(url_indice: str, sesion: str, espera_ms: int,
                        selector: str | None) -> list[dict]:
    abrir(url_indice, sesion, espera_ms)
    comprobar_sesion(sesion)

    if selector:
        js = (
            "JSON.stringify(Array.from(document.querySelectorAll(%s))"
            ".filter(a => a.getAttribute('href')).map(a => ({"
            "titulo: (a.innerText||'').trim().replace(/\\s+/g,' ').slice(0,200),"
            "url: new URL(a.getAttribute('href'), location.href).href.split('#')[0]"
            "})).filter(x => x.titulo && x.url));" % json.dumps(selector)
        )
        enlaces = eval_js(js, sesion) or []
    else:
        enlaces = eval_js(JS_ENLACES, sesion, selectores=SEL_INDICE) or []

    base = urlparse(url_indice)
    filtradas, vistas = [], set()
    for e in enlaces:
        u = e.get("url", "")
        if not u or u in vistas:
            continue
        p = urlparse(u)
        if p.netloc != base.netloc or RUIDO_URL.search(p.path):
            continue
        if ETIQUETA_PROHIBIDA.search(e.get("titulo", "")):
            continue  # no arrastrar exámenes a la extracción
        if not selector and not PISTAS_LECCION.search(p.path):
            continue
        vistas.add(u)
        filtradas.append({"titulo": e["titulo"], "url": u})

    if not filtradas and not selector:
        for e in enlaces:
            u = e.get("url", "")
            if u and u not in vistas and urlparse(u).netloc == base.netloc:
                vistas.add(u)
                filtradas.append(e)
    return filtradas


def recorrer_siguientes(url_inicial: str, sesion: str, espera_ms: int,
                        limite: int) -> list[dict]:
    """Para cursos sin índice: encadena 'siguiente' hasta agotar o repetirse."""
    lecciones, vistas = [], set()
    url = url_inicial
    while url and url not in vistas and len(lecciones) < limite:
        abrir(url, sesion, espera_ms)
        comprobar_sesion(sesion)
        vistas.add(url)
        titulo = ab(["get", "title"], sesion).strip() or url
        lecciones.append({"titulo": titulo, "url": url})
        siguiente = eval_js(JS_SIGUIENTE, sesion)
        if not isinstance(siguiente, dict):
            break
        print(f"  -> siguiente: {siguiente.get('etiqueta', '')}", file=sys.stderr)
        url = siguiente.get("url")
    return lecciones


def extraer_leccion(leccion: dict, sesion: str, espera_ms: int,
                    destino_shots: Path | None, indice: int) -> dict:
    abrir(leccion["url"], sesion, espera_ms)
    comprobar_sesion(sesion)
    titulo = ab(["get", "title"], sesion).strip() or leccion["titulo"]

    texto, origen = "", "?"
    cuerpo = eval_js(JS_CONTENIDO, sesion, selectores=SEL_CONTENIDO)
    if isinstance(cuerpo, dict):
        texto, origen = cuerpo.get("texto", ""), cuerpo.get("selector", "?")

    if len(texto) < 200:
        try:
            texto, origen = ab(["read"], sesion, timeout=120), "read (fallback)"
        except (ErrorNavegador, subprocess.TimeoutExpired) as exc:
            texto, origen = f"(no se pudo leer: {exc})", "error"

    media = eval_js(JS_MEDIA, sesion) or []
    transcripcion = ""
    if media:
        t = eval_js(JS_TRANSCRIPCION, sesion)
        if isinstance(t, dict) and len(t.get("texto", "")) > 120:
            transcripcion = t["texto"]

    captura = None
    if destino_shots is not None:
        ruta = destino_shots / f"{indice:02d}-{slug(titulo, 40)}.png"
        try:
            ab(["screenshot", "--full", str(ruta)], sesion, timeout=90)
            captura = ruta.name
        except (ErrorNavegador, subprocess.TimeoutExpired):
            pass

    return {"titulo": titulo, "url": leccion["url"], "texto": texto, "media": media,
            "origen": origen, "transcripcion": transcripcion, "captura": captura}


def escribir_leccion(destino: Path, indice: int, datos: dict) -> Path:
    ruta = destino / f"{indice:02d}-{slug(datos['titulo'])}.md"
    partes = [f"# {datos['titulo']}", "",
              f"> Fuente: {datos['url']}",
              f"> Extraído de: `{datos.get('origen', '?')}`", ""]
    if datos.get("captura"):
        partes += [f"![captura](../capturas/{datos['captura']})", ""]
    if datos["media"]:
        partes += ["## Media en la lección", ""]
        for m in datos["media"]:
            dur = f" — {m['duracion']}s" if m.get("duracion") else ""
            partes.append(f"- `{m['tipo']}`{dur}: {m['src']}")
            for p in m.get("pistas") or []:
                partes.append(f"  - subtítulos ({p.get('idioma') or '?'}): {p.get('src')}")
        partes.append("")
    partes += ["## Contenido", "", datos["texto"].strip(), ""]
    if datos.get("transcripcion"):
        partes += ["## Transcripción del vídeo", "", datos["transcripcion"].strip(), ""]
    ruta.write_text("\n".join(partes), encoding="utf-8")
    return ruta


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", help="URL del índice/temario del curso")
    ap.add_argument("--salida", required=True, help="Carpeta destino")
    ap.add_argument("--sesion", default="curso-estudio", help="Sesión de agent-browser")
    ap.add_argument("--puerto", type=int, help="Puerto CDP de un Chrome ya abierto")
    ap.add_argument("--selector", help="Selector CSS de los enlaces de lección")
    ap.add_argument("--descubrir", action="store_true",
                    help="Solo proponer selectores candidatos y salir")
    ap.add_argument("--solo-indice", action="store_true", help="Solo listar lecciones")
    ap.add_argument("--seguir", action="store_true",
                    help="Sin índice: encadenar enlaces 'siguiente'")
    ap.add_argument("--capturas", action="store_true",
                    help="Guardar screenshot completo de cada lección")
    ap.add_argument("--desde", type=int, default=1, help="Reanudar desde la lección N")
    ap.add_argument("--limite", type=int, default=300, help="Tope de lecciones")
    ap.add_argument("--espera", type=int, default=1200,
                    help="Pausa ms entre páginas (cortesía con el servidor)")
    args = ap.parse_args()

    destino = Path(args.salida)
    (destino / "lecciones").mkdir(parents=True, exist_ok=True)
    shots = destino / "capturas" if args.capturas else None
    if shots:
        shots.mkdir(exist_ok=True)

    if args.puerto:
        try:
            ab(["connect", str(args.puerto)], args.sesion, restore=False)
            print(f"Conectado a Chrome en CDP :{args.puerto}", file=sys.stderr)
        except ErrorNavegador as exc:
            print(f"No se pudo conectar a :{args.puerto} — {exc}", file=sys.stderr)
            return 2

    try:
        if args.descubrir:
            for c in descubrir_selectores(args.url, args.sesion, args.espera):
                print(f"{c['enlaces']:>4} enlaces  --selector \"{c['selector']}\"")
            return 0

        if args.seguir:
            lecciones = recorrer_siguientes(args.url, args.sesion, args.espera,
                                            args.limite)
        else:
            lecciones = descubrir_lecciones(args.url, args.sesion, args.espera,
                                            args.selector)[: args.limite]
    except MuroLogin as exc:
        print(f"\n{exc}\n", file=sys.stderr)
        return 3
    except (ErrorNavegador, subprocess.TimeoutExpired) as exc:
        print(f"Fallo abriendo el curso: {exc}", file=sys.stderr)
        return 2

    if not lecciones:
        print("No se detectó ninguna lección.\n"
              "Prueba:  --descubrir   (propone selectores)\n"
              "     o:  --seguir      (cursos sin índice navegable)", file=sys.stderr)
        return 1

    indice_md = ["# Índice detectado", "", f"Origen: {args.url}", ""]
    indice_md += [f"{i}. [{l['titulo']}]({l['url']})" for i, l in enumerate(lecciones, 1)]
    (destino / "INDICE.md").write_text("\n".join(indice_md) + "\n", encoding="utf-8")
    print(f"{len(lecciones)} lecciones -> {destino / 'INDICE.md'}")

    if args.solo_indice:
        return 0

    fallos, hechas = [], 0
    for i, leccion in enumerate(lecciones, 1):
        if i < args.desde:
            continue
        try:
            datos = con_reintentos(
                lambda l=leccion, n=i: extraer_leccion(l, args.sesion, args.espera,
                                                       shots, n)
            )
            ruta = escribir_leccion(destino / "lecciones", i, datos)
            hechas += 1
            extra = " +transcripción" if datos.get("transcripcion") else ""
            print(f"[{i}/{len(lecciones)}] {ruta.name}{extra}")
        except MuroLogin as exc:
            print(f"\n{exc}\n", file=sys.stderr)
            return 3
        except (ErrorNavegador, subprocess.TimeoutExpired) as exc:
            fallos.append((i, leccion["url"], str(exc)[:200]))
            print(f"[{i}/{len(lecciones)}] FALLO {leccion['url']}", file=sys.stderr)

    print(f"\n{hechas} lecciones extraídas, {len(fallos)} fallos -> {destino}")
    if fallos:
        (destino / "FALLOS.md").write_text(
            "\n".join(f"- {i} · {u} · {m}" for i, u, m in fallos) + "\n",
            encoding="utf-8",
        )
        print(f"Reanudar con:  --desde {fallos[0][0]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
