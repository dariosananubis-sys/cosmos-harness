---
cosmos: pueblo
nombre: extractor-de-curso
padre: extraccion/fuentes-web
resumen: Vuelca el temario de un aula virtual con tu sesion ya iniciada, sin marcar lecciones ni responder examenes.
---

Rescatado de la skill `curso-estudio` de un arnes propio; el envoltorio (preparar examenes de una
persona concreta) se ha quitado y queda la maquina. Los dos guiones viajan con el pueblo:
`scripts/extraer_curso.py` (537 lineas) y `scripts/chrome_cdp.sh`. Necesita `agent-browser`.

```bash
python3 scripts/extraer_curso.py https://aula.example/curso/mi-curso \
    --salida ./temario --solo-indice          # primero mira que ha encontrado
python3 scripts/extraer_curso.py https://aula.example/curso/mi-curso \
    --salida ./temario --descubrir --capturas --desde 1 --limite 300
```

Reconoce la forma de las URL de los gestores de aprendizaje habituales (Moodle, LearnDash, Teachable,
Docebo y compania: `/leccion/`, `/topic/`, `/mod/page/`, `/mod/book/`, `/unidad/`…), sigue el indice,
y deja cada leccion en Markdown. `--capturas` guarda las diapositivas que son imagen. `--desde N`
reanuda donde se quedo, que en un curso de doscientas lecciones no es un lujo.

**Es de solo lectura por diseno**: no marca lecciones como completadas, no envia formularios, no
responde cuestionarios y no simula interaccion humana. Esa restriccion esta en el guion, no en la
buena voluntad de quien lo usa.

El companero `chrome_cdp.sh` encierra un gotcha que cuesta una tarde descubrir: **Chrome 136 y
posteriores ignoran `--remote-debugging-port` cuando apuntan al perfil por defecto**, asi que no hay
forma de reutilizar tu sesion ya iniciada sin copiar antes el perfil a otra carpeta. El guion hace esa
copia y la borra al cerrar — y borrarla no es opcional, porque contiene las cookies de todas las
cuentas de ese perfil.

Gana a `trafilatura` y `scrapy`, que estan en este mismo pais, en lo unico que importa aqui: el
contenido esta **detras de un login** y repartido en un arbol de lecciones. Aquellos extraen muy bien
una pagina publica y no saben nada de sesiones ni de la estructura de un curso. Gana a conducir
`playwright` a mano en que ahi te toca escribir el descubrimiento, la paginacion y la reanudacion.

Ojo, tres. Las heuristicas de URL fallan en aulas hechas a medida: pasa `--selector` con el CSS de los
enlaces de leccion o te llevas el menu lateral como si fueran lecciones. **Los videos no se
transcriben aqui**: se extrae la transcripcion si la plataforma la publica como texto; si no, el
audio hay que pasarlo por `whisper-cpp`. Y volcar un curso de pago a tu disco puede ir contra sus
condiciones de uso: es cosa tuya comprobar que puedes.
