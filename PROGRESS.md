# Progreso de COSMOS

Actualizado: 2026-09-01, catálogo por nicho implementado y medido.

## Cierre — catálogo por nicho

### Estado real

- `contexto_inicial(arbol, nichos=None)` conserva índice, océanos y mapa estructural, pero no carga
  ninguna ciudad ni pueblo. Con una selección incluye solo las skills invocables de esos sistemas.
- `cosmos medir` publica base y peor nicho; `--nicho` es repetible y `--combinacion a,b,c` mide una
  unión concreta. E16 usa siempre el peor nicho individual y nombra al culpable y el exceso.
- `cosmos validar --nicho n` valida E19 contra esa selección.
- `cosmos compilar --nicho n` aplana solo ese nicho. Las entradas registradas de otros nichos pasan
  por la misma regla de obsoletos: se borran si conservan el hash y se preservan si fueron tocadas.
  El manifiesto declara `nichos`, se escribe de forma atómica y sigue protegido por el lock previo.
- La revisión adversarial está en `reviews/codex-revisa-catalogo-por-nicho.md`. Intentó demostrar
  pérdida de descubrimiento, exceso en combinaciones, borrado ajeno y alternancia entre sesiones.

Durante esta ronda entraron por otra ventana los commits `0a37be9` y `b9e46b7`, que reorganizaron
`galaxia/` de 20 a 21 oficios y dejaron su índice E15 rojo a propósito. Se conservaron completos:
este trabajo no tocó `galaxia/`, `registro/` ni `cosecha/`. Por eso la salida inicial de 3.918 y la
final de 1.743 pertenecen a dos revisiones distintas del árbol. Sobre el árbol actual, activar los
21 nichos reproduce el antiguo catálogo global: 4.070 tokens, de los que 3.206 son catálogo. Durante
el cierre aparecieron además 16 estrellas nuevas sin seguimiento dentro de `galaxia/`; se preservaron
como trabajo de la otra ventana y solo elevaron `Universo`, no la entrada ni el peor nicho.

### Pruebas nuevas vistas fallar antes de implementar

Comando:

```text
python3 -m unittest tests.test_medidor.PruebasMedidor.test_catalogo_base_no_contiene_ningun_pueblo tests.test_medidor.PruebasMedidor.test_catalogo_web_contiene_solo_pueblos_de_web tests.test_validador.PruebasInvariantes.test_e16_usa_peor_nicho_aunque_el_caso_base_quepa tests.test_compilar.PruebasCompilacion.test_compilar_nicho_aplana_solo_web_y_aplica_hash_a_otros_nichos -v
```

Resultado literal previo:

```text
test_catalogo_base_no_contiene_ningun_pueblo (tests.test_medidor.PruebasMedidor.test_catalogo_base_no_contiene_ningun_pueblo) ... FAIL
test_catalogo_web_contiene_solo_pueblos_de_web (tests.test_medidor.PruebasMedidor.test_catalogo_web_contiene_solo_pueblos_de_web) ... ERROR
test_e16_usa_peor_nicho_aunque_el_caso_base_quepa (tests.test_validador.PruebasInvariantes.test_e16_usa_peor_nicho_aunque_el_caso_base_quepa) ... ERROR
test_compilar_nicho_aplana_solo_web_y_aplica_hash_a_otros_nichos (tests.test_compilar.PruebasCompilacion.test_compilar_nicho_aplana_solo_web_y_aplica_hash_a_otros_nichos) ... ERROR

Ran 4 tests in 0.020s

FAILED (failures=1, errors=3)
```

El fallo encontró el pueblo `web-tool` en el caso base. Los tres errores restantes fueron las
interfaces aún inexistentes: `contexto_inicial(..., nichos=...)`, `medir_arbol(..., nichos=...)` y
`compilar_arbol(..., nichos=...)`.

### Medición anterior solicitada

Ejecutada al inicio, antes del cambio, con `python3 -m cosmos medir galaxia --config galaxia.toml`:

```text
COSMOS  medir

  Entrada ......... 3.918 tokens   (estimado, ±desconocido, heurística v1)
  Universo ........ 11.725 tokens   (estimado, ±desconocido, heurística v1)
  Descarga ........ 66,6 %
  Presupuesto ..... 4.000     OK, quedan 82 tokens

  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)

  Lo más caro de la entrada:
    1.  3.059 tok  catálogo visible
    2.  520 tok  índice de galaxia
    3.  77 tok  oceano/irreversible
```

