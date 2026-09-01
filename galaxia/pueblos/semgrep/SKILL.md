---
cosmos: pueblo
nombre: semgrep
padre: ciberseguridad/analisis/vulnerabilidades
resumen: Busca patrones por sintaxis real en treinta lenguajes, con reglas legibles y ampliables.
---

https://github.com/semgrep/semgrep · LGPL-2.1 · 16.459★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
brew install semgrep
# o:  pipx install semgrep
```

```bash
# reglas de seguridad mantenidas por el proyecto, sin cuenta ni clave
semgrep --config=p/security-audit --error .

# una regla propia, que es donde está su valor real
cat > regla.yaml <<'YML'
rules:
  - id: subproceso-con-shell
    languages: [python]
    severity: ERROR
    message: subprocess con shell=True sobre entrada no validada
    pattern: subprocess.$FN(..., shell=True, ...)
YML
semgrep --config=regla.yaml .
```

No es una expresión regular disfrazada: casa sobre el **árbol sintáctico**, así que `subprocess.run(
  cmd, shell=True)` partido en tres líneas también cae. Gana a los analizadores nativos de cada
lenguaje (`bandit`, `gosec`) por cubrir treinta lenguajes con una sola sintaxis de regla, legible
por quien no escribió el motor.

Ojo, y lo dice su propio README: la edición libre **"will miss many true positives as it can only
analyze code within the boundaries of a single function or file"**. El seguimiento de contaminación
entre funciones y ficheros exige Semgrep AppSec Platform, de pago, y no se usa. Consecuencia
práctica: un verde de Semgrep CE significa «no hay nada dentro de una función», no «no hay nada».
Descartado por lo mismo el motor con seguimiento interprocedimental (CodeQL), técnicamente superior:
su uso sobre código privado exige suscripción de la plataforma.
