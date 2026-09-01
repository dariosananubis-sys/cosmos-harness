#!/usr/bin/env python3
"""Báscula de contexto de Claude Code: mide el coste de arranque y el peso de cada sesión.

Para qué
--------
Es la báscula que hace verificable cualquier optimización del gasto de contexto. Sin medir
antes/después, "he bajado el gasto" es una impresión. Con esto es un número.

Mide tres cosas, todas leídas de los transcripts .jsonl reales (deduplicando por requestId,
que en el .jsonl aparece 3-4 veces):

1. **arranque**: coste fijo del primer request de cada sesión NUEVA reciente. Es el
   system prompt + CLAUDE.md + ORQUESTADOR.md + catálogo de skills + hooks de SessionStart.
   Se paga entero cada vez que se abre una ventana o un subagente. Es la palanca mayor:
   bajarlo ahorra en TODAS partes.
2. **sesiones**: contexto del último turno real de cada sesión activa (lo que se
   reenvía en cada mensaje) + coste equivalente acumulado de la sesión.
3. **total**: suma del coste equivalente de todas las sesiones vivas.

coste equivalente = cache_creation*1.25 + cache_read*0.10 (multiplicadores de facturación de
Anthropic respecto a input). Es la unidad comparable entre "crear caché" y "releer caché".

Uso
---
    python3 tools/medir-contexto-claude.py                 # informe legible
    python3 tools/medir-contexto-claude.py --json          # JSON (para diff antes/después)
    python3 tools/medir-contexto-claude.py --json > antes.json
    # ... aplicar una mejora, abrir una ventana nueva ...
    python3 tools/medir-contexto-claude.py --json > despues.json
    python3 tools/medir-contexto-claude.py --diff antes.json despues.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from pathlib import Path

CLAW = Path(__file__).resolve().parent.parent / ".claude" / "claudeclaw"
# Claude Code deriva el slug del proyecto sustituyendo "/" por "-" en la ruta absoluta del repo.
PROJECT = os.environ.get("CLAUDE_PROJECT_SLUG") or str(Path(__file__).resolve().parent.parent).replace("/", "-")


def config_dir() -> Path:
    """Base de transcripts de la cuenta que gasta (CLAUDE_CONFIG_DIR), como el resto del arnés."""
    cfg = os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude"))
    return Path(cfg) / "projects" / PROJECT


def session_ids() -> dict[str, str]:
    """{sessionId: nombre} de sesiones conocidas (opcional, vía sessions.json/session.json si existen) + el global."""
    ids: dict[str, str] = {}
    try:
        th = json.loads((CLAW / "sessions.json").read_text(encoding="utf-8")).get("threads", {})
        for tid, s in th.items():
            if s.get("sessionId"):
                ids[s["sessionId"]] = tid
    except (OSError, json.JSONDecodeError):
        pass
    try:
        g = json.loads((CLAW / "session.json").read_text(encoding="utf-8"))
        if g.get("sessionId"):
            ids[g["sessionId"]] = "global"
    except (OSError, json.JSONDecodeError):
        pass
    return ids


def escanea(path: Path) -> dict:
    """Recorre un .jsonl una vez. Devuelve métricas dedup por requestId."""
    seen: set = set()
    arranque = 0          # cache_creation del primer request (coste de abrir la sesión)
    ctx_final = 0         # contexto del último turno con tokens (lo que se reenvía)
    ctx_max = 0
    cache_new = cache_read = reqs = 0
    for line in _lines(path):
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        m = o.get("message") or {}
        u = m.get("usage")
        if not u:
            continue
        rid = o.get("requestId") or m.get("id")
        if rid in seen:
            continue
        seen.add(rid)
        reqs += 1
        cn = u.get("cache_creation_input_tokens", 0)
        cr = u.get("cache_read_input_tokens", 0)
        inp = u.get("input_tokens", 0)
        if reqs == 1:
            arranque = cn
        cache_new += cn
        cache_read += cr
        ctx = inp + cr + cn
        if ctx > 0:
            ctx_final = ctx
            ctx_max = max(ctx_max, ctx)
    equiv = int(cache_new * 1.25 + cache_read * 0.10)
    return {
        "reqs": reqs, "arranque": arranque, "ctx_final": ctx_final,
        "ctx_max": ctx_max, "cache_new": cache_new, "cache_read": cache_read,
        "equiv": equiv,
    }


def _lines(path: Path):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        yield from fh


def recoge() -> dict:
    base = config_dir()
    ids = session_ids()
    sesiones = []
    arranques = []
    total_equiv = 0
    for sid, nombre in ids.items():
        hits = glob.glob(str(base / f"{sid}*.jsonl"))
        if not hits:
            continue
        p = Path(hits[0])
        met = escanea(p)
        met.update(thread=nombre, sessionId=sid, mb=round(p.stat().st_size / 1048576, 1))
        sesiones.append(met)
        total_equiv += met["equiv"]
        if met["arranque"] > 50000:      # un arranque real ronda 100k; <50k es una sesión continuada
            arranques.append(met["arranque"])
    sesiones.sort(key=lambda m: -m["ctx_final"])
    arranque_medio = int(sum(arranques) / len(arranques)) if arranques else 0
    return {
        "arranque_medio": arranque_medio,
        "arranque_muestras": len(arranques),
        "total_equiv": total_equiv,
        "sesiones": sesiones,
    }


def imprime(d: dict) -> None:
    print(f"ARRANQUE medio (coste fijo por sesión nueva): {d['arranque_medio']:,} tok "
          f"(de {d['arranque_muestras']} sesiones)")
    print(f"COSTE EQUIVALENTE total de sesiones vivas:    {d['total_equiv']/1e6:.2f}M tok\n")
    print(f"{'thread':<20} {'ctx_final':>10} {'ctx_max':>10} {'equiv':>9} {'MB':>5}")
    for s in d["sesiones"]:
        print(f"{s['thread']:<20} {s['ctx_final']:>10,} {s['ctx_max']:>10,} "
              f"{s['equiv']/1000:>8.0f}k {s['mb']:>5}")


def diff(a_path: str, b_path: str) -> None:
    a = json.loads(Path(a_path).read_text())
    b = json.loads(Path(b_path).read_text())
    da = b["arranque_medio"] - a["arranque_medio"]
    print(f"ARRANQUE: {a['arranque_medio']:,} -> {b['arranque_medio']:,} tok "
          f"({da:+,}  {da/max(a['arranque_medio'],1)*100:+.1f}%)")
    dt = b["total_equiv"] - a["total_equiv"]
    print(f"TOTAL equiv: {a['total_equiv']/1e6:.2f}M -> {b['total_equiv']/1e6:.2f}M "
          f"({dt/1e6:+.2f}M)")
    if da < 0:
        print(f"\nAHORRO por arranque: {-da:,} tok. En 100 sesiones nuevas = {-da*100/1e6:.1f}M tok menos.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Báscula de contexto de Claude Code.")
    ap.add_argument("--json", action="store_true", help="salida JSON para comparar antes/después")
    ap.add_argument("--diff", nargs=2, metavar=("ANTES", "DESPUES"), help="compara dos ficheros --json")
    args = ap.parse_args()
    if args.diff:
        diff(*args.diff)
        return 0
    d = recoge()
    if args.json:
        json.dump(d, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        imprime(d)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
