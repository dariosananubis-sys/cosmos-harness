---
cosmos: pueblo
nombre: checkdmarc
padre: entregabilidad/autenticacion
resumen: Lee SPF, DKIM, DMARC y MX de un dominio y dice cual de los tres esta roto antes de enviar nada.
---

https://github.com/domainaware/checkdmarc · Apache-2.0 · 321★ · último push 2026-08-31 (comprobado
2026-09-04, API de GitHub y `commits/HEAD.atom`: HEAD 2026-08-31T04:44Z; no archivado)

```bash
pip install checkdmarc
```

```bash
checkdmarc github.com                             # informe JSON: SPF, DMARC, MX, DNSSEC y avisos
checkdmarc -f csv -o informe github.com wikipedia.org
checkdmarc --skip-tls github.com                  # sin la comprobacion de STARTTLS de cada MX
```

Gana a resolver los registros a mano con `dig` en lo único que se equivoca siempre quien lo hace a
mano: cuenta el **límite de diez consultas DNS de SPF** siguiendo los `include:` recursivamente y
avisa cuando se pasa. Un SPF que se pasa de ese límite es un `permerror`, y un `permerror` con la
política de DMARC en `reject` tira el correo legítimo — el fallo más caro de este oficio, y no se ve
mirando el registro con los ojos porque la cadena está a tres niveles de profundidad.

Frontera con `parsedmarc`, su hermano del mismo autor: este mira **lo que has publicado** antes de
enviar; aquel lee **lo que devuelven los receptores** cuando ya estás enviando. La configuración
correcta no garantiza que nadie más esté mandando en tu nombre, y eso solo lo dicen los informes.

Ojo de tamaño: 321★ y un solo mantenedor. Es la pieza más pequeña de este oficio y se dice; entra
porque no hay equivalente libre que cuente el límite de SPF y porque comparte autor con `parsedmarc`,
que sí tiene comunidad.

Ojo de alcance: comprueba lo que dice el DNS, no lo que hace tu servidor. Un DKIM publicado no
prueba que estés firmando —para eso hay que mirar una cabecera de un mensaje enviado de verdad— y un
verde aquí con la aplicación mal configurada es un falso verde.
