#!/usr/bin/env python3
"""Pico histórico de consumo de Claude Code en cualquier ventana rodante (5 h por
defecto, 168 h = semana).

Muchos planes tienen techos de consumo que el proveedor no publica en detalle, así
que se estima midiendo el pico real alcanzado en los transcripts locales. Es un
SUELO observado, no el límite oficial — si se llegó ahí sin evidencia de corte, el
techo real es >= al pico medido.

billable = input_tokens + output_tokens + cache_creation_input_tokens (la lectura
de caché, cache_read, se excluye — es mucho más barata y no debería contar igual).

Uso:
    python3 quota-peak.py              # ventana de 5 h
    python3 quota-peak.py --horas 168  # ventana semanal
"""
from __future__ import annotations

import argparse
import json
from collections import deque
from datetime import datetime
from pathlib import Path

_ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
_ap.add_argument("--horas", type=float, default=5, help="tamaño de la ventana rodante (5 = plan corto, 168 = semana)")
_args = _ap.parse_args()

HORAS = _args.horas
WINDOW_MS = int(HORAS * 60 * 60 * 1000)
PROJECTS = Path.home() / ".claude" / "projects"

events: list[tuple[int, int]] = []  # (timestamp_ms, billable)
files = 0

for path in PROJECTS.rglob("*.jsonl"):
    files += 1
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        continue
    for line in text.split("\n"):
        if not line or '"usage"' not in line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        usage = (row.get("message") or {}).get("usage")
        if not isinstance(usage, dict):
            continue
        ts_raw = row.get("timestamp")
        if not ts_raw:
            continue
        try:
            ts = int(datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00")).timestamp() * 1000)
        except ValueError:
            continue

        def num(key: str) -> int:
            v = usage.get(key)
            return v if isinstance(v, (int, float)) else 0

        billable = num("input_tokens") + num("output_tokens") + num("cache_creation_input_tokens")
        events.append((ts, billable))

events.sort()

# Ventana rodante: el máximo siempre ocurre en una ventana que ARRANCA en un evento.
window: deque[tuple[int, int]] = deque()
running = 0
peak = 0
peak_at = 0
for ts, billable in events:
    window.append((ts, billable))
    running += billable
    while window and ts - window[0][0] > WINDOW_MS:
        running -= window.popleft()[1]
    if running > peak:
        peak = running
        peak_at = ts

def fmt(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M")

print(f"ficheros escaneados : {files}")
print(f"mensajes con usage  : {len(events):,}")
if events:
    print(f"rango               : {fmt(events[0][0])}  ->  {fmt(events[-1][0])}")
print(f"PICO {HORAS:g}h (billable) : {peak:,} tokens")
print(f"alcanzado el        : {fmt(peak_at)}")

# Top 10 de ventanas de 5h más cargadas, separadas entre sí para no repetir el mismo pico.
tops: list[tuple[int, int]] = []
window.clear()
running = 0
for ts, billable in events:
    window.append((ts, billable))
    running += billable
    while window and ts - window[0][0] > WINDOW_MS:
        running -= window.popleft()[1]
    tops.append((running, ts))
tops.sort(reverse=True)
seen: list[int] = []
print(f"\ntop ventanas de {HORAS:g}h (separadas entre sí):")
for total, ts in tops:
    if any(abs(ts - s) < WINDOW_MS for s in seen):
        continue
    seen.append(ts)
    print(f"  {total:>12,}  hasta {fmt(ts)}")
    if len(seen) >= 10:
        break
