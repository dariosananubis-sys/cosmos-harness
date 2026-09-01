# Progreso de COSMOS

Actualizado: 2026-09-01, ronda 3 de Codex relanzada.

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
IGUAL /Users/<usuario>/cosmos/.claude/skills/probar-salida
IGUAL /Users/<usuario>/cosmos/.claude/skills/revisar-formato
```

La misma batería se ejecutó además con `/opt/homebrew/bin/python3.11`: 47 tests, OK, 1 saltado.

## Batería final literal

Comando ejecutado desde `/Users/<usuario>/cosmos`:

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
