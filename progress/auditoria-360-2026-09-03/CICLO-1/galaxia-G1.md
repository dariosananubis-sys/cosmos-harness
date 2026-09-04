# Galaxia G1 — informe (auditoría 360, ciclo 1)

Hallazgos trabajados: C-03 (ciberseguridad sin nmap), C-04 (infraestructura sin IaC), C-05
(rendimiento sin perfilador de memoria), C-10 (24 fichas eligen por las restricciones de una sola
máquina).

## Tabla — pueblos añadidos

| herramienta | padre | URL | último commit | estrellas | licencia | añadida/omitida y por qué |
|---|---|---|---|---|---|---|
| nmap | ciberseguridad/ofensiva/reconocimiento | github.com/nmap/nmap | 2026-09-02 | 13.512 | NPSL (Nmap Public Source License, LICENSE propio) | Añadida |
| ffuf | ciberseguridad/ofensiva/reconocimiento | github.com/ffuf/ffuf | 2026-08-20 | 16.629 | MIT | Añadida |
| hashcat | ciberseguridad/ofensiva/post-explotacion | github.com/hashcat/hashcat | 2026-09-03 | 26.695 | MIT (docs/license.txt; la API de GitHub no la detecta) | Añadida |
| wireshark | ciberseguridad/analisis/forense | github.com/wireshark/wireshark | 2026-09-03 | 9.815 | GPL-2.0 | Añadida |
| codeql | ciberseguridad/analisis/vulnerabilidades | github.com/github/codeql | 2026-09-02 | 10.045 | MIT (queries/librerías QL de este repo; el CLI del motor tiene términos de uso propios de GitHub) | Añadida |
| httpx | ciberseguridad/ofensiva/reconocimiento | github.com/projectdiscovery/httpx | 2026-09-01 | 10.347 | MIT | Añadida |
| subfinder | ciberseguridad/ofensiva/reconocimiento | github.com/projectdiscovery/subfinder | 2026-08-31 | 14.365 | MIT | Añadida |
| osquery | ciberseguridad/defensiva/deteccion | github.com/osquery/osquery | 2026-08-25 | 23.537 | Apache-2.0 o GPL-2.0 (dual, LICENSE-Apache-2.0 / LICENSE-GPL-2.0) | Añadida |
| ansible | infraestructura/despliegue | github.com/ansible/ansible | 2026-09-02 | 70.568 | GPL-3.0 | Añadida |
| opentofu | infraestructura/despliegue | github.com/opentofu/opentofu | 2026-09-02 | 30.025 | MPL-2.0 | Añadida |
| grafana | infraestructura/vigilancia | github.com/grafana/grafana | 2026-09-03 | 76.559 | AGPL-3.0 | Añadida |
| loki | infraestructura/vigilancia | github.com/grafana/loki | 2026-09-02 | 28.830 | AGPL-3.0 | Añadida |
| vector | infraestructura/vigilancia | github.com/vectordotdev/vector | 2026-09-02 | 22.509 | MPL-2.0 | Añadida |
| coolify | infraestructura/despliegue | github.com/coollabsio/coolify | 2026-09-02 | 61.334 | Apache-2.0 | Añadida |
| memray | rendimiento/perfilado | github.com/bloomberg/memray | 2026-09-01 | 15.212 | Apache-2.0 | Añadida |
| scalene | rendimiento/perfilado | github.com/plasma-umass/scalene | 2026-08-27 | 13.496 | Apache-2.0 | Añadida |
| async-profiler | rendimiento/perfilado | github.com/async-profiler/async-profiler | 2026-09-02 | 9.131 | Apache-2.0 | Añadida |

17 añadidas, 0 omitidas. Todas verificadas vivas (200, sin archivar, último commit ≥ 2026-08-20,
muy por encima del corte de 2026-03-01). Cero repetidas: `grep -rl` contra `galaxia/` no encontró
ninguno de los 17 slugs antes de crearlos.

## Presupuesto de ciberseguridad (el nicho más caro)

Tras cada pueblo de ciberseguridad se corrió `cosmos medir`. Nota: G2/G3 trabajaban a la vez sobre
otros nichos, así que "quedan" incluye también sus adiciones concurrentes al universo global (no
solo las mías) — la cifra tras cada mi propia adición, en orden:

nmap → 239 · ffuf → 330 · hashcat → 304 · wireshark → 276 · codeql → 249 (tras converger la
compilación) · httpx → 219 · subfinder → 192 · osquery → 163.

En ningún punto "quedan" bajó de 60 tokens, así que no hizo falta parar. Cifra final tras las 8
(y las adiciones concurrentes de otros nichos): **163 tokens libres**, ciberseguridad en 35
pueblos.

## Tarea 2 — 16 fichas con justificación atada a una sola máquina (C-10)

