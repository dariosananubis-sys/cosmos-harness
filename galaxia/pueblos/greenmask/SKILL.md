---
cosmos: pueblo
nombre: greenmask
padre: cumplimiento/datos-personales
resumen: Vuelca la base de produccion ya anonimizada, para que el entorno de pruebas no lleve datos reales.
---

https://github.com/GreenmaskIO/greenmask · Apache-2.0 · 1.756★ · último push 2026-08-25 (comprobado
por API de GitHub el 2026-09-01)

```bash
brew install greenmask      # o el binario de la version publicada; usa pg_dump/pg_restore por debajo
```

```yaml
# greenmask.yaml
dump:
  transformation:
    - schema: public
      name: clientes
      transformers:
        - name: Hash                 # determinista: el mismo correo da siempre el mismo resultado
          params: { column: email, salt_from_env: GREENMASK_SALT }
        - name: RandomPersonName
          params: { columns: [{ name: nombre }, { name: apellidos }] }
        - name: NoiseDate
          params: { column: fecha_nacimiento, min_ratio: "1 year", max_ratio: "5 years" }
        - name: Replace
          params: { column: telefono, value: "600000000" }
```

```bash
export GREENMASK_SALT="$(security find-generic-password -s <SERVICIO_EN_EL_LLAVERO> -w)"
greenmask --config greenmask.yaml dump
greenmask --config greenmask.yaml restore latest      # a la base de pruebas, ya sin datos reales
```

Resuelve el caso concreto que rompe el cumplimiento sin que nadie se dé cuenta: **el volcado de
producción que alguien copió a su portátil para reproducir un fallo**. Ese fichero es un tratamiento
de datos personales sin base jurídica, y suele vivir años en una carpeta de descargas.

Frontera con sus dos vecinos, que no se sustituyen: `presidio` encuentra y tacha datos personales en
**texto**; `arx` demuestra que lo que queda **no reidentifica**; esto reescribe **la base entera**
manteniendo claves ajenas, tipos y relaciones, de modo que la aplicación arranca igual contra el
volcado transformado. Y gana a `smithoss/gonymizer` (161★) por cobertura y ritmo, y a un guion de
`UPDATE` escrito a mano —que es lo que se hace de verdad— porque aquel se queda desactualizado en
cuanto se añade una columna y este falla en voz alta si la tabla configurada ya no existe.

**Norma que cubre**: principio de minimización del **RGPD** (Reglamento UE 2016/679, art. 5.1.c) y la
seudonimización que su art. 32.1.a cita como medida de seguridad del tratamiento; en España, con la
**LOPDGDD (Ley Orgánica 3/2018)** encima. Territorio: **Unión Europea**. Es la medida técnica, no la
justificación jurídica.

**Lo que NO comprueba**: no busca dónde están los datos personales —hay que decírselo columna a
columna, y la que se olvide sale en claro—, no mide riesgo de reidentificación de lo que queda, y no
lleva registro de tratamientos. Una base «anonimizada» que conserva código postal, sexo y fecha de
nacimiento **sigue reidentificando**: esa comprobación es de `arx`, no de aquí.

Ojo operativo: el transformador `Hash` es determinista a propósito —hace falta para que las relaciones
sigan cuadrando—, así que **con la misma sal, dos volcados son enlazables entre sí**. La sal se trata
como un secreto: fuera del repositorio y por variable de entorno.
