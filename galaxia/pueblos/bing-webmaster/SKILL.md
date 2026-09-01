---
cosmos: pueblo
nombre: bing-webmaster
padre: visibilidad
resumen: El otro buscador, el que alimenta a varios asistentes de IA: alta, envio de URL y de mapa del sitio.
---

`cosecha/bing-webmaster.py` — herramienta propia, no hay repositorio público. La ruta ES la
referencia. Consola de la API REST de Bing Webmaster Tools
(https://learn.microsoft.com/en-us/bingwebmaster/getting-started).

```bash
export BING_API_KEY=<CLAVE_API>        # una por cuenta, desde la interfaz de Bing

python3 cosecha/bing-webmaster.py ping
python3 cosecha/bing-webmaster.py add-site https://ejemplo.test/
python3 cosecha/bing-webmaster.py verify https://ejemplo.test/          # tras inyectar el meta
python3 cosecha/bing-webmaster.py submit-feed https://ejemplo.test/ https://ejemplo.test/sitemap_index.xml
python3 cosecha/bing-webmaster.py submit-url  https://ejemplo.test/ https://ejemplo.test/contacto/
python3 cosecha/bing-webmaster.py quota https://ejemplo.test/
python3 cosecha/bing-webmaster.py url-info https://ejemplo.test/ https://ejemplo.test/contacto/
```

El otro buscador **importa más de lo que su cuota de mercado sugiere**, porque parte de los asistentes
de IA se apoyan en su índice y no en el del primero. Es la pareja de `search-console` y se prefiere a
hacerlo por la interfaz web porque el alta, la verificación y el envío de mapa son exactamente los
pasos que se repiten en cada web de cliente: aquí son una línea reproducible en el ledger, no un
recorrido de pantallas.

Ojo, y es el enredo que hace perder la tarde: **el envío de URL y de mapa devuelve un valor nulo
cuando ha ido BIEN**, no solo cuando ha fallado. Quien interprete ese nulo como error reintentará para
siempre sobre algo que ya estaba hecho — y hay cuota diaria de envío, así que el reintento la quema.
Comprobar con `quota` antes de un lote.

Ojo de verificación: Bing **no expone `getToken`** como el otro buscador. El meta `msvalidate.01` se
saca una vez a mano en su interfaz (o se importa la verificación desde Search Console) y se guarda en
`BING_META_TOKEN`. Ese paso no se puede automatizar entero.
