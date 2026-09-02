# Cómo reproducir el arnés de sabotaje

`sabotear.py` corre cada mutación sobre un árbol limpio extraído de un tar, nunca sobre el repo.

```bash
mkdir -p /tmp/rp/mut
cd /Users/<usuario>/cosmos
git archive 6a32781 -o /tmp/rp/pristino.tar        # el commit congelado de la revisión
cp progress/revision-profunda-2026-09-02/pruebas/sabotear.py /tmp/rp/mut/
cd /tmp/rp && python3 mut/sabotear.py M00          # línea base: tests OK, puente OK, validar rojo 1 (E19), 38/38
cd /tmp/rp && python3 mut/sabotear.py M15          # el sabotaje más contundente
```

Salida: una línea JSON con `estado` (`CAZADO` / `SUPERVIVIENTE` / `NO_APLICA`), las diferencias
contra la línea base y el detalle de cada suite. Cada mutación tarda ~45 s.

`M00` **debe** dar `tests: Ran 175 — OK` y `puente: Ran 113 — OK`. Si da menos tests o algún fallo,
el tar no está limpio: el árbol de trabajo se contamina al correr la suite (ver A05 del informe) y
eso produce falsos rojos — pasó en la primera tanda de esta revisión.
