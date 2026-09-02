"""Wrapper de la API de Google Chat para mandar mensajes 1:1 desde un bot de
Service Account.

Auth vía Service Account (variable de entorno GOOGLE_CHAT_SA_JSON, ruta al
JSON de credenciales).

Requisitos:
- Chat API habilitada en el proyecto GCP de esa Service Account.
- Chat App configurada (nombre, visibility list, Receive 1:1 + Join spaces).
- El destinatario debe haber iniciado conversación con el bot al menos UNA vez
  (limitación de la Chat API — el bot no puede crear DMs unilateralmente sin
  domain-wide delegation).

Uso CLI:
    python -m google-chat-dm list-spaces
    python -m google-chat-dm send <user_email> "<texto>"
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import typer
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from log import api_call, api_response, fail, info, ok, step

SCOPES = [
    "https://www.googleapis.com/auth/chat.bot",
]
SPACE_CACHE = Path(os.environ.get("GOOGLE_CHAT_CACHE_DIR", ".")) / "chat-spaces.json"
BOT_NAME = os.environ.get("GOOGLE_CHAT_BOT_NAME", "Bot")

app = typer.Typer(no_args_is_help=True)


def _sa_path() -> str:
    p = os.environ.get("GOOGLE_CHAT_SA_JSON")
    if not p:
        fail("GOOGLE_CHAT_SA_JSON no definida en el entorno (ruta al JSON de la Service Account)")
        sys.exit(1)
    return p


def _client():
    creds = service_account.Credentials.from_service_account_file(
        _sa_path(), scopes=SCOPES
    )
    return build("chat", "v1", credentials=creds, cache_discovery=False)


def _load_cache() -> dict:
    if SPACE_CACHE.exists():
        return json.loads(SPACE_CACHE.read_text())
    return {}


def _save_cache(data: dict) -> None:
    SPACE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    SPACE_CACHE.write_text(json.dumps(data, indent=2))


def _resolve_space_for_user(user_email: str) -> str:
    """Devuelve el name del space DM con `user_email`. Cachea en chat-spaces.json."""
    cache = _load_cache()
    if user_email in cache:
        return cache[user_email]
    api_call("GET", f"chat.spaces.findDirectMessage(users/{user_email})")
    chat = _client()
    try:
        space = (
            chat.spaces()
            .findDirectMessage(name=f"users/{user_email}")
            .execute()
        )
    except HttpError as e:
        api_response(e.status_code, str(e)[:300])
        raise RuntimeError(
            f"No hay DM con {user_email}. El usuario debe abrir chat.google.com, "
            f"buscar el bot '{BOT_NAME}' y enviarle al menos un mensaje primero."
        ) from e
    space_name = space["name"]
    api_response(200, space_name)
    cache[user_email] = space_name
    _save_cache(cache)
    return space_name


@app.command(name="list-spaces")
def cmd_list_spaces() -> None:
    """Lista todos los spaces donde el bot está añadido."""
    step("Listando spaces del bot")
    chat = _client()
    res = chat.spaces().list(pageSize=100).execute()
    spaces = res.get("spaces", [])
    if not spaces:
        info("(sin spaces — ningún usuario ha iniciado conversación con el bot aún)")
        return
    for s in spaces:
        print(f"  - {s['name']:60s} type={s.get('spaceType','?')} display={s.get('displayName','(DM)')}")
    ok(f"{len(spaces)} spaces")


def _send_message(user_email: str, text: str) -> str:
    space_name = _resolve_space_for_user(user_email)
    chat = _client()
    msg = {"text": f"[{BOT_NAME}] {text}"}
    api_call("POST", f"{space_name}/messages")
    res = chat.spaces().messages().create(parent=space_name, body=msg).execute()
    api_response(200, res.get("name", ""))
    return res["name"]


@app.command()
def send(user_email: str, text: str) -> None:
    """Envía mensaje 1:1 a `user_email`. Texto se prefija con el nombre del bot."""
    step(f"Enviando mensaje a {user_email}")
    name = _send_message(user_email, text)
    ok(f"Mensaje enviado: {name}")


if __name__ == "__main__":
    app()
