---
cosmos: pueblo
nombre: playwright
padre: extraccion/fuentes-web
resumen: Conduce Chromium, Firefox y WebKit reales con esperas automaticas y traza de cada accion.
---

https://github.com/microsoft/playwright · Apache-2.0 · 95.465★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
pip install playwright && playwright install chromium
```

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    nav = p.chromium.launch()
    pag = nav.new_page(viewport={"width": 390, "height": 844})
    pag.goto("https://example.com")
    pag.wait_for_selector("h1", timeout=5000)     # TimeoutError explicito si no aparece
    print(pag.title(), pag.locator("h1").count())
    nav.close()
```

Base de hecho de todo lo que necesita ver una página renderizada. Cada acción espera a que el elemento
sea accionable y falla con traza: **no hay modo silencioso**, o la acción ocurrió o Playwright lo
dice. Es el mecanismo de fallo más limpio del nicho.

Frontera con `agent-browser`, que es lo que se usa aquí para mirar con los ojos: aquel reutiliza una
sesión ya iniciada por protocolo de depuración y sale más barato para QA interactivo; **esto es para
tuberías** —repetible, sin estado heredado, con traza por acción. `browser-use/browser-use` (111.924★)
va un piso más arriba: conduce la página con un modelo, para lo que no se puede describir con
selectores.

Ojo: no incluye evasión de detección de bots **por diseño**, y los forks «stealth» que la añaden están
descartados por el filtro legal de este árbol. Y `playwright install` descarga navegadores de cientos
de MB: en una máquina justa de memoria conviene instalar solo `chromium`, no los tres.
