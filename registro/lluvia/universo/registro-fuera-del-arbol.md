---
cosmos: lluvia
nombre: registro-fuera-del-arbol
moja: []
resumen: Lo que no cuelga de la raiz configurada no lo ve nadie, aunque tenga frontmatter correcto.
---

# El registro estaba escrito y el arbol no lo veia

**Fecha:** 2026-09-01 · **Sintoma:** `cosmos estado` decia `lluvia 0` teniendo dos entradas
escritas, validas y con `cosmos: lluvia` en su frontmatter.

## Que era de verdad

`cargar_arbol` recorria **una sola raiz**, la de `[raiz] arbol` (`galaxia/`). El registro vive
fuera a proposito —`spec/REGISTRO.md` lo quiere como puerta aparte— asi que sus ficheros nunca
entraban. No era un fallo de las entradas: era que nadie las leia.

Lo caro del caso es que **la spec prometia lo contrario**: «el validador tambien las comprueba».
Una promesa de spec que ningun codigo cumple no da rojo nunca; solo hace que alguien se fie.

## Que NO era

- No era el frontmatter: parseaba bien, se comprobo a mano con `parsear_frontmatter`.
- No era `puente/lluvia.py`: esa pieza indexa `registro/` por su cuenta y siempre las encontro.
  Dos lectores distintos del mismo directorio, uno de ellos ciego, y ninguno se contradecia en
  voz alta.

## El arreglo

`cargar_arbol(..., tambien=(...))` acepta raices hermanas y `cosmos.toml` declara
`[raiz] registro = "registro"`. Las rutas de una raiz añadida se nombran desde su directorio
padre, para que un error diga `registro/lluvia/x.md` y no `lluvia/x.md`.

## Como verlo rapido la proxima vez

Si un nodo existe y el arbol no lo cuenta, la pregunta no es «que tiene mal el nodo» sino
**«esta debajo de la raiz que este comando carga»**. Un `find` por `cosmos:` comparado con
`cosmos estado --json` lo enseña en un comando.
