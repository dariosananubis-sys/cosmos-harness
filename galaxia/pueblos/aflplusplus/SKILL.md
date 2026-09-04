---
cosmos: pueblo
nombre: aflplusplus
padre: ciberseguridad/ofensiva/codigo-ofensivo
resumen: Muta entradas guiado por cobertura y encuentra el dato que revienta un analizador.
---

https://github.com/AFLplusplus/AFLplusplus · AGPL-3.0 · 6.741★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
brew install afl++
```

```bash
# compilar el objetivo con la instrumentación de cobertura
afl-clang-fast -o objetivo objetivo.c

# fuzzing guiado por cobertura: casos semilla en 'entradas', hallazgos en 'salidas'
mkdir -p entradas salidas && printf 'MARCADOR' > entradas/semilla
afl-fuzz -i entradas -o salidas -- ./objetivo @@

# cada fichero de 'salidas/default/crashes' es una entrada que hizo caer al objetivo
```

Gana al fuzzer equivalente `google/honggfuzz` (3.376★) por comunidad e integraciones listas, y a
`libFuzzer` porque este vive dentro de LLVM y no tiene repositorio propio que auditar. Muta las
entradas guiándose por qué ramas nuevas del código alcanza, así que encuentra el dato exacto que
revienta un analizador sin que nadie tenga que imaginarlo.

Ojo, dos cosas. La **licencia es AGPL-3.0 con copyleft de red**: para auditoría y pentest no estorba
(no se redistribuye como servicio), pero si algún día se empaqueta como servicio en línea hay que
releerla. Y el fuzzing **no termina solo**: un fuzzer que corrió una hora sin caídas no dice que el
objetivo sea seguro, dice que esa hora y ese conjunto de semillas no encontraron nada — el valor
está en la cobertura alcanzada (`afl-whatsup`) y en las semillas de partida, no en el reloj.

Contexto de uso legítimo: fuzzing de código propio o entregado en un encargo, investigación y CTF.

Ojo, doble uso declarado: un fuzzer se usa para encontrar fallos en código **propio o con permiso
escrito**, en auditoría contratada o laboratorio, nunca contra un objetivo fuera del alcance acordado.
