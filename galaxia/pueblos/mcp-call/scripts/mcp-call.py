#!/usr/bin/env python3
"""Llama a una tool de un servidor MCP que hable JSON-RPC por STDIN/STDOUT (un
bridge stdio), sin dejar una conexión persistente abierta.

  mcp-call.py <tool> '<json-args>'
  mcp-call.py --list
  mcp-call.py --schema <tool1>,<tool2>

Manda `initialize` + la llamada por STDIN al comando definido en la variable de
entorno MCP_BRIDGE_CMD (o edítalo directamente en BRIDGE_CMD más abajo), y parsea
la respuesta JSON-RPC de la salida estándar. El stderr del bridge se descarta (si se
mezcla con stdout rompe el parseo del JSON).

Ejemplo de BRIDGE_CMD: un wrapper que arranca tu servidor MCP y lo deja hablando por
stdio, p.ej. `npx -y @tuservidor/mcp-bridge --config <ruta>`.
"""
import json
import os
import shlex
import subprocess
import sys

BRIDGE_CMD = os.environ.get("MCP_BRIDGE_CMD", "")


def rpc(mensajes):
    if not BRIDGE_CMD:
        sys.exit("Falta MCP_BRIDGE_CMD (comando que arranca el servidor MCP por stdio).")
    entrada = "".join(json.dumps(m) + "\n" for m in mensajes)
    p = subprocess.run(
        shlex.split(BRIDGE_CMD),
        input=entrada, capture_output=True, text=True, timeout=300,
    )
    dec = json.JSONDecoder()
    data, i, objs = p.stdout, 0, []
    while i < len(data):
        if data[i] in " \n\r\t":
            i += 1
            continue
        if data[i] != "{":
            j = data.find("\n", i)
            i = j + 1 if j >= 0 else len(data)
            continue
        try:
            o, end = dec.raw_decode(data, i)
        except json.JSONDecodeError:
            i += 1
            continue
        objs.append(o)
        i = end
    if not objs:
        sys.stderr.write(p.stderr[-2000:])
    return objs


def main():
    init = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "mcp-call", "version": "1"}}}
    if sys.argv[1] == "--list":
        objs = rpc([init, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}])
        for o in objs:
            if o.get("id") == 2:
                for t in o["result"]["tools"]:
                    print(t["name"])
        return
    if sys.argv[1] == "--schema":
        objs = rpc([init, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}])
        buscados = sys.argv[2].split(",")
        for o in objs:
            if o.get("id") == 2:
                for t in o["result"]["tools"]:
                    if t["name"] in buscados:
                        print(json.dumps(t, indent=1)[:6000])
        return
    tool = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    objs = rpc([init, {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                       "params": {"name": tool, "arguments": args}}])
    for o in objs:
        if o.get("id") == 2:
            print(json.dumps(o.get("result", o), ensure_ascii=False))


if __name__ == "__main__":
    main()
