#!/usr/bin/env python3
"""Auditor de fugas de tokens de un harness de Claude Code — solo lectura, salida
corta. Mide el presupuesto de contexto que tu propio repo mete en CADA sesión, sin
que nadie lo pida: hooks de UserPromptSubmit, rules cargadas siempre (`paths:` mal
puesto o ausente cuando debería ser lazy), el catálogo de skills/agentes/comandos
que el CLI inyecta en el system prompt (incluyendo el de los plugins habilitados),
duplicación literal entre CLAUDE.md y las rules, y ficheros de memoria huérfanos.

Uso:  python3 auditar-gasto.py               # audita
      python3 auditar-gasto.py --arreglar    # reaplica los plugins de PLUGINS_APAGADOS a false

Sale 1 si detecta una fuga (rule mal-path fuera de la lista blanca, catálogo por
encima del presupuesto, o un plugin descartado/apagado que ha vuelto a activarse);
0 si limpio.

Antes de usarlo en tu repo, rellena las tres listas de abajo (GLOBALES_OK,
PLUGINS_DESCARTADOS, PLUGINS_APAGADOS) y PRESUPUESTO_CATALOGO con tu propio
histórico — están vacías/a modo de ejemplo a propósito.
"""
from __future__ import annotations
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOK = 4  # bytes/token aprox

# Rules que SON legítimamente globales (paths:**) en tu repo. Cualquier otra global
# que detecte el auditor se marca como fuga. Rellena con los nombres de fichero
# (sin ruta) de tus rules realmente globales, p.ej. {"seguridad.md", "git.md"}.
GLOBALES_OK: set[str] = set()

# Plugins que decidiste descartar con evidencia (coste medido sin uso real). Si
# reaparecen habilitados en settings.json, es una regresión.
PLUGINS_DESCARTADOS: set[str] = set()

# Plugins apagados por decisión medida (poco o ningún uso en tus transcripts).
# OJO: borrar la llave de settings.json no los apaga — algunos harnesses la
# reescriben a `true` en el siguiente bootstrap. La única forma estable suele ser
# dejar la llave explícita a `false`.
PLUGINS_APAGADOS: set[str] = set()

# Techo del catálogo (skills+agentes+comandos+plugins) que se inyecta en cada
# sesión. Ponlo justo por encima de tu estado ya revisado y aprobado — un
# presupuesto siempre en rojo no avisa de nada nuevo.
PRESUPUESTO_CATALOGO = 15000


def _tok(txt: str) -> int:
    return len(txt.encode()) // TOK


def _frontmatter(md: str) -> str:
    m = re.match(r"^---\n(.*?)\n---", md, re.S)
    return m.group(1) if m else ""


def por_turno() -> list[str]:
    """Bytes reales que meten los hooks UserPromptSubmit en cada turno.

    Ajusta la lista de nombres de hook a los tuyos (o vacíala si no usas hooks
    UserPromptSubmit que inyecten texto en cada turno).
    """
    out = []
    stdin = '{"hook_event_name":"UserPromptSubmit"}'
    for hook in ():  # p.ej. ("mis-notas.sh", "mis-recordatorios.sh")
        p = REPO / ".claude/hooks" / hook
        if not p.exists():
            continue
        r = subprocess.run(["bash", str(p)], input=stdin, capture_output=True, text=True)
        out.append(f"  {hook}: ~{_tok(r.stdout)} tok/turno")
    return out


def rules_fuga() -> tuple[list[str], int, int]:
    """Devuelve (fugas, tok_globales, n_globales)."""
    fugas, tok_glob, n_glob = [], 0, 0
    for p in sorted((REPO / ".claude/rules").glob("*.md")):
        fm = _frontmatter(p.read_text())
        tiene_paths = "paths:" in fm
        es_universal = '"**"' in fm or "'**'" in fm
        global_ = es_universal or not tiene_paths
        if global_:
            tok_glob += _tok(p.read_text())
            n_glob += 1
            if p.name not in GLOBALES_OK:
                motivo = "paths:**" if es_universal else "sin paths:"
                fugas.append(f"  FUGA {p.name} ({motivo}, ~{_tok(p.read_text())} tok/sesión) -> pasar a lazy")
    return fugas, tok_glob, n_glob


def duplicacion() -> list[str]:
    def frases(t: str) -> set[str]:
        return {f.strip() for f in re.split(r"[.\n]", t) if len(f.strip()) > 70}
    cm = frases((REPO / "CLAUDE.md").read_text())
    dup = []
    for p in sorted((REPO / ".claude/rules").glob("*.md")):
        inter = cm & frases(p.read_text())
        if inter:
            dup.append(f"  {p.name}: {len(inter)} frase(s) duplicada(s) con CLAUDE.md")
    return dup


