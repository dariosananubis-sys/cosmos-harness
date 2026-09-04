---
cosmos: pueblo
nombre: codigo-al-modelo
padre: agentes-ia/coste
resumen: Dar codigo a un modelo: el fragmento que pide la intencion, o el repositorio entero si no puede abrir ficheros.
origen: propio
---

`scripts/semble-doctor.sh` y `scripts/repomix-pack.sh` — herramientas propias, no de GitHub.

```bash
chmod +x scripts/semble-doctor.sh scripts/repomix-pack.sh
scripts/semble-doctor.sh --warm ./src ./tools     # instala semble y pre-indexa
semble search "flujo de autenticacion" ./src --top-k 5 --max-snippet-lines 10
scripts/repomix-pack.sh ./src/mi-proyecto         # -> repomix-output.md, para el otro caso
```

La regla de elección es una y no otra: **si el que lee puede abrir ficheros, fragmento; si no puede,
paquete.** `semble` localiza por intención y devuelve solo el trozo con su fichero y su línea; medido
en un caso real, el mismo lookup cuesta unas cuarenta veces menos que leer el fichero entero.

Lo importante de `semble-doctor.sh` no es instalar, es la segunda mitad: **borra su servidor MCP de la
configuración si alguien lo coló**. Ese servidor se paga en cada sesión aunque no se invoque, así que
la garantía tiene que ser un mecanismo idempotente y no una nota. También pre-calienta el índice,
porque el minuto largo de la primera búsqueda es lo que hace que la gente vuelva al grep a ciegas.

`repomix-pack.sh` gana solo cuando el lector **no puede abrir ficheros** (una consola ajena, otro
proveedor, una revisión fuera de la máquina): respeta `.gitignore` y escanea secretos antes de
escribir. Dentro de una sesión con acceso al disco es la forma más cara posible de mirar código.

Ojo: `semble` NO sustituye a `grep`. Para TODAS las ocurrencias literales de una cadena —los llamantes
de una función que se renombra— la búsqueda semántica se deja alguna, y eso rompe el refactor.
