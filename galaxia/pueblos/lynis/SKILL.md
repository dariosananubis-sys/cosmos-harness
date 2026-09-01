---
cosmos: pueblo
nombre: lynis
padre: ciberseguridad/defensiva
resumen: Audita el endurecimiento de un host UNIX contra listas ejecutables, no un documento.
---

https://github.com/CISOfy/lynis · GPL-3.0 · 16.262★ · último push 2026-08-05 (comprobado 2026-09-01)

```bash
brew install lynis
# en el servidor auditado, mejor desde el repositorio del proyecto que desde el de la distribución
```

```bash
# auditoría completa del sistema local, sin preguntar entre secciones
sudo lynis audit system --quick

# solo un bloque, cuando ya se está corrigiendo algo concreto
sudo lynis audit system --tests-from-group authentication,ssh

# el resultado que sirve para comparar dos fechas
sudo lynis audit system --quick --report-file ./lynis-$(date +%F).dat
```

Cuelga del continente y no de un país porque no agrupa con nadie: es el único de su hueco. Gana a
`OpenSCAP/openscap` (1.810★) para el uso de agencia porque corre con un guion y sin instalar nada en
el objetivo; OpenSCAP es el estándar certificado NIST y es mejor cuando el cliente exige un
cumplimiento formal (CIS, PCI-DSS) firmado. Frontera con `scorecard`: allí se mira la higiene del
proyecto, aquí la de la máquina donde ese proyecto acaba corriendo.

Ojo: su «índice de endurecimiento» **no es una nota de seguridad**, es un recuento de sugerencias
atendidas — se sube apagando avisos y sin arreglar nada. Y muchas comprobaciones solo se ejecutan
con `sudo`: correrlo como usuario normal da una lista mucho más corta y engañosamente tranquila.
Leer siempre el recuento de pruebas ejecutadas junto al índice.