Se buscó con el grep indicado en cada uno de los 16 pueblos listados y se reescribió solo el
**cuerpo** (nunca el `resumen`) para que el criterio de elección sea del oficio, dejando el
requisito de hardware — cuando lo hay — como dato cuantificado en el aviso de máquina, no como
motivo de elección. Ninguna decisión se invirtió: los 16 pueblos se quedan tal cual estaban
posicionados en su padre.

| pueblo | qué tenía | qué se cambió |
|---|---|---|
| dask | Elegía sobre Ray "por una razón medible en esta máquina concreta" (reserva de RAM de Ray) | Reescrito a framing de arranque/cluster vs. escalado hacia abajo; el dato de RAM de Ray se movió al aviso de máquina existente |
| lancedb | "Es el mejor **para esta máquina**" tras comparar con qdrant/chroma por RAM | Reescrito a huella de recursos (embebido vs. servidor aparte) como criterio; el matiz de RAM quedó como nota en el Ojo |
| kokoro | Preámbulo de elección apoyado en "una máquina justa de memoria" | Reescrito a capacidad del oficio (sintesis local sin GPU); se mantiene el dato de 2-3 GB como hecho descriptivo |
| pixi | La comparación de velocidad contra conda pasaba por "una máquina justa de memoria" | Generalizada a "con memoria de sobra o sin ella" |
| ponder | La comparación de huella con graph-node pasaba por "una máquina justa de memoria con Docker" | Generalizada a "cualquier máquina modesta" |
| platformio | La elección incluía "en una máquina justa de memoria, cada IDE nativo aparte revienta el disco" | Frase retirada de la justificación; el punto de disco se fusionó con el aviso de `~/.platformio` ya existente |
| polars | El "gana a pandas" estaba anclado a "lo que decide en una máquina justa de memoria" | Reescrito a "datasets que no caben enteros en RAM" (criterio de tamaño de dato, no de máquina) |
| bevy, duckdb, esp-idf, zephyr, whisper-cpp, demucs, reprozip, cuentas-del-asistente, playwright | La frase ya vivía en el aviso/Ojo (no eran motivo de elección) | Solo se generalizó la redacción, quitando "esta máquina"/"máquina justa" por una cifra o condición ("con poca RAM libre", "sea cual sea la RAM", "necesita X GB") |

Caso aparte, **reprozip**: la frase original decía "en una máquina justa de memoria no se puede
empaquetar nada nativamente", pero la restricción real es de sistema operativo (`ptrace` solo en
Linux), no de RAM — se corrigió a la vez que se generalizaba, dejando "en macOS no se puede
empaquetar nada nativamente".

Ningún fichero de la lista citaba el coste en tokens de contexto (la excepción que no se toca).

## Verificación de la propia galaxia

`python3 -m cosmos validar`:
```
COSMOS  verde  0 errores
```

`python3 -m cosmos medir` (estado final):
```
COSMOS  medir

  Entrada base .... 1.234 tokens
  Peor nicho ...... 2.484 tokens   (ciberseguridad, 35 pueblos)
  Agua condicional  1.163 tokens
  Peor con agua ... 3.647 tokens
  Universo ........ 170.696 tokens
  Descarga ........ 98,5 %
  Presupuesto ..... 4.000     OK, quedan 163 tokens con el margen calibrado (+5,2 %) en el peor caso con agua (ciberseguridad)
```

Nota de proceso: al trabajar G1/G2/G3 a la vez sobre el mismo árbol sin commits intermedios,
`cosmos compilar`/`validar` entraron varias veces en carrera con pueblos de otros agentes a medio
escribir (E19 por nodos aún no compilados, y una vez un E07 de resumen largo en `pa11y`, ajeno a
mi lista, que se resolvió solo cuando su agente lo corrigió). Se resolvió reintentando
`compilar`+`validar` en bucle hasta converger en verde; no se tocó ningún fichero fuera de mi
lista.

## Ficheros tocados

Creados (17): `galaxia/pueblos/{nmap,ffuf,hashcat,wireshark,codeql,httpx,subfinder,osquery,ansible,opentofu,grafana,loki,vector,coolify,memray,scalene,async-profiler}/SKILL.md`.

Editados (16, solo cuerpo, `resumen` intacto): `galaxia/pueblos/{bevy,dask,duckdb,esp-idf,platformio,polars,zephyr,whisper-cpp,demucs,kokoro,lancedb,pixi,playwright,ponder,reprozip,cuentas-del-asistente}/SKILL.md`.

No se tocó `spec/`, `README.md`, `GOAL.md`, `cosmos/`, `puente/`, `tests/`, ni el `resumen` de
ningún pueblo. No se ejecutó `cosmos generar`. Sí se ejecutó `cosmos compilar` repetidamente (paso
indicado por el propio `cosmos validar` para sincronizar la vista plana tras crear pueblos).
