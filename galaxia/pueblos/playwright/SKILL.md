---
cosmos: pueblo
nombre: playwright
padre: extraccion/fuentes-web
resumen: Conduce Chromium, Firefox y WebKit reales con esperas automaticas y traza de cada accion.
---

Base de hecho de todo lo que necesita ver una pagina renderizada. Cada accion espera a que el
elemento sea accionable y falla con traza: es el mecanismo de fallo mas limpio del nicho.

Para trabajo interactivo con sesiones ya iniciadas, el navegador por protocolo de depuracion del otro
nicho sale mas barato; este es para tuberias.
