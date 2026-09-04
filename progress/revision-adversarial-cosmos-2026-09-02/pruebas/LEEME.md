# Los cinco guiones que sostienen el informe

Se ejecutan desde la raíz del repositorio con `python3`. Los cinco reproducen (verificado
2026-09-02 sobre `fbde93b`).

| Guion | Qué demuestra |
|---|---|
| `probe_sobreajuste.py` | H01 — qué encargos flipearon y qué palabras se les metieron |
| `probe_vocab.py` | H01 — las 6 palabras nuevas que solo existen en el conjunto de validación |
| `probe_estrella.py` | Afirmación 2 — la estrella no se engancha por nombre suelto (aguantó) |
| `probe_escala.py` | H10 — pendiente y punto de rotura reales |
| `probe_e17.py` | H09 — falso negativo y falso positivo de E17 |

**Requisito de `probe_sobreajuste.py` y `probe_vocab.py`:** necesitan `/tmp/advcosmos/mix`, que es
el código de HEAD con la `galaxia/` de `a4f880e`. Se reconstruye así:

```bash
cd ~/cosmos
mkdir -p /tmp/advcosmos/at_a4f880e /tmp/advcosmos/mix
git archive a4f880e | tar -x -C /tmp/advcosmos/at_a4f880e
git archive HEAD    | tar -x -C /tmp/advcosmos/mix
rm -rf /tmp/advcosmos/mix/galaxia
cp -R /tmp/advcosmos/at_a4f880e/galaxia /tmp/advcosmos/mix/galaxia
```
