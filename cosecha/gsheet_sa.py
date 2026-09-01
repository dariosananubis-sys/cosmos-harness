#!/usr/bin/env python3
"""Acceso a Google Drive/Sheets vía Service Account SIN dependencias google-*.
Firma el JWT RS256 con openssl (presente en macOS/Linux) y usa la REST API con
urllib de la stdlib — nada que instalar.

Requiere la variable de entorno GOOGLE_SA_KEY_PATH apuntando al JSON de la cuenta
de servicio (o pásala con --key <ruta>).

Uso:
  gsheet_sa.py list                         -> lista spreadsheets accesibles por la SA
  gsheet_sa.py tabs <sheetId>               -> lista pestañas (gid+titulo)
  gsheet_sa.py csv  <sheetId> [<tabTitle>]  -> vuelca una pestaña como CSV
"""
import base64, json, os, subprocess, sys, tempfile, time, urllib.request, urllib.parse
from pathlib import Path

SCOPES = "https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/spreadsheets.readonly"


def key_path() -> Path:
    raw = os.environ.get("GOOGLE_SA_KEY_PATH")
    if "--key" in sys.argv:
        i = sys.argv.index("--key")
        raw = sys.argv[i + 1]
        del sys.argv[i:i + 2]
    if not raw:
        sys.exit(
            "Falta la clave de la cuenta de servicio. Exporta GOOGLE_SA_KEY_PATH=<ruta.json> "
            "o pásala con --key <ruta.json>."
        )
    p = Path(raw).expanduser()
    if not p.exists():
        sys.exit(f"No existe el fichero de clave: {p}")
    return p


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def access_token(key: Path):
    info = json.loads(key.read_text())
    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    claims = {
        "iss": info["client_email"], "scope": SCOPES,
        "aud": info["token_uri"], "iat": now, "exp": now + 3600,
    }
    signing_input = f"{b64u(json.dumps(header).encode())}.{b64u(json.dumps(claims).encode())}".encode()
    # firmar RS256 con openssl usando la private_key en fichero temporal 0600
    fd, kp = tempfile.mkstemp(); os.close(fd); os.chmod(kp, 0o600)
    try:
        Path(kp).write_text(info["private_key"])
        sig = subprocess.run(["openssl", "dgst", "-sha256", "-sign", kp],
                             input=signing_input, capture_output=True, check=True).stdout
    finally:
        os.remove(kp)
    assertion = signing_input.decode() + "." + b64u(sig)
    body = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": assertion}).encode()
    req = urllib.request.Request(info["token_uri"], data=body)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())["access_token"]


def api(url, tok):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def main():
    key = key_path()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    tok = access_token(key)

    if cmd == "list":
        q = urllib.parse.quote("mimeType='application/vnd.google-apps.spreadsheet' and trashed=false")
        url = ("https://www.googleapis.com/drive/v3/files?q=" + q +
               "&orderBy=" + urllib.parse.quote("modifiedTime desc") + "&pageSize=100"
               "&fields=" + urllib.parse.quote("files(id,name,modifiedTime,owners(emailAddress))"))
        files = api(url, tok).get("files", [])
        print(f"Spreadsheets accesibles por la SA: {len(files)}\n")
        for f in files:
            owner = (f.get("owners") or [{}])[0].get("emailAddress", "?")
            print(f"[{f.get('modifiedTime','')[:10]}] {f['name'][:60]:60} | {f['id']} | {owner}")

    elif cmd == "tabs":
        sid = sys.argv[2]
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{sid}?fields=properties.title,sheets.properties"
        d = api(url, tok)
        print("TITULO:", d.get("properties", {}).get("title"))
        for s in d.get("sheets", []):
            p = s["properties"]
            print(f"  gid={p['sheetId']:>12}  filas~{p.get('gridProperties',{}).get('rowCount','?'):>6}  {p['title']}")

    elif cmd == "csv":
        sid = sys.argv[2]
        tab = sys.argv[3] if len(sys.argv) > 3 else None
        rng = urllib.parse.quote(tab) if tab else "A1:Z2000"
        url = (f"https://sheets.googleapis.com/v4/spreadsheets/{sid}/values/{rng}"
               "?majorDimension=ROWS&valueRenderOption=FORMATTED_VALUE")
        rows = api(url, tok).get("values", [])
        for r in rows:
            print("\t".join(str(c) for c in r))

    else:
        sys.exit("cmd desconocido: " + cmd)


if __name__ == "__main__":
    main()
