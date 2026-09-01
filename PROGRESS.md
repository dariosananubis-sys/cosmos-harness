# Progreso de COSMOS

Actualizado: 2026-09-01, ronda Codex posterior al corte por disco lleno.

## Estado real

### Terminado en esta ronda

- `cosmos/validar.py`: E00 (sintaxis/esquema) y E01–E18. E17 compara shingles de cuatro
  palabras mediante Jaccard solo entre galaxia, océanos y estrellas que iluminan la galaxia. E18
  exige unicidad global provisional entre ciudades/pueblos y nombra ambas rutas en conflicto.
- `cosmos/cli.py` y `cosmos/__main__.py`: subcomandos `validar`, `medir`, `generar` y `mapa`, con
  configuración TOML, salidas humanas y JSON donde corresponde.
- `cosmos.toml`: presupuestos normativos y `guardarrailes.umbral_solapamiento = 0.25`.
- `ejemplo/`: árbol genérico verde con una galaxia, dos sistemas solares, dos planetas, una
  provincia, dos pueblos, una estrella, una luna, dos océanos, un mar, un lago, un río y una
  lluvia. `ejemplo/COSMOS.md` está generado y sincronizado.
- `tests/`: un rojo por E00–E18, verde del ejemplo, control negativo de E17, cuatro pruebas del
  medidor, cuatro pruebas CLI y meta-prueba mutante.
- `reviews/codex-revisa-specs.md`: revisión adversarial completa de `GOAL.md` y `spec/*.md`.

### Pendiente para la ronda siguiente

- E19 y `cosmos compilar` no se implementaron en esta ronda, tal como permitía el encargo.
- Antes de implementarlos hay que resolver o fijar explícitamente las dos ambigüedades bloqueantes
  encontradas en la revisión: qué nodos/directorios se aplanan y cómo puede `compilar` reparar E19
  si la regla actual le obliga a abortar ante cualquier rojo.
- Los enganches, saltos caducables y comandos `enganchar`/`desenganchar` de `GUARDARRAILES.md`
  tampoco formaban parte de la implementación solicitada en esta ronda; solo E17.

## Evidencia roja

La meta-prueba sustituyó el conjunto completo de comprobaciones por una tupla vacía, equivalente a
un validador que siempre dice “bien”, y volvió a ejecutar los 19 tests E00–E18. Resultado literal:

```text
MUTANTE siempre-verde: Ran 19 tests; failures=19; errors=0
```

Por tanto, vaciar el validador pone roja la batería; no puede sobrevivir como validador decorativo.

## Evidencia verde final

Comando ejecutado desde `/Users/<usuario>/cosmos`:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Resumen literal de la ejecución final:

```text
----------------------------------------------------------------------
Ran 30 tests in 0.095s

OK (skipped=1)
```

El único salto fue explícito:

```text
tokenizador exacto local no disponible; comparación declaradamente omitida
```

No se instaló `tiktoken` ni ninguna dependencia. Las otras 29 pruebas pasaron.

## Comprobación funcional del ejemplo

```text
COSMOS  verde  0 errores
```

Medición aproximada declarada del ejemplo:

```text
Entrada ......... 276 tokens   (estimado, ±desconocido, heurística v1)
Árbol ........... 695 tokens   (estimado, ±desconocido, heurística v1)
Descarga ........ 60,3 %
Fuera de COSMOS . no_medido
```

## Disco

Al comenzar quedaban aproximadamente 239 MiB; durante la ronda el sistema liberó espacio y la
última lectura mostró aproximadamente 2,4 GiB disponibles. No se produjo otro `No space left on
device`. No se creó entorno virtual, log voluminoso ni caché persistente; el `__pycache__` pequeño
generado por una comprobación inicial fue retirado.
