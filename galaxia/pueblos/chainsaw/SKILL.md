---
cosmos: pueblo
nombre: chainsaw
padre: ciberseguridad/analisis/forense
resumen: Busca sobre los registros de eventos de Windows con reglas de deteccion ya escritas.
---

https://github.com/WithSecureLabs/chainsaw · GPL-3.0 · 3.652★ · último push 2026-08-25 (comprobado 2026-09-01)

```bash
brew install chainsaw
git clone --depth 1 https://github.com/SigmaHQ/sigma.git   # el corpus de reglas
```

```bash
# caza con reglas Sigma sobre los EVTX recogidos de una máquina
chainsaw hunt ./evtx_recogidos/ \
  --sigma sigma/rules/windows/ \
  --mapping mappings/sigma-event-logs-all.yml \
  --csv --output ./hallazgos/

# búsqueda cruda por cadena o por identificador de evento, sin reglas
chainsaw search ./evtx_recogidos/ -e 4625 -t 'Event.System.Computer: =EQUIPO-EJEMPLO'
```

Es el puente entre los dos continentes: la misma regla Sigma que vigila en vivo sirve para buscar
hacia atrás en el disco de una máquina ya comprometida. Gana a `Neo23x0/Loki` (3.786★, último push
2026-01-12) para este hueco porque Loki escanea ficheros por indicadores y reglas YARA, y aquí lo
que se lee es la **línea temporal de eventos**, que es otra pregunta.

Ojo: sin el fichero de `--mapping` correcto para el corpus que uses, las reglas casan contra campos
que no existen y el resultado es **cero hallazgos sin ningún error** — el falso verde más caro de
esta herramienta. Y solo habla EVTX: para artefactos de disco (MFT, prefetch, papelera) hace falta
otra pieza. En un caso real, trabajar siempre sobre copia de los registros, nunca sobre el original.
