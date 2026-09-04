---
cosmos: pueblo
nombre: i18next
padre: localizacion/mensajes
resumen: Cambia de idioma en caliente en JavaScript y trae detector, carga por HTTP y respaldo de idioma de serie.
---

https://github.com/i18next/i18next · MIT · 8.625★ · último push 2026-09-03 (comprobado 2026-09-04,
API de GitHub y `commits/HEAD.atom`: HEAD 2026-09-03T20:23Z; no archivado)

```bash
npm install i18next
```

```js
import i18next from "i18next";

await i18next.init({
  lng: "es",
  fallbackLng: "en",
  resources: {
    es: { translation: { saludo: "Hola {{nombre}}", articulo_one: "{{count}} articulo", articulo_other: "{{count}} articulos" } },
    en: { translation: { saludo: "Hello {{nombre}}", articulo_one: "{{count}} item",     articulo_other: "{{count}} items" } },
  },
});

i18next.t("saludo", { nombre: "Ada" });   // "Hola Ada"
i18next.t("articulo", { count: 3 });      // "3 articulos"
await i18next.changeLanguage("en");       // cambia sin recargar la pagina
```

Gana a `formatjs` cuando lo que hace falta es el andamiaje y no el estándar: detección del idioma del
navegador o de la URL, carga de los ficheros de traducción bajo demanda por HTTP, respaldo en cadena
de idiomas y espacios de nombres para partir el catálogo por pantalla. Todo eso son complementos
oficiales suyos y en `formatjs` hay que montarlo.

Frontera con `formatjs`: aquel implementa ICU MessageFormat, el estándar que también entienden las
herramientas de traducción; este trae un formato de plural propio (`_one`, `_other`) que es más
cómodo de escribir y menos portable. Si el catálogo va a viajar a una plataforma de traducción o a
otro lenguaje, el estándar pesa más que la comodidad.

Ojo, y es el falso verde clásico: una clave que no existe **devuelve la propia clave** y la
aplicación sigue pintando. `saludo.usuario` sale en pantalla tal cual y nadie se entera hasta que lo
ve un cliente. Se apaga con `parseMissingKeyHandler` o `saveMissing`, y se comprueba en la prueba,
no a ojo. Y `init()` es asíncrono: llamar a `t()` antes de que resuelva devuelve la clave por la
misma vía, con lo que un fallo de orden se disfraza de traducción ausente.
