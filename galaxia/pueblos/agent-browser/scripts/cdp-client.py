#!/usr/bin/env python3
"""Cliente CDP mínimo por WebSocket (stdlib) para mover cookies entre navegadores.

  cdp.py dump <puerto> <fichero.json>     # Storage.getCookies del navegador entero
  cdp.py load <puerto> <fichero.json>     # Storage.setCookies en el navegador destino
"""
import base64, json, os, socket, struct, sys, urllib.request


def ws_connect(url):
    assert url.startswith("ws://")
    resto = url[5:]
    hostport, path = resto.split("/", 1)
    path = "/" + path
    host, port = hostport.split(":")
    s = socket.create_connection((host, int(port)), timeout=20)
    key = base64.b64encode(os.urandom(16)).decode()
    req = (f"GET {path} HTTP/1.1\r\nHost: {hostport}\r\nUpgrade: websocket\r\n"
           f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
    s.sendall(req.encode())
    buf = b""
    while b"\r\n\r\n" not in buf:
        buf += s.recv(4096)
    return s


def ws_send(s, texto):
    datos = texto.encode()
    mask = os.urandom(4)
    n = len(datos)
    cab = b"\x81"
    if n < 126:
        cab += struct.pack("!B", n | 0x80)
    elif n < 65536:
        cab += struct.pack("!BH", 126 | 0x80, n)
    else:
        cab += struct.pack("!BQ", 127 | 0x80, n)
    enmascarado = bytes(b ^ mask[i % 4] for i, b in enumerate(datos))
    s.sendall(cab + mask + enmascarado)


def _leer(s, n):
    out = b""
    while len(out) < n:
        trozo = s.recv(n - len(out))
        if not trozo:
            raise ConnectionError("el navegador cerró la conexión")
        out += trozo
    return out


def ws_recv(s):
    while True:
        cab = _leer(s, 2)
        opcode = cab[0] & 0x0F
        n = cab[1] & 0x7F
        if n == 126:
            n = struct.unpack("!H", _leer(s, 2))[0]
        elif n == 127:
            n = struct.unpack("!Q", _leer(s, 8))[0]
        payload = _leer(s, n)
        if opcode == 1:
            return payload.decode()
        if opcode == 8:
            raise ConnectionError("cerrado por el navegador")


def llamar(puerto, metodo, params=None):
    with urllib.request.urlopen(f"http://127.0.0.1:{puerto}/json/version", timeout=10) as r:
        url = json.load(r)["webSocketDebuggerUrl"]
    s = ws_connect(url)
    ws_send(s, json.dumps({"id": 1, "method": metodo, "params": params or {}}))
    while True:
        msg = json.loads(ws_recv(s))
        if msg.get("id") == 1:
            s.close()
            return msg


CAMPOS = ("name", "value", "domain", "path", "secure", "httpOnly", "sameSite", "expires")

if __name__ == "__main__":
    accion, puerto, fichero = sys.argv[1], sys.argv[2], sys.argv[3]
    if accion == "dump":
        resp = llamar(puerto, "Storage.getCookies")
        cookies = resp.get("result", {}).get("cookies", [])
        json.dump(cookies, open(fichero, "w"))
        print(len(cookies))
    else:
        cookies = json.load(open(fichero))
        limpias = []
        for c in cookies:
            d = {k: c[k] for k in CAMPOS if k in c and c[k] is not None}
            if d.get("sameSite") not in ("Strict", "Lax", "None"):
                d.pop("sameSite", None)
            if d.get("expires", 0) in (-1, 0):
                d.pop("expires", None)
            limpias.append(d)
        resp = llamar(puerto, "Storage.setCookies", {"cookies": limpias})
        print("error" if resp.get("error") else f"puestas {len(limpias)}")
        if resp.get("error"):
            print(json.dumps(resp["error"])[:300])
