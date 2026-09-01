#!/usr/bin/env python3
"""
Telegram Bridge para Claude Code
Escucha mensajes de Telegram y los ejecuta en Claude Code CLI.
Responde con el output directamente en el chat.

Setup: ver tools/TELEGRAM_SETUP.md
"""

import os
import re
import subprocess
import sys
import time
import requests

# ── Configuración (editar antes de usar) ─────────────────────────────────────
BOT_TOKEN      = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ALLOWED_USER_ID = int(os.environ.get("VANGUARDIA_TELEGRAM_USER_ID", "0"))
WORKSPACE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ej. D:/tu-workspace
CLAUDE_TIMEOUT = 600  # segundos máximos por respuesta (10 min)
# ─────────────────────────────────────────────────────────────────────────────

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"
MAX_MSG_LEN = 4000  # Telegram limit es 4096, dejamos margen


def validate_config():
    if not BOT_TOKEN:
        print("ERROR: Variable de entorno TELEGRAM_BOT_TOKEN no definida.")
        print("Ejecuta: set TELEGRAM_BOT_TOKEN=tu_token_aqui")
        sys.exit(1)
    if ALLOWED_USER_ID == 0:
        print("ERROR: Variable de entorno VANGUARDIA_TELEGRAM_USER_ID no definida.")
        print("Ejecuta: set VANGUARDIA_TELEGRAM_USER_ID=tu_id_de_telegram")
        sys.exit(1)


def get_updates(offset=None):
    params = {"timeout": 30, "offset": offset}
    try:
        r = requests.get(f"{API_BASE}/getUpdates", params=params, timeout=35)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[WARN] getUpdates falló: {e}")
        time.sleep(5)
        return {"result": []}


def md_to_html(text: str) -> str:
    """Convierte Markdown de Claude Code al subconjunto HTML que admite Telegram."""
    # Extraer bloques de código con placeholders para no procesarlos
    blocks = []
    def save_block(m):
        blocks.append(f"<pre><code>{m.group(1).strip()}</code></pre>")
        return f"\x00BLOCK{len(blocks)-1}\x00"
    def save_inline(m):
        blocks.append(f"<code>{m.group(1)}</code>")
        return f"\x00BLOCK{len(blocks)-1}\x00"

    text = re.sub(r"```(?:\w+)?\n(.*?)```", save_block, text, flags=re.DOTALL)
    text = re.sub(r"`([^`\n]+)`", save_inline, text)

    # Escapar HTML en texto plano (orden: & primero)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Headings
    text = re.sub(r"^#{1,6} (.+)$", r"<b>\1</b>", text, flags=re.MULTILINE)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Italic *text* (sin matchear **)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    # Italic _text_ (con word boundaries para no romper snake_case)
    text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"<i>\1</i>", text)
    # Strikethrough
    text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text)

    # Restaurar bloques de código
    for i, block in enumerate(blocks):
        text = text.replace(f"\x00BLOCK{i}\x00", block)

    return text


def send_message(chat_id, text):
    """Envía texto dividido en chunks si supera el límite de Telegram."""
    if not text or not text.strip():
        text = "(sin output)"
    text = md_to_html(text)
    chunks = [text[i:i + MAX_MSG_LEN] for i in range(0, len(text), MAX_MSG_LEN)]
    for chunk in chunks:
        try:
            requests.post(f"{API_BASE}/sendMessage", json={
                "chat_id": chat_id,
                "text": chunk,
                "parse_mode": "HTML"
            }, timeout=10)
        except Exception as e:
            print(f"[WARN] sendMessage falló: {e}")


def send_typing(chat_id):
    try:
        requests.post(f"{API_BASE}/sendChatAction",
                      json={"chat_id": chat_id, "action": "typing"},
                      timeout=5)
    except Exception:
        pass


