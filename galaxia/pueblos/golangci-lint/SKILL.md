---
cosmos: pueblo
nombre: golangci-lint
padre: refactorizacion/reglas
resumen: Corre un centenar de analizadores de Go compartiendo un solo parseo, y cachea: por eso cabe en cada commit.
---

https://github.com/golangci/golangci-lint · GPL-3.0 · 19.342★ · push 2026-09-01 (comprobado 2026-09-01, v2.13.2)

```bash
brew install golangci-lint
# o: go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@latest   (ojo al /v2)

golangci-lint run ./...
golangci-lint run --new-from-merge-base=origin/main ./...   # solo lo que introduce esta rama
golangci-lint fmt ./...                                     # formateadores, misma herramienta
golangci-lint migrate                                       # convierte una configuracion v1 a v2
```

Lo que aporta no son los analizadores —son de terceros y se podrian correr sueltos— sino que los corre
**una sola vez sobre el mismo arbol y la misma informacion de tipos**. Cargar y comprobar los tipos de
un paquete es la parte cara; hacerlo una vez y repartir el resultado entre cien analizadores es lo que
convierte una comprobacion de minutos en una de segundos, y ademas guarda el resultado en cache entre
ejecuciones. Correr `staticcheck`, `errcheck`, `govet` e `ineffassign` por separado paga ese coste
cuatro veces.

`--new-from-merge-base` es la razon por la que se puede meter en un repositorio que nunca paso un
analizador: denuncia solo lo que introduce la rama, sin obligar a arreglar diez anos de historia antes
de poder usarlo.

Ojo: el conjunto activado por defecto es **corto** a proposito. Activar todo produce miles de avisos
—duplicados entre analizadores que se solapan, quejas de estilo y falsos positivos de los mas
agresivos— y el resultado practico es que se desactiva entero; se empieza por el conjunto por defecto
y se anade de uno en uno. La version 2 cambio el formato de configuracion y una `.golangci.yml` de la
version 1 no vale: para eso esta `migrate`, y la ruta del modulo lleva `/v2`, que es el fallo tipico al
instalarlo con `go install`. Y la licencia es **GPL-3.0**, no permisiva como la del resto de este
continente: correr la herramienta sobre codigo propio no afecta a ese codigo, pero redistribuir el
binario dentro de un producto cerrado si tiene consecuencias, y conviene mirarlo antes de empaquetarlo
en una imagen que se entrega a un cliente.