def catalogo() -> tuple[list[str], int]:
    """Coste del catálogo que el harness inyecta en el system prompt de CADA sesión.

    Skills, agentes y comandos se listan siempre (nombre + description), se usen o
    no. Suele ser el mayor bloque de contexto fijo.
    """
    def desc(p: Path) -> int:
        m = re.match(r"^---\n(.*?)\n---", p.read_text(errors="ignore")[:12000], re.S)
        return len(m.group(1)) // TOK if m else 0

    sk = ag = cm = 0
    raiz = REPO / ".claude/skills"
    if raiz.is_dir():
        for d in raiz.iterdir():
            if not d.is_dir() or d.name.startswith("_"):
                continue  # convención: un prefijo "_" archiva la skill (no se carga)
            if (d / "SKILL.md").exists():
                sk += desc(d / "SKILL.md")
            for n in d.glob("skills/*/SKILL.md"):
                sk += desc(n)
    for p in (REPO / ".claude/agents").glob("**/*.md"):
        ag += desc(p)
    for p in (REPO / ".claude/commands").glob("**/*.md"):
        cm += desc(p)

    # Un plugin habilitado mete SUS skills/agentes/comandos en el mismo catálogo,
    # normalmente cacheados fuera del repo — si no se cuentan, quedan invisibles.
    pl = 0
    cache = Path.home() / ".claude/plugins/cache"
    for clave, on in _plugins().items():
        if not on or "@" not in clave:
            continue
        base = cache / clave.split("@")[1] / clave.split("@")[0]
        if not base.is_dir():
            continue
        vers = sorted(d for d in base.iterdir() if d.is_dir())
        if not vers:
            continue
        for patron in ("skills/*/SKILL.md", "agents/*.md", "commands/**/*.md"):
            pl += sum(desc(p) for p in vers[-1].rglob(patron))

    tot = sk + ag + cm + pl
    out = [f"  skills ~{sk} tok · agentes ~{ag} tok · comandos ~{cm} tok · "
           f"plugins ~{pl} tok = ~{tot} tok/sesión"]
    if tot > PRESUPUESTO_CATALOGO:
        out.append(f"  FUGA catálogo ~{tot} tok > presupuesto {PRESUPUESTO_CATALOGO} "
                   f"-> archivar lo que no se usa o apagar plugins (llave a false)")
    return out, tot


def _plugins() -> dict[str, bool]:
    import json
    p = REPO / ".claude/settings.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text()).get("enabledPlugins", {})


def plugins_regresion() -> list[str]:
    """Plugins descartados/apagados que han vuelto, y llaves que el harness puede resucitar."""
    ep = _plugins()
    out = [f"  REGRESIÓN plugin descartado habilitado: {p}"
           for p in sorted(PLUGINS_DESCARTADOS) if ep.get(p)]
    out += [f"  REGRESIÓN plugin apagado por decisión vuelve a estar ON: {p}"
            for p in sorted(PLUGINS_APAGADOS - PLUGINS_DESCARTADOS) if ep.get(p)]
    # Borrar la llave no apaga nada si tu harness la reescribe a `true` sola.
    sin_llave = sorted(p for p in PLUGINS_APAGADOS if p not in ep)
    if sin_llave:
        out.append("  SIN LLAVE (el harness podría volver a encenderlos; ponlos a false): "
                   + ", ".join(sin_llave))
    return out


def reaplicar_plugins() -> list[str]:
    """`--arreglar`: deja los plugins de PLUGINS_APAGADOS a `false` (no toca nada más)."""
    import json
    p = REPO / ".claude/settings.json"
    d = json.loads(p.read_text())
    ep = d.setdefault("enabledPlugins", {})
    tocados = [k for k in sorted(PLUGINS_APAGADOS) if ep.get(k) is not False]
    if not tocados:
        return ["  ya estaban todos a false (nada que hacer)"]
    for k in tocados:
        ep[k] = False
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    return [f"  apagado: {k}" for k in tocados]


def huerfanos_memory() -> int:
    mem = REPO / "memory"
    idx_f = mem / "MEMORY.md"
    if not idx_f.exists():
        return 0
    idx = idx_f.read_text()
    n = 0
    for f in mem.glob("*.md"):
        if f.name != "MEMORY.md" and f"({f.name})" not in idx:
            n += 1
    return n


def main() -> int:
    if "--arreglar" in sys.argv:
        print("== REAPLICANDO PLUGINS APAGADOS ==")
        for l in reaplicar_plugins():
            print(l)
        return 0
    print("== AUDITOR DE GASTO DEL ARNÉS ==")
    print("[por-turno] hooks UserPromptSubmit:")
    for l in por_turno():
        print(l)

    fugas, tok_glob, n_glob = rules_fuga()
    print(f"[rules] {n_glob} globales = ~{tok_glob} tok/sesión")
    for l in fugas:
        print(l)
    if not fugas:
        print("  sin rules mal-path (todas las globales están en la lista blanca)")

    cat_lineas, cat_tok = catalogo()
    print("[catálogo system prompt] skills/agentes/comandos:")
    for l in cat_lineas:
        print(l)

    regres = plugins_regresion()
    print("[plugins descartados]:")
    for l in (regres or ["  ninguno habilitado (correcto)"]):
        print(l)

    dup = duplicacion()
    print("[dup CLAUDE.md<->rules]:")
    for l in (dup or ["  cero duplicación"]):
        print(l)

    h = huerfanos_memory()
    print(f"[memory] {h} ficheros fuera del índice "
          f"(se recuperan por búsqueda/grep; meterlos subiría tokens del índice)")

    problemas = fugas + regres + [l for l in cat_lineas if "FUGA" in l]
    print("VEREDICTO:", "FUGA NUEVA (ver arriba)" if problemas else "limpio")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
