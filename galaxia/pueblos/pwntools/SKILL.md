---
cosmos: pueblo
nombre: pwntools
padre: ciberseguridad/ofensiva/codigo-ofensivo
resumen: Empaqueta procesos, sockets y shellcode para escribir el exploit sin andamiaje.
---

https://github.com/Gallopsled/pwntools · MIT en su mayor parte, con piezas GPL y BSD-2 (leído en `LICENSE-pwntools.txt`; la API de GitHub la reporta como `NOASSERTION`) · 13.669★ · último push 2026-08-30 (comprobado 2026-09-01)

```bash
pipx install pwntools
```

```python
# el esqueleto de un exploit de reto: local ahora, remoto cambiando una línea
from pwn import *

context.update(arch="amd64", os="linux")

io = process("./reto")                 # en el reto real: remote("HOST-EJEMPLO", 31337)
io.recvuntil(b"nombre: ")

carga = b"A" * 40 + p64(0xdeadbeef)    # relleno + dirección de retorno de ejemplo
io.sendline(carga)

io.interactive()                        # entrega la shell obtenida
```

Es el estándar de la competición y del desarrollo de exploits: empaqueta interacción con
procesos y sockets, empaquetado de enteros, ROP y `shellcraft` para no reescribir el andamiaje en
cada reto. Complemento citado y no admitido como pueblo aparte: `JonathanSalwan/ROPgadget`
(4.472★), que resuelve **un paso** —buscar los fragmentos de retorno— y no el oficio entero.

Ojo: la licencia es mixta a propósito. La mayor parte es MIT, pero hay ficheros bajo GPL y BSD-2 con
su cabecera propia — para redistribuir un derivado hay que mirar fichero a fichero, no asumir MIT
para todo. Y el marcador `0xdeadbeef` del ejemplo es literalmente un marcador: una dirección real se
saca de cada binario concreto en cada ejecución (el espacio de direcciones cambia), nunca se copia
de un exploit ajeno.

Contexto de uso legítimo: CTF, formación y desarrollo de exploits contra objetivos propios o dentro
del alcance de un encargo autorizado.