CONTEXT_PREFIX = (
    "Estás en el workspace del proyecto. Workspace raíz: WORKSPACE.\n"
    "Tienes acceso COMPLETO a todo el workspace, igual que en una sesión interactiva:\n"
    "  - projects/   → contexto y CLAUDE.md de cada proyecto\n"
    "  - src/         → código fuente de todos los proyectos (submodulos git)\n"
    "  - tools/       → scripts y utilidades (codex-delegate.sh, etc.)\n"
    "  - notes/       → Obsidian vault (ADRs, runbooks, dailies)\n"
    "  - .claude/     → skills, agents, commands disponibles\n"
    "Herramientas disponibles: Read, Edit, Write, Bash, Glob, Grep, Agent, y todas las skills/agentes de .claude/.\n"
    "Usa las skills y agentes que la tarea requiera, exactamente igual que en sesión interactiva.\n"
    "El CLAUDE.md raíz está en la raíz del workspace — léelo si necesitas contexto del proyecto.\n"
    "Responde siempre en castellano.\n\n"
    "ORDEN DEL USUARIO:\n"
)


def run_claude(prompt: str) -> str:
    """Ejecuta claude -p en el workspace y devuelve el output."""
    full_prompt = CONTEXT_PREFIX + prompt
    try:
        env = os.environ.copy()
        env["_VANGUARDIA_PROMPT"] = full_prompt
        result = subprocess.run(
            'claude -p "%_VANGUARDIA_PROMPT%" --output-format text --dangerously-skip-permissions',
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=WORKSPACE,
            timeout=CLAUDE_TIMEOUT,
            shell=True,
            env=env,
        )
        output = result.stdout.strip()
        if result.returncode != 0 and result.stderr:
            output += f"\n\n⚠️ stderr:\n{result.stderr.strip()}"
        return output or "(sin output)"
    except subprocess.TimeoutExpired:
        return f"⏱ Timeout: la tarea superó {CLAUDE_TIMEOUT // 60} minutos."
    except FileNotFoundError:
        return "❌ Error: `claude` no encontrado en el PATH. ¿Claude Code está instalado?"
    except Exception as e:
        return f"❌ Error inesperado: {e}"


def handle_message(msg: dict):
    chat_id = msg["chat"]["id"]
    user_id = msg.get("from", {}).get("id")
    text = msg.get("text", "").strip()

    if user_id != ALLOWED_USER_ID:
        print(f"[WARN] Mensaje ignorado de user_id={user_id} (no autorizado)")
        return

    if not text:
        return

    # Comandos internos del bridge
    if text.lower() == "/ping":
        send_message(chat_id, "🟢 Bridge activo.")
        return
    if text.lower() == "/help":
        send_message(chat_id, (
            "*Claude Code Bridge*\n"
            "Escribe cualquier orden en lenguaje natural y Claude Code la ejecutará en tu workspace.\n\n"
            "Comandos del bridge:\n"
            "`/ping` — verificar conexión\n"
            "`/help` — esta ayuda\n\n"
            f"Workspace: `{WORKSPACE}`\n"
            f"Timeout por tarea: {CLAUDE_TIMEOUT // 60} min"
        ))
        return

    print(f"[INFO] Orden recibida: {text[:80]}{'...' if len(text) > 80 else ''}")
    send_typing(chat_id)
    send_message(chat_id, "⏳ Procesando...")

    output = run_claude(text)
    send_message(chat_id, output)
    print(f"[INFO] Respuesta enviada ({len(output)} chars)")


def main():
    validate_config()
    print(f"✓ Telegram Bridge para Claude Code arrancado")
    print(f"  Workspace : {WORKSPACE}")
    print(f"  User ID   : {ALLOWED_USER_ID}")
    print(f"  Timeout   : {CLAUDE_TIMEOUT}s")
    print("  Esperando mensajes... (Ctrl+C para parar)\n")

    offset = None
    while True:
        data = get_updates(offset)
        for update in data.get("result", []):
            offset = update["update_id"] + 1
            if "message" in update:
                handle_message(update["message"])


if __name__ == "__main__":
    main()