### Medición final solicitada

Ejecutada con `python3 -m cosmos medir galaxia --config galaxia.toml` después del cambio y de la
reorganización externa del árbol:

```text
COSMOS  medir

  Entrada base .... 1.100 tokens   (índice + océanos + estructura, sin pueblos; estimado, ±desconocido, heurística v1)
  Peor nicho ...... 1.743 tokens   (ciberseguridad, 26 pueblos)
  Universo ........ 11.154 tokens   (estimado, ±desconocido, heurística v1)
  Descarga ........ 84,4 %
  Presupuesto ..... 4.000     OK, quedan 2.257 tokens en el peor caso

  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)

  Lo más caro de la entrada evaluada:
    1.  879 tok  catálogo visible
    2.  525 tok  índice de galaxia
    3.  77 tok  oceano/irreversible
```

Contrafactual verificable sobre el mismo árbol actual, activando sus 21 nichos: `4.070` tokens,
`127` pueblos y `3.206` tokens de catálogo. El peor nicho individual reduce esa vista global en
`2.327` tokens (`57,2 %`).

### Batería final literal

Comando ejecutado con Python 3.11.15:

```text
/opt/homebrew/bin/python3.11 -m unittest discover -s tests -v
```

Salida literal:

```text
test_generar (test_cli.PruebasCLI.test_generar) ... ok
test_mapa (test_cli.PruebasCLI.test_mapa) ... ok
test_medir (test_cli.PruebasCLI.test_medir) ... ok
test_medir_nichos_repetidos_y_combinacion (test_cli.PruebasCLI.test_medir_nichos_repetidos_y_combinacion) ... ok
test_validar (test_cli.PruebasCLI.test_validar) ... ok
test_arbol_invalido_no_escribe_en_destino (test_compilar.PruebasCompilacion.test_arbol_invalido_no_escribe_en_destino) ... ok
test_compilar_nicho_aplana_solo_web_y_aplica_hash_a_otros_nichos (test_compilar.PruebasCompilacion.test_compilar_nicho_aplana_solo_web_y_aplica_hash_a_otros_nichos) ... ok
test_compilar_repara_e19_sin_interbloqueo (test_compilar.PruebasCompilacion.test_compilar_repara_e19_sin_interbloqueo) ... ok
test_editar_copia_a_mano_produce_e19 (test_compilar.PruebasCompilacion.test_editar_copia_a_mano_produce_e19) ... ok
test_editar_por_symlink_edita_la_verdad_y_no_rompe_e19 (test_compilar.PruebasCompilacion.test_editar_por_symlink_edita_la_verdad_y_no_rompe_e19) ... ok
test_fichero_ajeno_sobrevive_y_se_reporta (test_compilar.PruebasCompilacion.test_fichero_ajeno_sobrevive_y_se_reporta) ... ok
test_generar_repara_e15_pero_no_ignora_e19 (test_compilar.PruebasCompilacion.test_generar_repara_e15_pero_no_ignora_e19) ... ok
test_idempotencia_segunda_compilacion_no_cambia (test_compilar.PruebasCompilacion.test_idempotencia_segunda_compilacion_no_cambia) ... ok
test_lock_exclusivo_rechaza_segunda_compilacion (test_compilar.PruebasCompilacion.test_lock_exclusivo_rechaza_segunda_compilacion) ... ok
test_modo_copia_exporta_directorio_y_no_deja_symlinks (test_compilar.PruebasCompilacion.test_modo_copia_exporta_directorio_y_no_deja_symlinks) ... ok
test_obsoleta_intacta_se_borra_por_hash (test_compilar.PruebasCompilacion.test_obsoleta_intacta_se_borra_por_hash) ... ok
test_obsoleta_modificada_se_preserva_y_sale_del_manifiesto (test_compilar.PruebasCompilacion.test_obsoleta_modificada_se_preserva_y_sale_del_manifiesto) ... ok
test_seco_no_escribe_y_anuncia_lo_que_hace_luego (test_compilar.PruebasCompilacion.test_seco_no_escribe_y_anuncia_lo_que_hace_luego) ... ok
test_aproximado_y_exacto_respetan_margen_publicado (test_medidor.PruebasMedidor.test_aproximado_y_exacto_respetan_margen_publicado) ... skipped 'tokenizador exacto local no disponible; comparación declaradamente omitida'
test_arbol_de_tokens_conocidos_a_mano (test_medidor.PruebasMedidor.test_arbol_de_tokens_conocidos_a_mano) ... ok
test_arbol_vacio_no_publica_descarga_perfecta (test_medidor.PruebasMedidor.test_arbol_vacio_no_publica_descarga_perfecta) ... ok
test_catalogo_base_no_contiene_ningun_pueblo (test_medidor.PruebasMedidor.test_catalogo_base_no_contiene_ningun_pueblo) ... ok
test_catalogo_web_contiene_solo_pueblos_de_web (test_medidor.PruebasMedidor.test_catalogo_web_contiene_solo_pueblos_de_web) ... ok
test_contexto_y_medidor_usan_el_cuerpo_sin_frontmatter (test_medidor.PruebasMedidor.test_contexto_y_medidor_usan_el_cuerpo_sin_frontmatter) ... ok
test_no_medido_nunca_se_convierte_en_cero (test_medidor.PruebasMedidor.test_no_medido_nunca_se_convierte_en_cero) ... ok
test_regresion_descarga_nunca_sale_de_cero_uno (test_medidor.PruebasMedidor.test_regresion_descarga_nunca_sale_de_cero_uno) ... ok
test_e00_sintaxis_o_esquema (test_validador.PruebasInvariantes.test_e00_sintaxis_o_esquema) ... ok
test_e01_nodo_huerfano (test_validador.PruebasInvariantes.test_e01_nodo_huerfano) ... ok
test_e02_padre_inexistente (test_validador.PruebasInvariantes.test_e02_padre_inexistente) ... ok
test_e03_contencion_invertida (test_validador.PruebasInvariantes.test_e03_contencion_invertida) ... ok
test_e04_ciclo (test_validador.PruebasInvariantes.test_e04_ciclo) ... ok
test_e05_varias_galaxias (test_validador.PruebasInvariantes.test_e05_varias_galaxias) ... ok
test_e06_hermanos_homonimos (test_validador.PruebasInvariantes.test_e06_hermanos_homonimos) ... ok
test_e07_resumen_demasiado_largo (test_validador.PruebasInvariantes.test_e07_resumen_demasiado_largo) ... ok
test_e08_resumen_no_informa (test_validador.PruebasInvariantes.test_e08_resumen_no_informa) ... ok
test_e09_nivel_desconocido (test_validador.PruebasInvariantes.test_e09_nivel_desconocido) ... ok
test_e10_agua_sin_alcance (test_validador.PruebasInvariantes.test_e10_agua_sin_alcance) ... ok
test_e11_oceano_encubierto (test_validador.PruebasInvariantes.test_e11_oceano_encubierto) ... ok
test_e12_exceso_de_oceanos (test_validador.PruebasInvariantes.test_e12_exceso_de_oceanos) ... ok
test_e13_adjunto_incorrecto (test_validador.PruebasInvariantes.test_e13_adjunto_incorrecto) ... ok
test_e14_dos_estrellas (test_validador.PruebasInvariantes.test_e14_dos_estrellas) ... ok
test_e15_indice_desincronizado (test_validador.PruebasInvariantes.test_e15_indice_desincronizado) ... ok
test_e16_presupuesto_superado (test_validador.PruebasInvariantes.test_e16_presupuesto_superado) ... ok
test_e16_usa_peor_nicho_aunque_el_caso_base_quepa (test_validador.PruebasInvariantes.test_e16_usa_peor_nicho_aunque_el_caso_base_quepa) ... ok
test_e17_parafrasis_en_contexto_permanente (test_validador.PruebasInvariantes.test_e17_parafrasis_en_contexto_permanente) ... ok
test_e18_colision_global_al_aplanar_y_rutas (test_validador.PruebasInvariantes.test_e18_colision_global_al_aplanar_y_rutas) ... ok
test_e19_vista_plana_desincronizada (test_validador.PruebasInvariantes.test_e19_vista_plana_desincronizada) ... ok
test_e17_no_compara_nodos_que_no_coinciden (test_validador.PruebasValidadorComplementarias.test_e17_no_compara_nodos_que_no_coinciden) ... ok
test_ejemplo_completo_es_verde (test_validador.PruebasValidadorComplementarias.test_ejemplo_completo_es_verde) ... ok
test_identidad_completa_desambigua_provincias_homonimas (test_validador.PruebasValidadorComplementarias.test_identidad_completa_desambigua_provincias_homonimas) ... ok
test_meta_bateria_rechaza_validador_siempre_verde (test_validador.PruebasValidadorComplementarias.test_meta_bateria_rechaza_validador_siempre_verde) ... ok
test_validar_no_depende_de_que_exista_tokenizador (test_validador.PruebasValidadorComplementarias.test_validar_no_depende_de_que_exista_tokenizador) ... ok

----------------------------------------------------------------------
Ran 52 tests in 0.226s

OK (skipped=1)
```

