---
cosmos: pueblo
nombre: trufflehog
padre: ciberseguridad/analisis/vulnerabilidades
resumen: Encuentra credenciales en el historico y ademas intenta usarlas para saber si siguen vivas.
---

https://github.com/trufflesecurity/trufflehog · AGPL-3.0 · 27.647★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
brew install trufflehog
```

```bash
# todo el histórico de un repositorio local, solo lo confirmado vivo
trufflehog git file://. --only-verified

# el árbol de trabajo, sin recorrer el histórico
trufflehog filesystem . --only-verified --json

# como puerta antes de commitear
trufflehog git file://. --since-commit HEAD --only-verified --fail
```

El único de su hueco que **verifica de verdad**: para cada secreto detectado intenta autenticarse
contra el proveedor y dice si sigue activo. Eso convierte una lista de sospechas en una lista de
trabajo. Gana a `gitleaks/gitleaks` (29.046★, más adoptado) por dos motivos medidos: gitleaks
detecta por expresión regular y entropía sin verificar, y su propio README declara desde 2026 que
**está terminado y solo recibirá parches de seguridad**, con el desarrollo movido a otro repositorio.

Ojo, tres avisos. `--only-verified` **hace llamadas de red a los proveedores** con las credenciales
encontradas: es exactamente lo que lo hace útil, y también lo que puede disparar alertas en la
cuenta del cliente — se avisa antes de lanzarlo en un encargo. Sin `--only-verified` la salida
vuelve a ser una lista de sospechas larga. Y verificado significa **vivo**, no *explotable*: un
testigo de solo lectura y uno de administración salen igual de rojos, la prioridad la pones tú.
