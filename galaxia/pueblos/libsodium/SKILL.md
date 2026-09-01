---
cosmos: pueblo
nombre: libsodium
padre: ciberseguridad/defensiva/codigo-defensivo
resumen: Cripto de alto nivel que es dificil de usar mal: no se elige modo ni relleno.
---

https://github.com/jedisct1/libsodium · ISC (leído en su `LICENSE`; la API de GitHub la reporta como `NOASSERTION`) · 13.927★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
brew install libsodium
pip install pynacl        # el enlace de Python, el más usado
```

```python
# cifrado autenticado: la clave y el nonce los genera la librería, no tú
from nacl.secret import SecretBox
from nacl.utils import random

clave = random(SecretBox.KEY_SIZE)          # 32 bytes; se guarda en el gestor de secretos
caja = SecretBox(clave)

cifrado = caja.encrypt(b"MENSAJE-DE-EJEMPLO")   # nonce incluido dentro
assert caja.decrypt(cifrado) == b"MENSAJE-DE-EJEMPLO"
```

Entra como pueblo aunque sea biblioteca: es la decisión de diseño, no un consejo. Gana a OpenSSL
para código de aplicación porque **no ofrece las decisiones que rompen**: no se elige modo de
cifrado, ni relleno, ni se reutiliza un nonce por descuido, y el cifrado va siempre autenticado.
OpenSSL sigue siendo lo correcto cuando hace falta TLS o un formato heredado concreto.

Ojo: no resuelve la parte difícil, que es **dónde vive la clave**. Una clave en una variable de
entorno de un contenedor público sigue siendo una clave filtrada por muy bien cifrado que esté el
mensaje — eso vive en el agua de custodia y en `infraestructura/sops`. Y el enlace de Python
(`PyNaCl`) va por detrás de las novedades del núcleo en C: para primitivas recientes hay que mirar
si el enlace ya las expone antes de prometerlas.
