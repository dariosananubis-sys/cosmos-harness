---
cosmos: lluvia
nombre: bascula-rota
moja: []
resumen: Como se diagnostica en minutos un juez de acierto que sube sin que el arbol mejore, y que lo cierra.
---

# La báscula rota: cómo saber si la cifra de acierto es honesta

**Fecha:** 2026-09-03 · **Origen:** auditoría 360, informe B (`progress/auditoria-360-2026-09-03/B-juez.md`)
· **Cerrado en:** `CICLO-1/FIX.md`, spec `NUCLEO.md` §11.

## Síntoma

La contra-métrica (`cosmos acertar`) publicaba «la cifra que vale es 40 %» con todas las puertas
en verde. Reescribiendo los veinte resúmenes del holdout con las palabras literales de cada consulta
—sin añadir una herramienta ni corregir un resumen malo— la validación subía a **100 %**, `validar`
seguía verde, `medir` daba 204 tokens MÁS barato y `--minimo 95` salía 0. Un control independiente
sobre el mismo árbol inflado daba 30 %: el árbol estaba peor y todos los números mejor.

## Causa raíz (y qué NO era)

- El examen viajaba en claro dentro del repositorio (`pruebas/encargos-validacion.json`): quien
  clonaba tenía el holdout. El sello solo impedía ver el `--detalle`, no leer el fichero.
- La guarda anti-Goodhart miraba al lado equivocado: `brecha = ajuste − validación` alarmaba con
  brecha ≥ 10 y **felicitaba** con brecha ≤ −5, que es la firma exacta del examen filtrado.
- Con el sello roto la salida decía «no publicable» y cuatro líneas después «la cifra que vale».
- El criterio de corrección (`_acierta`) no tenía ninguna prueba: aflojarlo subía 5 puntos con
  259 tests en verde.
- **No era** un problema de calibración del medidor (verificada: ±2 % en los tres factores), ni
  del techo de 4.000 (nunca se movió), ni de la batería de mutación (59/59 reales).

## Cómo diagnosticarlo RÁPIDO la próxima vez

```bash
cd ~/cosmos
git ls-files pruebas | grep -c validacion.json          # tiene que ser 0: el examen no se versiona
python3 -m cosmos acertar | grep -E "Historia git|NO es publicable|La cifra que vale"
python3 -m cosmos acertar --minimo 1 >/dev/null 2>&1; echo $?   # 1 si la cifra no es publicable
python3 -m puente.tests.mutaciones | grep -E "M6[0-7]|M7[23]"   # las puertas del juez, vistas fallar
```

Si «La cifra que vale» aparece con una brecha muy negativa, o el holdout está en `git ls-files`, o
alguna de esas mutaciones sale VERDE: la báscula vuelve a estar rota.

## Fix (resumen)

Holdout fuera del repositorio (`~/.cosmos/holdout/`, solo su `.SELLO` se versiona, con procedencia
declarada); comprobación contra la historia git de que ninguna consulta estuvo nunca en el repo;
brecha ≤ −15 = alarma y no publicable; sello roto o ausente = no publicable; `--minimo` sale 1 en
todos esos estados; la cifra siempre con `n` e intervalo de Wilson; el juez puntúa la línea literal
que renderiza el catálogo; canario P01 en el gate contra resúmenes vaciados. Con la báscula honesta,
la nota de hoy es DESCONOCIDA (el único holdout está quemado por historia) — y eso es un resultado.
