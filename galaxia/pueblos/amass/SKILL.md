---
cosmos: pueblo
nombre: amass
padre: ciberseguridad/ofensiva/reconocimiento
resumen: Mapea la superficie del objetivo cruzando fuentes publicas con resolucion masiva de DNS.
---

https://github.com/owasp-amass/amass · Apache-2.0 (leído en `LICENSE`; la API de GitHub la reporta como `NOASSERTION`) · 15.081★ · último push 2026-07-19 (comprobado 2026-09-01)

```bash
brew install amass
```

```bash
# solo fuentes públicas, sin tocar la infraestructura del objetivo
amass enum -passive -d dominio-del-alcance.example -o pasivo.txt

# reconocimiento activo (resuelve y fuerza subdominios): más ruidoso, dentro del alcance
amass enum -active -brute -d dominio-del-alcance.example -dir ./caso/

# consultar el grafo de activos que quedó guardado
amass db -dir ./caso/ -names
```

Cubre el reconocimiento entero, pasivo y activo, y deja un **grafo de activos consultable**. Gana al
enumerador del mismo ecosistema `projectdiscovery/subfinder` (14.350★) porque subfinder solo hace el
paso pasivo, que aquí es una parte del trabajo y no el trabajo.

Ojo, la distinción que evita un problema legal: `-passive` no toca al objetivo (consulta fuentes de
terceros), pero `-active` y `-brute` **resuelven y fuerzan DNS contra su infraestructura** — eso es
tráfico dirigido y solo entra dentro de un alcance autorizado. Y el modo pasivo depende de APIs de
terceros: sin claves configuradas devuelve mucho menos, y una salida corta puede parecer «poca
superficie» cuando en realidad es «pocas fuentes consultadas».
