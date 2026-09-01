---
cosmos: pueblo
nombre: web-fidelidad-elementor
padre: web/construccion-de-sitios
resumen: Mide el maquetado contra el mockup en pixeles y corrige con controles nativos, sin CSS pegado.
---

Mecanismo propio de esta casa. **Aviso de procedencia: el guion no vive en este árbol** — es la skill
`web-fidelidad-elementor` del arnés (`.claude/skills/web-fidelidad-elementor/SKILL.md`), y este pueblo
solo la referencia. Si el árbol se compila en una máquina que no tenga ese arnés, este pueblo promete
algo que no entrega.

```bash
# 1. la puerta de entrada obligatoria del oficio, primero y siempre
#    (skill `web-elementor-cero-fallos`, nunca en su lugar)
# 2. medir el montaje contra el mockup, por ancho, en numeros:
agent-browser --session fidelidad-<slug> open https://<staging>/<pagina>
agent-browser --session fidelidad-<slug> set viewport 1440 900
agent-browser --session fidelidad-<slug> eval \
  "JSON.stringify({sw:document.documentElement.scrollWidth, h1:document.querySelectorAll('h1').length})"
agent-browser --session fidelidad-<slug> close
```

Por qué gana a las colecciones de skills de terceros para el mismo constructor —`Mekko-Digital/elementor-skills`
(1★), `guramzhgamadze/WordPress-Elementor-Skill` (25★) y las demás—: aquellas **opinan** sobre el
resultado en prosa; esto lo **mide en números** contra el mockup y contra webs ya validadas, y reintenta
hasta converger. Cubre cabecera, pie y espacios en todos los anchos, y corrige con controles nativos
de Elementor, sin CSS pegado.

Ojo, tres cosas: un `scrollWidth` mayor que el ancho del viewport es desbordamiento horizontal aunque
la página «se vea bien»; «presente en el DOM» no es «visible» —exigir `offsetParent` y dimensiones
mayores que cero—; y esto se invoca **después** de la puerta de entrada obligatoria, nunca en su lugar.
Reutilizar una sesión de `agent-browser` de otro trabajo mide otra página y el informe sale entero y
es mentira.
