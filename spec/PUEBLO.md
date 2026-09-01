# Qué tiene que traer un pueblo — normativo

Escrito tras el hallazgo H05 de `reviews/revision-adversarial-final.md`, que medió los 189 pueblos
existentes y encontró esto:

```
   0/189  url http(s)
   0/189  bloque de código
   0/189  comando de instalación
   0/189  evidencia de que se probó
ficheros que acompañan a cada pueblo: NINGUNO
```

Es decir: **189 párrafos que no nombran lo que hay que ejecutar.** `cosmos compilar` los enlaza en
`.claude/skills/`, así que un agente que invoque una de esas skills recibe prosa y se queda igual
que estaba. El criterio 1 de `spec/UNIVERSO.md` —«se ejecuta»— es eliminatorio, y ninguno lo cumple.

Este fichero define el mínimo para que un pueblo sirva.

## El contrato

Un pueblo responde a cuatro preguntas, en este orden. Si falta una, no está terminado.

| | Pregunta | Dónde |
|---|---|---|
| 1 | **¿Qué es y dónde está?** | URL del repositorio, en la primera línea del cuerpo |
| 2 | **¿Cómo se instala?** | Un comando, en bloque de código |
| 3 | **¿Cómo se usa?** | Un ejemplo mínimo que se pueda copiar y pegar |
| 4 | **¿Por qué este y no otro?** | Una o dos frases con la alternativa nombrada |

## La forma

```markdown
---
cosmos: pueblo
nombre: osv-scanner
padre: ciberseguridad/analisis/cadena-de-suministro
resumen: Audita lockfiles de 20 ecosistemas contra OSV.dev; base cacheada, corre sin red.
---

https://github.com/google/osv-scanner · Apache-2.0 · 10.9k★ · activo 2026-09-01

```bash
brew install osv-scanner
osv-scanner scan source -r .
```

Gana a `grype` en ruido: su base está deduplicada y da la versión afectada exacta, no un
listado de CVE por paquete de sistema. Si además quieres escanear imágenes de contenedor,
ahí `trivy` cubre más.

Ojo: `scan source` no ve dependencias transitivas de un lockfile ausente. Si el proyecto no
tiene lockfile, el resultado es un falso verde.
```

## Reglas que no se negocian

1. **La URL es literal y verificada.** No «el paquete oficial de X»: la URL. Sin ella, el pueblo no
   nombra nada y el agente que lo lea sigue sin saber qué ejecutar.
2. **Los datos de vida se citan con su fecha.** Estrellas, último push y licencia salen de una
   comprobación real, y se dice cuándo se hizo. Un dato sin fecha envejece en silencio.
3. **El comando de uso se puede copiar y pegar.** No pseudocódigo, no `<tu-configuración-aquí>`
   donde pueda haber un valor real de ejemplo.
4. **La comparación nombra al rival.** «Gana a las alternativas» no informa. «Gana a `grype` en
   ruido» sí, y además deja ver si la decisión sigue siendo válida cuando el rival mejore.
5. **Lo que no hace bien, también.** El apartado de avisos es lo que distingue una ficha útil de un
   anuncio. Un falso verde silencioso (`osv-scanner` sin lockfile) vale más que tres virtudes.
6. **Cero valores reales.** Ni claves, ni dominios de nadie, ni rutas de una máquina concreta. Los
   ejemplos usan marcadores explícitos.

## El presupuesto no cambia

El cuerpo de un pueblo **no está en el contexto de entrada**: solo su `resumen` (≤120 caracteres)
aparece en el catálogo, y solo cuando su nicho está activo. Así que el cuerpo puede ser todo lo
completo que haga falta — **no se recorta por miedo al coste, porque no cuesta.**

Lo que sí cuesta es el resumen. Ahí sigue mandando la regla de siempre: que diga en qué se distingue
de su vecino, no qué categoría de cosa es.

## Cuándo un pueblo lleva ficheros propios

Si la herramienta necesita configuración, plantillas o guiones para ser útil, van **dentro del
directorio del pueblo** (son `casa` en la taxonomía) y se referencian desde el cuerpo. `compilar`
exporta el directorio entero, así que llegan con la skill.

Un pueblo cuya utilidad depende de un fichero que no está es peor que no tenerlo: promete algo y no
lo entrega.
