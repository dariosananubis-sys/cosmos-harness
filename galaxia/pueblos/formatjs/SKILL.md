---
cosmos: pueblo
nombre: formatjs
padre: localizacion/mensajes
resumen: Mensajes en ICU: el plural y el formato de fecha los decide el estandar, y trae extractor y compilador.
---

https://github.com/formatjs/formatjs · MIT por paquete (`@formatjs/intl` y `@formatjs/cli` lo
declaran en su `package.json`; el monorepo no publica licencia en la raíz, así que la API de GitHub
no da SPDX) · 14.747★ · último push 2026-09-04 (comprobado 2026-09-04, API de GitHub y
`commits/HEAD.atom`: HEAD 2026-09-04T05:58Z; no archivado)

```bash
npm install @formatjs/intl @formatjs/cli
```

```js
import { createIntl, createIntlCache } from "@formatjs/intl";

const intl = createIntl({
  locale: "es",
  messages: {
    articulos: "{count, plural, =0 {sin articulos} one {un articulo} other {# articulos}}",
    caduca: "Caduca el {fecha, date, long}",
  },
}, createIntlCache());

intl.formatMessage({ id: "articulos" }, { count: 0 });              // "sin articulos"
intl.formatMessage({ id: "caduca" }, { fecha: new Date() });        // "Caduca el 4 de septiembre de 2026"
```

```bash
# extraer del codigo a un catalogo, y compilarlo al formato de ejecucion
npx formatjs extract 'src/**/*.{js,ts,tsx}' --out-file catalogo/es.json
npx formatjs compile catalogo/es.json --out-file compilado/es.json
```

Gana a `i18next` en portabilidad del catálogo: ICU MessageFormat es el mismo formato que entienden
`weblate`, las plataformas comerciales y las bibliotecas de Java, PHP o Python, así que el mensaje
escrito aquí sobrevive a un cambio de tecnología. Además el plural no lo inventa la biblioteca: sale
de las reglas CLDR, que ya saben que el ruso tiene tres formas y el árabe seis.

Frontera con `i18next`: aquel gana en andamiaje (detección de idioma, carga por HTTP, espacios de
nombres); este gana en estándar y en herramienta de línea de comandos —`extract` recorre el código y
saca el catálogo, `compile` lo deja en el formato rápido de ejecución—, que es lo que permite que el
código sea la fuente de verdad de qué hay que traducir.

Ojo: la sintaxis ICU es un lenguaje, y un mensaje mal cerrado revienta **en tiempo de ejecución**, no
al compilar el proyecto — por eso `formatjs compile` en la tubería no es opcional, es lo que convierte
ese fallo en un rojo de la construcción. Y el corrector de tipos que ofrece no comprueba que los
argumentos que pasas existan en el mensaje: `{count}` sin pasar `count` produce texto con el hueco
literal dentro, sin error.
