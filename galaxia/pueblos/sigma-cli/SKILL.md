---
cosmos: pueblo
nombre: sigma-cli
padre: ciberseguridad/defensiva/deteccion
resumen: La regla se escribe una vez y se traduce a la sintaxis de cada plataforma.
---

https://github.com/SigmaHQ/sigma-cli · LGPL-2.1 · 209★ · último push 2026-07-07 (comprobado 2026-09-01) · corpus: https://github.com/SigmaHQ/sigma · 10.966★ · último push 2026-09-01

```bash
pipx install sigma-cli
sigma plugin install splunk elasticsearch      # un backend por plataforma destino
git clone --depth 1 https://github.com/SigmaHQ/sigma.git
```

```bash
# una regla, traducida a la sintaxis de la plataforma que toque
sigma convert -t splunk -p sysmon sigma/rules/windows/process_creation/

# comprobar que la regla es válida antes de subirla a ningún sitio
sigma check ./mis-reglas/
```

Entra el **motor**, no el corpus: el corpus (`SigmaHQ/sigma`) es el estándar y se consume desde
aquí. Es el equivalente para registros de lo que `yara` es para ficheros y memoria; por eso conviven
y no se sustituyen. Y es lo que evita reescribir la misma lógica de detección una vez por SIEM.

Ojo, las estrellas engañan: **209★ es el motor, no el proyecto** — el corpus tiene 10.966★ y se
publica a diario. Segundo aviso, el que de verdad cuesta dinero: la traducción **depende del perfil
de mapeo de campos** (`-p sysmon`, `-p windows_audit`…). Con el perfil equivocado la regla se
convierte igual, sin error, y en la plataforma no casa nunca — una detección que nunca dispara se
parece mucho a una detección que funciona. Toda regla convertida se prueba contra un evento real
conocido antes de darla por desplegada.
