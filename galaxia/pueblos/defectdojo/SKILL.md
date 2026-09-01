---
cosmos: pueblo
nombre: defectdojo
padre: ciberseguridad/gobierno
resumen: Junta los hallazgos de todos los escaneres y les da dueno, estado y fecha.
---

https://github.com/DefectDojo/django-DefectDojo · BSD-3-Clause · 4.917★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
git clone https://github.com/DefectDojo/django-DefectDojo.git
cd django-DefectDojo
./dc-up.sh          # levanta la pila con Docker Compose
```

```bash
# importar el JSON de un escáner (Trivy, Semgrep, Nuclei…) por su API
curl -s -X POST "http://localhost:8080/api/v2/import-scan/" \
  -H "Authorization: Token $DD_TOKEN" \
  -F "scan_type=Trivy Scan" \
  -F "engagement=1" \
  -F "file=@resultado-trivy.json"
```

No escanea nada: **importa lo que escanean los demás** —conoce el formato de decenas de
herramientas, incluidas las de la cadena de suministro de este mismo nicho— y a cada hallazgo le
pone dueño, estado y fecha. Es la pieza que convierte cuatrocientos avisos sueltos en una lista que
se cierra. Gana a `infobyte/faraday` (6.699★) para el uso de agencia por deduplicar hallazgos entre
escaneos repetidos, que es lo que evita revisar el mismo fallo dos veces.

Ojo: es un **servicio con estado**, no un binario que se corre y termina — hay una base de datos que
respaldar y una instancia que mantener actualizada, y el token de su API es una credencial de pleno
derecho (va al gestor de secretos, nunca a un fichero de configuración). Y un hallazgo importado
hereda la gravedad que le puso el escáner de origen: si esa herramienta exageraba, DefectDojo
propaga la exageración — la deduplicación ordena, no juzga.