`python3 -m compileall -q cosmos tests` y `git diff --check` terminaron con código 0. El ejemplo
sigue en `COSMOS verde 0 errores`. La galaxia real queda con un único E15 por el índice que el commit
externo dejó desincronizado; no se regeneró porque la restricción de esta ronda prohíbe tocar
`galaxia/`.

## Estado real de la ronda 3

### Terminado

- Aplicado `spec/NUCLEO.md` al código y al ejemplo: `padre`, `ilumina` y `orbita` usan ruta
  completa; la galaxia se referencia con `""`.
- Una sola función `cuerpo(nodo)` elimina frontmatter y recorta extremos. El medidor y E17 la
  reutilizan; no existe una segunda extracción.
- Una sola función `contexto_inicial(arbol)` materializa índice, cuerpos de océanos por nombre y
  catálogo. El catálogo excluye galaxia/sistemas/océanos y ordena los sólidos por rango.
- El medidor calcula `universo = entrada + resto`; la descarga queda acotada a `[0, 1]`, o
  `no_definida` cuando el universo es cero. `fuera_cosmos` nace como `no_medido` en el constructor.
- Eliminado el método `auto`. `validar` usa siempre `[medicion].metodo` de `cosmos.toml`; el flag
  `--metodo` solo existe en `medir`. `exacto` sin tokenizador falla en voz alta.
