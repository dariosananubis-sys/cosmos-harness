#!/usr/bin/env python3
"""Envía un correo por SMTP directo usando un buzón propio (cualquier proveedor con SMTP/IMAP,
o Gmail con app-password).

Pensado como canal por defecto para mandar documentación sin abrir un cliente de correo ni
tocar el navegador. Usa otro canal (chat, etc.) solo cuando se pida expresamente.

Credenciales: ~/.secrets/mail-cuenta.env  (MAIL_EMAIL, MAIL_PASSWORD, MAIL_SMTP_HOST,
MAIL_SMTP_PORT, MAIL_SMTP_ENC, MAIL_IMAP_*). Nunca se imprimen.

Uso:
  python3 scripts/enviar-correo-smtp.py --to ejemplo@dominio.com \
      --asunto "..." --cuerpo-fichero cuerpo.txt --adjunto "/ruta/adjunto.zip"
  (--cc admite varios separados por coma; --cuerpo acepta el texto directo)

Tras enviar, sube una copia a la carpeta de Enviados por IMAP para que quede en el buzón.
"""
import argparse, mimetypes, os, smtplib, ssl, sys, imaplib, time
from email.message import EmailMessage
from pathlib import Path

ENV = Path.home() / ".secrets/mail-cuenta.env"


def cargar_env():
    if not ENV.exists():
        sys.exit(f"no existe {ENV}")
    datos = {}
    for linea in ENV.read_text().splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        k, v = linea.split("=", 1)
        datos[k.strip()] = v.strip().strip('"').strip("'")
    return datos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True)
    ap.add_argument("--cc", default="")
    ap.add_argument("--asunto", required=True)
    ap.add_argument("--cuerpo", default="")
    ap.add_argument("--cuerpo-fichero", default="")
    ap.add_argument("--adjunto", action="append", default=[])
    ap.add_argument("--dry-run", action="store_true", help="prepara el mensaje y NO lo envía")
    a = ap.parse_args()

    env = cargar_env()
    remitente = env.get("MAIL_EMAIL")
    clave = env.get("MAIL_PASSWORD")
    host = env.get("MAIL_SMTP_HOST")
    puerto = int(env.get("MAIL_SMTP_PORT", 465))
    enc = (env.get("MAIL_SMTP_ENC") or "ssl").lower()
    if not remitente or not clave or not host:
        sys.exit("faltan MAIL_EMAIL / MAIL_PASSWORD / MAIL_SMTP_HOST en el .env")

    cuerpo = Path(a.cuerpo_fichero).read_text() if a.cuerpo_fichero else a.cuerpo
    if not cuerpo.strip():
        sys.exit("cuerpo vacío")

    msg = EmailMessage()
    msg["From"] = remitente
    msg["To"] = a.to
    if a.cc:
        msg["Cc"] = a.cc
    msg["Subject"] = a.asunto
    msg.set_content(cuerpo)

    for ruta in a.adjunto:
        p = Path(ruta)
        if not p.exists():
            sys.exit(f"no existe el adjunto {p}")
        tipo, _ = mimetypes.guess_type(p.name)
        maintype, subtype = (tipo.split("/", 1) if tipo else ("application", "octet-stream"))
        msg.add_attachment(p.read_bytes(), maintype=maintype, subtype=subtype, filename=p.name)
        print(f"adjunto: {p.name} ({p.stat().st_size/1_048_576:.1f} MB)")

    destinos = [x.strip() for x in (a.to + ("," + a.cc if a.cc else "")).split(",") if x.strip()]
    print(f"de {remitente} -> {destinos} | asunto: {a.asunto}")
    if a.dry_run:
        print("dry-run: no se envía")
        return

    ctx = ssl.create_default_context()
    if enc in ("ssl", "tls-implicit", "ssl/tls"):
        with smtplib.SMTP_SSL(host, puerto, context=ctx, timeout=120) as s:
            s.login(remitente, clave)
            s.send_message(msg, from_addr=remitente, to_addrs=destinos)
    else:
        with smtplib.SMTP(host, puerto, timeout=120) as s:
            s.starttls(context=ctx)
            s.login(remitente, clave)
            s.send_message(msg, from_addr=remitente, to_addrs=destinos)
    print("ENVIADO OK")

    # Copia en Enviados (muchos proveedores no la guardan solos al enviar por SMTP)
    ihost = env.get("MAIL_IMAP_HOST")
    if not ihost:
        print("aviso: no se pudo guardar copia en Enviados (falta MAIL_IMAP_HOST)")
        return
    try:
        with imaplib.IMAP4_SSL(ihost, int(env.get("MAIL_IMAP_PORT", 993))) as m:
            m.login(remitente, clave)
            carpetas = [c.decode() for c in m.list()[1]]
            destino = next((c.split(' "/" ')[-1].strip('"') for c in carpetas
                            if "Sent" in c or "Enviados" in c), "INBOX.Sent")
            m.append(f'"{destino}"', "\\Seen", imaplib.Time2Internaldate(time.time()), msg.as_bytes())
            print(f"copia guardada en {destino}")
    except Exception as e:
        print(f"aviso: no se pudo guardar copia en Enviados ({e})")


if __name__ == "__main__":
    main()
