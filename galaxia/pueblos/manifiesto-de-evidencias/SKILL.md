---
cosmos: pueblo
nombre: manifiesto-de-evidencias
padre: cumplimiento
resumen: Liga cada prueba entregada a la version publicada por su hash; si alguien la retoca despues, salta.
---

Rescatado de la skill `web-release-evidence` de un arnes propio, quitado el envoltorio de un tramite
concreto. El validador viaja con el pueblo: `scripts/evidence_contract.py` (405 lineas, sin
dependencias) y un `ejemplo/` completo que se puede correr tal cual.

```bash
python3 scripts/evidence_contract.py ejemplo/manifiesto.json --root ejemplo
#   {"manifest_receipt": "d00f062f...", "ok": true, "violations": []}   -> rc 0
```

Cada prueba declara `kind`, `origin`, `collected_at`, su `sha256` y su ruta; el manifiesto declara la
huella de la version publicada, los origenes permitidos y los tipos de prueba obligatorios. El
validador comprueba que no falte ninguno, que ninguna prueba venga de un origen no declarado, que
ninguna sea mas vieja que `max_age_days`, que las marcadas `requires_attestation` tengan una
atestacion humana con actor, y que **el fichero en disco siga teniendo el hash que dice**. Comprobado
el 2026-09-02: editando un artefacto sin tocar el manifiesto sale `artifact_digest_mismatch` con el
identificador del elemento y codigo `1`.

Gana a `in-toto` y a las firmas de artefactos, que son el rival serio: aquellos acreditan **como se
construyo** un artefacto, con claves, un servicio de transparencia y una cadena que hay que montar.
Aqui la pregunta es otra y mas humilde: este paquete de pruebas —informes, capturas, mediciones— ¿es
de **esta** version y sigue intacto? Se responde con un guion local, sin claves, sin red y sin servicio
de terceros, que es lo unico que se sostiene en una entrega pequena. `reuse` y `ort`, en este mismo
nicho, miran licencias: otra pregunta distinta.

Ojo. Esto valida el **manifiesto**, no la verdad de lo que contiene: si una captura es de otra pagina
pero su hash cuadra, sale verde — la honestidad del `origin` y del `collected_at` la pone quien
recoge. Y `requires_attestation` comprueba que hay un identificador de persona, no que esa persona
mirara nada; sirve para dejar a alguien firmado al lado de lo que no se puede automatizar
(accesibilidad revisada a mano, sobre todo), no para sustituirlo.
