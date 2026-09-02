---
cosmos: pueblo
nombre: gate-de-salida-web
padre: web/calidad-de-sitio
resumen: Dice PASA o FALLA de un sitio; lo que no se pudo medir cuenta como fallo, jamas como aprobado.
---

Destilado generico del gate de salida de webs de un arnes propio, sin nada de aquel negocio dentro.
El guion viaja con el pueblo: `scripts/gate_web.py`. Necesita `agent-browser` y `Pillow`.

```bash
python3 scripts/gate_web.py http://127.0.0.1:8731 \
    --referencia http://127.0.0.1:8732 --anchos 1440 390 \
    --paginas / /contacto --informe informe.json
```

`0` PASA, `1` FALLA, y el informe JSON queda escrito como prueba. Seis comprobaciones, todas
criticas: HTTP de cada pagina, desborde horizontal (`scrollWidth` contra `clientWidth`), exactamente
un `h1` **visible** (con `offsetParent`, no «presente en el DOM»), imagenes que no cargan, pagina
practicamente vacia, y comparacion de pixeles contra la referencia franja a franja de 40 px, que dice
**donde** difiere y no solo cuanto.

La regla que lo hace distinto de cualquier guion de comprobaciones: **una comprobacion que no se pudo
ejecutar sale `no_medido` y no cuenta como aprobada.** El navegador que no esta, la referencia que no
se dio, el sitio que no responde: todo eso ponia verde a los demas. Aqui impide el PASA igual que un
fallo, y el informe dice cuantas y cuales. Por eso `--sin-pixeles` existe pero no ayuda: declara a
proposito que hoy no se compara, y el gate sigue sin poder pasar.

Gana a `lighthouse` y `unlighthouse`, que estan aqui al lado, en la pregunta que responde: aquellos
puntuan **rendimiento y buenas practicas** de una URL contra un baremo absoluto, y salen con exito
aunque la pagina este descuadrada. Este compara contra **la maqueta que el cliente aprobo**, que es la
unica verdad que discute. Gana a una suite de `playwright` en lo que ninguna suite cubre: una suite
afirma lo que a alguien se le ocurrio afirmar, y los defectos que canta un cliente —«movido»,
«descuadrado», «el texto no acompana a la caja»— caen justo fuera de esa lista; los pixeles no eligen.

Ojo, tres. La comparacion de pixeles es **estricta y tonta**: fuentes que cargan tarde, animaciones,
carruseles o contenido dinamico dan franjas rojas que no son defectos — sube `--umbral` o congela lo
dinamico antes de juzgar. Mide solo las paginas que le pases: lo que no este en `--paginas` no existe
para el gate, y eso no sale como `no_medido` porque nadie lo pidio. Y un PASA dice que esas paginas se
parecen a la referencia a esos anchos, no que el sitio sea bueno: accesibilidad es `axe-core` y
`a11y-auditoria-wcag`, velocidad es `lighthouse`.