- Implementados E19 y `cosmos compilar` para ciudades/pueblos, en modo `symlink` relativo o
  `copia`. La copia excluye `.git`, `__pycache__` y nombres que empiezan por punto.
- El manifiesto usa rutas relativas y escritura temporal + `os.replace`. El lock
  `.cosmos/compilar.lock` se crea con `O_CREAT|O_EXCL` antes de leer o escribir el estado.
- Las entradas obsoletas intactas se eliminan por hash. Las modificadas se conservan, se reportan
  y salen del manifiesto. Las entradas nunca registradas se respetan.
- Orden de validación aplicado: `generar` omite solo E15 antes de escribir y la comprueba después;
  `compilar` omite solo E19 antes de escribir y la comprueba después.
- El ejemplo usa un directorio por skill con `SKILL.md`; su índice, manifiesto y vista plana están
  sincronizados. `cosmos validar --config cosmos.toml` devuelve `COSMOS  verde  0 errores`.
- `reviews/codex-revisa-nucleo.md` contiene la revisión adversarial con premisa invertida y los
  intentos concretos de tumbar la norma.

### Pruebas añadidas

- Regresión H1 con galaxia + océano y propiedad `0 <= descarga <= 1`.
- Regresión H2: el veredicto de `validar` es idéntico con tokenizador ausente o disponible cuando
  la configuración fija `aprox`.
- Cuerpo sin frontmatter y contexto inicial único.
- Dos provincias `revision` bajo padres distintos, con referencias completas inequívocas.
- E19 rojo por vista plana desincronizada.
- Los siete casos de `COMPILACION.md`: E18 con ambas rutas, árbol inválido sin escrituras,
  idempotencia, ajeno conservado, edición manual detectada, seco fiel y copia sin symlinks.
- Casos adicionales: E19 reparable sin interbloqueo, orden de `generar`, lock exclusivo, edición a
  través de symlink, y obsoletos intactos/modificados.

