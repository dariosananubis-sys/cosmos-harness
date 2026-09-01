---
cosmos: pueblo
nombre: bing-webmaster
padre: visibilidad
resumen: El otro buscador, el que alimenta a varios asistentes de IA: alta, envio de URL y de mapa del sitio.
---

`cosecha/bing-webmaster.py` — consola de la API del segundo buscador. Importa mas de lo que su cuota
de mercado sugiere, porque parte de los asistentes de IA se apoyan en su indice y no en el del
primero.

Trae anotado el enredo que hace perder la tarde: el envio de URL y de mapa devuelve un valor nulo
cuando ha ido bien, no solo cuando ha fallado. Quien interprete ese nulo como error reintentara para
siempre sobre algo que ya estaba hecho.
