#!/usr/bin/env python3
"""Dedupe de bloques auto-capture apilados en notas diarias tipo notes/daily/*.md.

Pensado para el caso en que un hook de auto-captura re-appendea la sesión entera en
vez de actualizar el bloque existente (p.ej. por un marcador que deja de matchear):
el mismo bloque queda repetido N veces según crece su transcript.

Este script deja UN bloque por identificador de sesión: el "más completo" según el
metadato que definas en SID (por defecto, el de mayor "Transcript: N KB"). Todo lo
que no sea un bloque auto-capture (notas a mano, cierres manuales) se preserva byte
a byte — hay una guarda dura (assert) que lo comprueba antes de escribir.

Ajusta las tres expresiones regulares (OPEN/CLOSE/SID) al formato exacto que use tu
hook de auto-captura; tal como está, reconoce bloques delimitados por un encabezado
"## Auto-capture" y un pie "Generado automáticamente por...", con una línea
"Session ID: `...` | Transcript: N KB" dentro.

Uso:  dedupe-daily-autocapture.py [--apply] <fichero.md>...
      Sin --apply hace dry-run.
"""
import re
import sys
from pathlib import Path

FRONTMATTER = "---\ntype: session-log"
OPEN = re.compile(r"\n\n---\n\n## ⚠️ Auto-capture adicional \(\d\d:\d\d\) — `[^`]*`\n\n")
CLOSE = re.compile(r"---\n\*Generado automáticamente por `auto-capture\.py` a las \d\d:\d\d\*")
SID = re.compile(r"> Session ID: `([^`]+)`  \|  Transcript: (\d+) KB")


def find_blocks(text):
    """Spans (start, end, sid, kb) de cada bloque auto-capture completo.

    El frontmatter inicial del fichero NO entra en ningún bloque: es preámbulo del
    daily y debe sobrevivir aunque su bloque caiga por duplicado.
    """
    starts = []
    if text.startswith(FRONTMATTER):
        starts.append(text.index("\n---\n", len(FRONTMATTER)) + len("\n---\n"))
    starts += [m.start() for m in OPEN.finditer(text)]

    blocks = []
    for s in starts:
        close = CLOSE.search(text, s)
        if not close:
            continue  # bloque truncado -> no lo tocamos
        # Un bloque no puede contener otra apertura: si la hay, aquí no empieza un
        # bloque (p.ej. el primero ya se dedupeó en una pasada previa). Mantiene
        # esto idempotente.
        nxt = OPEN.search(text, s + 1)
        if nxt and nxt.start() < close.start():
            continue
        end = close.end()
        meta = SID.search(text, s, end)
        if not meta:
            continue  # sin Session ID -> no sabemos deduplicar, se preserva
        blocks.append((s, end, meta.group(1), int(meta.group(2))))
    return blocks


def winners(blocks):
    """Por session_id, el bloque con más KB (el último en caso de empate)."""
    best = {}
    for b in blocks:
        _, _, sid, kb = b
        if sid not in best or kb >= best[sid][3]:
            best[sid] = b
    return {(b[0], b[1]) for b in best.values()}


def dedupe(text):
    blocks = find_blocks(text)
    if not blocks:
        return text, 0, 0
    keep = winners(blocks)

    out, prev_end, dropped = [], 0, 0
    for s, e, sid, kb in blocks:
        out.append(text[prev_end:s])  # gap = contenido a mano, SIEMPRE se preserva
        if (s, e) in keep:
            out.append(text[s:e])
        else:
            dropped += 1
        prev_end = e
    out.append(text[prev_end:])
    return "".join(out), len(blocks), dropped


def non_block_text(text):
    """Todo lo que NO es bloque — debe sobrevivir intacto al dedupe."""
    blocks = find_blocks(text)
    out, prev_end = [], 0
    for s, e, _, _ in blocks:
        out.append(text[prev_end:s])
        prev_end = e
    out.append(text[prev_end:])
    return "".join(out)


def main():
    args = sys.argv[1:]
    apply = "--apply" in args
    paths = [Path(a) for a in args if a != "--apply"]

    for p in paths:
        text = p.read_text()
        new, total, dropped = dedupe(text)
        if total == 0:
            print(f"{p.name}: sin bloques auto-capture, intacto")
            continue

        # Guarda dura: ni una línea de contenido a mano puede perderse.
        assert non_block_text(text) == non_block_text(new), f"{p}: contenido a mano alterado"

        before, after = len(text.splitlines()), len(new.splitlines())
        print(
            f"{p.name}: {total} bloques -> {total - dropped} ({dropped} dup fuera) | "
            f"{before} -> {after} lineas (-{before - after})"
        )
        if apply:
            p.write_text(new)


if __name__ == "__main__":
    main()
