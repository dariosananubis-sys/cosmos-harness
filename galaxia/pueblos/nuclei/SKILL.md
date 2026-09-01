---
cosmos: pueblo
nombre: nuclei
padre: ciberseguridad/ofensiva/reconocimiento
resumen: Escanea con miles de plantillas de la comunidad sobre HTTP, DNS, red y nube.
---

https://github.com/projectdiscovery/nuclei · MIT · 30.962★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
brew install nuclei
nuclei -update-templates
```

```bash
# escaneo contra un objetivo del alcance, solo severidad alta y crítica
nuclei -u https://OBJETIVO-DEL-ALCANCE/ -severity high,critical -o hallazgos.txt

# varios objetivos desde fichero, limitando el ritmo para no saturar
nuclei -list objetivos-del-alcance.txt -rate-limit 50
```

Ocupa el hueco que en el mundo comercial ocupan los escáneres de vulnerabilidades por licencia
(Nessus, Qualys): miles de plantillas mantenidas por la comunidad sobre HTTP, DNS, red y nube, y es
un motor real que encadena peticiones, no solo un fuzzer de HTTP. Frontera con el vecino de la
cadena de suministro (`osv-scanner`, `trivy`): aquí se mira el **objetivo vivo**, allí el fichero de
bloqueo y la imagen.

Ojo: las plantillas son **contribuciones de la comunidad** — la mayoría excelentes, pero una mal
escrita da un falso positivo que hay que confirmar a mano antes de meterlo en un informe. Y a ritmo
alto contra un objetivo frágil, miles de peticiones pueden tumbarlo: `-rate-limit` no es opcional en
producción de un cliente. Cada hallazgo se verifica manualmente; una plantilla que «coincide» no
siempre es una vulnerabilidad explotable.
