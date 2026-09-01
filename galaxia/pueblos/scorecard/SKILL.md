---
cosmos: pueblo
nombre: scorecard
padre: ciberseguridad/analisis/cadena-de-suministro
resumen: No busca fallos: puntua la higiene del repositorio, que es lo que deja entrar a los fallos.
---

https://github.com/ossf/scorecard · Apache-2.0 · 5.662★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
brew install scorecard
# o, sin Homebrew:
go install github.com/ossf/scorecard/v5@latest
```

```bash
# token de solo lectura; nunca escrito a fichero ni impreso
export GITHUB_AUTH_TOKEN=$(security find-internet-password -s github.com -w)

# la higiene de una dependencia antes de meterla
scorecard --repo=github.com/OWNER/REPO

# solo las comprobaciones que deciden, con evidencia de cada una
scorecard --repo=github.com/OWNER/REPO \
  --checks=Branch-Protection,Pinned-Dependencies,Token-Permissions,Dangerous-Workflow \
  --show-details --format=json
```

Pregunta distinta y complementaria a la de los escáneres de CVE: rama protegida, dependencias de
integración continua ancladas por identificador, permisos del testigo de CI, flujos peligrosos.
Gana a su hermana `ossf/allstar` (1.446★) para este uso porque es de **solo lectura**: Allstar
impone políticas, pero exige instalar una aplicación con permisos amplios sobre toda la
organización.

Ojo: puntúa el **proceso**, no el código — una nota de 9 no dice que el paquete esté limpio, dice
que es difícil colar algo por su tubería. Y varias comprobaciones necesitan token con permisos de
lectura de administración del repositorio; sin ellos devuelve `-1` (no evaluada), que la vista
resumida puede parecer un aprobado. Leer siempre `--show-details` antes de citar una nota.
