#!/usr/bin/env python3
"""Barrido de los transcripts .jsonl de Claude Code: saca lo útil de cada sesión
(tus prompts + cómo cerró el asistente) agrupado por día, para poder consolidar
notas y memoria sin meter cientos de MB de tool-results en el contexto.

Uso:
    python3 barrido-transcripts.py <dir-salida> --proyecto <nombre-carpeta-en-~/.claude/projects> [--dias N] [--crudo]

    --proyecto   nombre exacto de la carpeta bajo ~/.claude/projects (Claude Code la
                 deriva de la ruta del repo con guiones; listar ~/.claude/projects
                 para verla) — obligatorio, no hay valor por defecto razonable entre
                 máquinas distintas.
    --dias N     solo sesiones cuyo primer mensaje sea de los últimos N días
    --crudo      no filtra el ruido (hooks automáticos, pings, keepalives)

Salida: <dir-salida>/dia-YYYY-MM-DD.md + INDEX.md

Por qué existe: buscar por palabra sobre el histórico sirve para encontrar un dato
suelto, pero para consolidar hace falta LEER un día entero seguido. Sin filtro, gran
parte de las sesiones son ruido de automatismos (hooks que abren sesión por cada
evento, daemons que hacen ping) y el día se vuelve ilegible.
"""
import argparse, json, os, re, sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

PROYECTOS = os.path.expanduser("~/.claude/projects")

# Sesiones que abre un automatismo, no un humano. Si TODOS sus prompts casan, la
# sesión se tira. Ajusta este patrón a los automatismos de tu propio harness.
RUIDO = re.compile(
    r"^(Review this change for security|You previously flagged these candidate|"
    r"responde solo|di solo|responde en una linea|cuenta hasta|Ejecuta: |"
    r"Ejecuta en bash|Ponle nombre a esta tarea|Olvida lo anterior|"
    r"Sin usar herramientas|Sin herramientas|Start the heartbeat|Stop the heartbeat|"
    r"Wakeup, my friend|Stop hook feedback|hola$|claude$|Continue from where|"
    r"\[\d{4}-\d\d-\d\d \d\d:\d\d:\d\d UTC|# /|<!-- generado por|"
    r"Base directory for this skill|A session-scoped Stop hook|"
    r"\[Your previous response had no visible output)", re.I)

# Prefijos que nunca son texto humano aunque vengan en un mensaje 'user'.
TECNICO = re.compile(
    r"^(<local-command|<command-name>|<command-message>|<command-args>|Caveat:|"
    r"<local-command-stdout|<system-reminder|\[Request interrupted|"
    r"<user-prompt-submit-hook|<bash-input>|<bash-stdout>|<bash-stderr>|API Error|"
    r"This session is being continued|<task-notification|\[Image)")


def texto(msg):
    c = msg.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(x.get("text", "") for x in c
                         if isinstance(x, dict) and x.get("type") == "text")
    return ""


def limpiar(t):
    t = re.sub(r"<system-reminder>.*?</system-reminder>", "", t, flags=re.S)
    t = re.sub(r"<local-command-stdout>.*?</local-command-stdout>", "", t, flags=re.S)
    return t.strip()


def barrer(raiz, corte, crudo):
    dias = defaultdict(list)
    for fn in sorted(os.listdir(raiz)):
        if not fn.endswith(".jsonl"):
            continue
        prompts, cierre, primero = [], "", None
        try:
            fh = open(os.path.join(raiz, fn), errors="replace")
        except OSError:
            continue
        with fh:
            for linea in fh:
                try:
                    d = json.loads(linea)
                except Exception:
                    continue
                ts = d.get("timestamp")
                if ts and not primero:
                    primero = ts
                if d.get("type") == "user":
                    m = d.get("message", {})
                    if not isinstance(m, dict):
                        continue
                    t = limpiar(texto(m))
                    if not t or TECNICO.match(t) or len(t) < 12:
                        continue
                    if not crudo and RUIDO.match(t):
                        continue
                    prompts.append(((ts or "")[11:16], t[:320] + (" […]" if len(t) > 320 else "")))
                elif d.get("type") == "assistant":
                    m = d.get("message", {})
                    if isinstance(m, dict):
                        t = limpiar(texto(m))
                        if t:
                            cierre = t[:320]
        if not prompts or not primero:
            continue
        if corte and primero[:10] < corte:
            continue
        dias[primero[:10]].append((fn[:8], primero, prompts, cierre))
    return dias


def escribir(dias, salida):
    os.makedirs(salida, exist_ok=True)
    idx = []
    for dia, sesiones in sorted(dias.items()):
        p = os.path.join(salida, f"dia-{dia}.md")
        n = 0
        with open(p, "w") as f:
            f.write(f"# {dia} — {len(sesiones)} sesiones con trabajo real\n")
            for sid, ts, prompts, cierre in sorted(sesiones, key=lambda s: s[1]):
                f.write(f"\n## {sid} · {ts} ({len(prompts)} prompts)\n")
                for hora, t in prompts:
                    n += 1
                    f.write(f"- [{hora}] {t}\n")
                if cierre:
                    f.write(f"  > CIERRE: {cierre}\n")
        idx.append((dia, len(sesiones), n, os.path.getsize(p)))
    with open(os.path.join(salida, "INDEX.md"), "w") as f:
        f.write("| dia | sesiones | prompts | bytes |\n|---|---|---|---|\n")
        for fila in idx:
            f.write("| %s | %d | %d | %d |\n" % fila)
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("salida")
    ap.add_argument("--dias", type=int, default=0)
    ap.add_argument("--crudo", action="store_true")
    ap.add_argument("--proyecto", required=True,
                     help="carpeta exacta bajo ~/.claude/projects (ls ~/.claude/projects para verla)")
    a = ap.parse_args()
    raiz = os.path.join(PROYECTOS, a.proyecto)
    if not os.path.isdir(raiz):
        sys.exit(f"no existe {raiz}")
    corte = ""
    if a.dias:
        corte = (datetime.now(timezone.utc) - timedelta(days=a.dias)).strftime("%Y-%m-%d")
    idx = escribir(barrer(raiz, corte, a.crudo), a.salida)
    for dia, ses, pr, b in idx:
        print(f"{dia}  {ses:>3} sesiones  {pr:>4} prompts  {b:>7} b")


if __name__ == "__main__":
    main()
