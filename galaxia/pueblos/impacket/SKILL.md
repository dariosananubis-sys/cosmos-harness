---
cosmos: pueblo
nombre: impacket
padre: ciberseguridad/ofensiva/post-explotacion
resumen: Habla SMB, Kerberos y LDAP desde Python para auditar un dominio de Windows.
---

https://github.com/fortra/impacket · licencia propia basada en Apache 1.1, permisiva con cláusula de atribución (leído en `LICENSE`; la API de GitHub la reporta como `NOASSERTION`) · 16.055★ · último push 2026-08-28 (comprobado 2026-09-01)

```bash
pipx install impacket
```

```bash
# comprobar credenciales del alcance contra un recurso compartido
smbclient.py 'DOMINIO-EJEMPLO/usuario:contrasena@HOST-DEL-ALCANCE'

# pedir tickets de servicio para auditar contraseñas débiles (Kerberoasting)
GetUserSPNs.py -request 'DOMINIO-EJEMPLO/usuario:contrasena' -dc-ip 198.51.100.10
```

Es la **base sobre la que están escritas** casi todas las herramientas del hueco: habla SMB, MSRPC,
Kerberos y LDAP desde Python, y trae de serie `secretsdump.py`, `psexec.py`, `GetUserSPNs.py`. Por
eso entra la base y no cada envoltorio que la reimporta (NetExec y compañía). Complemento de
`bloodhound`: aquel dibuja el camino, este da las piezas para recorrerlo.

Ojo, descartado a propósito el extractor de credenciales en memoria más conocido (Mimikatz): su
volcado ya está cubierto por `secretsdump.py` de aquí y es el que más fácil se sale del uso legítimo.
Doble uso declarado: solo en auditoría de un dominio del alcance, laboratorio y CTF. Y en lo técnico,
`secretsdump` y `psexec` **dejan rastro y disparan EDR** — no son sigilosos, así que un encargo que
mida detección los usará esperando que salten.
