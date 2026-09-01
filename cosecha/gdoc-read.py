#!/usr/bin/env python3
"""Lee un Google Doc vía Service Account, usando Drive export (no requiere la Docs
API habilitada, solo Drive API con scope readonly).

Uso: python3 gdoc-read.py <doc_id_o_url> [--urls-only]

Requiere:
  - Una cuenta de servicio de Google Cloud con la Drive API habilitada.
  - El fichero JSON de credenciales de esa cuenta de servicio, apuntado por la
    variable de entorno GOOGLE_SA_KEY_PATH (o pasado con --key <ruta>).
  - Que el Doc esté compartido (Viewer) con el email de esa cuenta de servicio
    (client_email dentro del JSON).
"""
import argparse
import os
import re
import sys
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
URL_RE = re.compile(r"https?://[^\s)>\]]+")


def doc_id(arg: str) -> str:
    m = re.search(r"/document/d/([a-zA-Z0-9_-]+)", arg)
    return m.group(1) if m else arg.strip()


def key_path(cli_key: str | None) -> Path:
    raw = cli_key or os.environ.get("GOOGLE_SA_KEY_PATH")
    if not raw:
        sys.exit(
            "Falta la ruta a la clave de la cuenta de servicio.\n"
            "Pásala con --key <ruta.json> o exporta GOOGLE_SA_KEY_PATH=<ruta.json>."
        )
    p = Path(raw).expanduser()
    if not p.exists():
        sys.exit(f"No existe el fichero de clave: {p}")
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("doc")
    ap.add_argument("--urls-only", action="store_true")
    ap.add_argument("--key", help="ruta al JSON de la cuenta de servicio (o usa GOOGLE_SA_KEY_PATH)")
    args = ap.parse_args()

    did = doc_id(args.doc)
    key = key_path(args.key)
    creds = service_account.Credentials.from_service_account_file(str(key), scopes=SCOPES)
    drive = build("drive", "v3", credentials=creds)
    meta = drive.files().get(fileId=did, fields="name").execute()
    data = drive.files().export(fileId=did, mimeType="text/plain").execute()
    text = data.decode("utf-8", "ignore") if isinstance(data, bytes) else str(data)

    links = list(dict.fromkeys(URL_RE.findall(text)))  # únicos, orden de aparición
    print(f"# {meta.get('name','(sin título)')}  [{did}]")
    print(f"# URLs encontradas: {len(links)}\n")
    for u in links:
        print(u)
    if not args.urls_only:
        print("\n===== TEXTO COMPLETO =====\n")
        print(text)


if __name__ == "__main__":
    main()