### Pendiente

No queda implementación solicitada en esta ronda.

La revisión adversarial no aprueba todavía `NUCLEO.md` como norma cerrada: identifica tres huecos
que requieren decisión del autor —tokenizador exacto sin identidad/version, directorio fuente de
una skill no definido y `rio` sin rango/ruta para el catálogo— más cinco precisiones menores. El
código adopta decisiones explícitas para poder funcionar, pero no modifica la spec normativa.

## Evidencia específica

Caso mínimo que antes daba descarga negativa:

```text
entrada= 48  universo= 48  descarga= 0.0
```

Compilación seca idempotente del ejemplo:

```text
COSMOS  compilar  seco

Creadas 0; actualizadas 0; iguales 2; ajenas respetadas 0; obsoletas eliminadas 0; obsoletas preservadas 0.
IGUAL <repo>/.claude/skills/probar-salida
IGUAL <repo>/.claude/skills/revisar-formato
```

La misma batería se ejecutó además con `/opt/homebrew/bin/python3.11`: 47 tests, OK, 1 saltado.

## Batería final literal

Comando ejecutado desde `<repo>`:

```text
python3 -m unittest discover -s tests -v
```

Salida literal:

```text
test_generar (test_cli.PruebasCLI.test_generar) ... ok
test_mapa (test_cli.PruebasCLI.test_mapa) ... ok
test_medir (test_cli.PruebasCLI.test_medir) ... ok
test_validar (test_cli.PruebasCLI.test_validar) ... ok
test_arbol_invalido_no_escribe_en_destino (test_compilar.PruebasCompilacion.test_arbol_invalido_no_escribe_en_destino) ... ok
test_compilar_repara_e19_sin_interbloqueo (test_compilar.PruebasCompilacion.test_compilar_repara_e19_sin_interbloqueo) ... ok
test_editar_copia_a_mano_produce_e19 (test_compilar.PruebasCompilacion.test_editar_copia_a_mano_produce_e19) ... ok
test_editar_por_symlink_edita_la_verdad_y_no_rompe_e19 (test_compilar.PruebasCompilacion.test_editar_por_symlink_edita_la_verdad_y_no_rompe_e19) ... ok
test_fichero_ajeno_sobrevive_y_se_reporta (test_compilar.PruebasCompilacion.test_fichero_ajeno_sobrevive_y_se_reporta) ... ok
test_generar_repara_e15_pero_no_ignora_e19 (test_compilar.PruebasCompilacion.test_generar_repara_e15_pero_no_ignora_e19) ... ok
test_idempotencia_segunda_compilacion_no_cambia (test_compilar.PruebasCompilacion.test_idempotencia_segunda_compilacion_no_cambia) ... ok
test_lock_exclusivo_rechaza_segunda_compilacion (test_compilar.PruebasCompilacion.test_lock_exclusivo_rechaza_segunda_compilacion) ... ok
test_modo_copia_exporta_directorio_y_no_deja_symlinks (test_compilar.PruebasCompilacion.test_modo_copia_exporta_directorio_y_no_deja_symlinks) ... ok
test_obsoleta_intacta_se_borra_por_hash (test_compilar.PruebasCompilacion.test_obsoleta_intacta_se_borra_por_hash) ... ok
test_obsoleta_modificada_se_preserva_y_sale_del_manifiesto (test_compilar.PruebasCompilacion.test_obsoleta_modificada_se_preserva_y_sale_del_manifiesto) ... ok
test_seco_no_escribe_y_anuncia_lo_que_hace_luego (test_compilar.PruebasCompilacion.test_seco_no_escribe_y_anuncia_lo_que_hace_luego) ... ok
test_aproximado_y_exacto_respetan_margen_publicado (test_medidor.PruebasMedidor.test_aproximado_y_exacto_respetan_margen_publicado) ... skipped 'tokenizador exacto local no disponible; comparación declaradamente omitida'
test_arbol_de_tokens_conocidos_a_mano (test_medidor.PruebasMedidor.test_arbol_de_tokens_conocidos_a_mano) ... ok
test_arbol_vacio_no_publica_descarga_perfecta (test_medidor.PruebasMedidor.test_arbol_vacio_no_publica_descarga_perfecta) ... ok
test_contexto_y_medidor_usan_el_cuerpo_sin_frontmatter (test_medidor.PruebasMedidor.test_contexto_y_medidor_usan_el_cuerpo_sin_frontmatter) ... ok
test_no_medido_nunca_se_convierte_en_cero (test_medidor.PruebasMedidor.test_no_medido_nunca_se_convierte_en_cero) ... ok
test_regresion_descarga_nunca_sale_de_cero_uno (test_medidor.PruebasMedidor.test_regresion_descarga_nunca_sale_de_cero_uno) ... ok
test_e00_sintaxis_o_esquema (test_validador.PruebasInvariantes.test_e00_sintaxis_o_esquema) ... ok
test_e01_nodo_huerfano (test_validador.PruebasInvariantes.test_e01_nodo_huerfano) ... ok
test_e02_padre_inexistente (test_validador.PruebasInvariantes.test_e02_padre_inexistente) ... ok
test_e03_contencion_invertida (test_validador.PruebasInvariantes.test_e03_contencion_invertida) ... ok
test_e04_ciclo (test_validador.PruebasInvariantes.test_e04_ciclo) ... ok
test_e05_varias_galaxias (test_validador.PruebasInvariantes.test_e05_varias_galaxias) ... ok
test_e06_hermanos_homonimos (test_validador.PruebasInvariantes.test_e06_hermanos_homonimos) ... ok
test_e07_resumen_demasiado_largo (test_validador.PruebasInvariantes.test_e07_resumen_demasiado_largo) ... ok
test_e08_resumen_no_informa (test_validador.PruebasInvariantes.test_e08_resumen_no_informa) ... ok
test_e09_nivel_desconocido (test_validador.PruebasInvariantes.test_e09_nivel_desconocido) ... ok
test_e10_agua_sin_alcance (test_validador.PruebasInvariantes.test_e10_agua_sin_alcance) ... ok
test_e11_oceano_encubierto (test_validador.PruebasInvariantes.test_e11_oceano_encubierto) ... ok
test_e12_exceso_de_oceanos (test_validador.PruebasInvariantes.test_e12_exceso_de_oceanos) ... ok
test_e13_adjunto_incorrecto (test_validador.PruebasInvariantes.test_e13_adjunto_incorrecto) ... ok
test_e14_dos_estrellas (test_validador.PruebasInvariantes.test_e14_dos_estrellas) ... ok
test_e15_indice_desincronizado (test_validador.PruebasInvariantes.test_e15_indice_desincronizado) ... ok
test_e16_presupuesto_superado (test_validador.PruebasInvariantes.test_e16_presupuesto_superado) ... ok
test_e17_parafrasis_en_contexto_permanente (test_validador.PruebasInvariantes.test_e17_parafrasis_en_contexto_permanente) ... ok
test_e18_colision_global_al_aplanar_y_rutas (test_validador.PruebasInvariantes.test_e18_colision_global_al_aplanar_y_rutas) ... ok
test_e19_vista_plana_desincronizada (test_validador.PruebasInvariantes.test_e19_vista_plana_desincronizada) ... ok
test_e17_no_compara_nodos_que_no_coinciden (test_validador.PruebasValidadorComplementarias.test_e17_no_compara_nodos_que_no_coinciden) ... ok
test_ejemplo_completo_es_verde (test_validador.PruebasValidadorComplementarias.test_ejemplo_completo_es_verde) ... ok
test_identidad_completa_desambigua_provincias_homonimas (test_validador.PruebasValidadorComplementarias.test_identidad_completa_desambigua_provincias_homonimas) ... ok
test_meta_bateria_rechaza_validador_siempre_verde (test_validador.PruebasValidadorComplementarias.test_meta_bateria_rechaza_validador_siempre_verde) ... ok
test_validar_no_depende_de_que_exista_tokenizador (test_validador.PruebasValidadorComplementarias.test_validar_no_depende_de_que_exista_tokenizador) ... ok

----------------------------------------------------------------------
Ran 47 tests in 0.211s

OK (skipped=1)
```

No se instaló ninguna dependencia ni se usó red. El único salto es el test comparativo que requiere
un tokenizador exacto local; el fallo explícito de `exacto` sin tokenizador sí está implementado.
