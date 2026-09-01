---
cosmos: pueblo
nombre: dominios-libres
padre: web/construccion-de-sitios
resumen: Dice si un dominio esta libre cruzando tres fuentes publicas, y admite no saberlo en vez de inventarselo.
---

`cosecha/domain-suggester.py` — comprueba disponibilidad contra los servidores de nombres
publicados, el protocolo de registro y la consulta clasica de titularidad, y devuelve tres estados,
no dos: libre, pillado e **incierto**. Ese tercero es la razon de existir del guion: cuando las
fuentes no coinciden o la extension no responde, un cero donde deberia decir no lo se acaba en una
compra equivocada o en descartar un nombre que estaba disponible.

Con un nombre sin punto propone variantes ya comprobadas; con un dominio exacto responde por el.

La compra queda deliberadamente fuera. Los buscadores de los registradores hacen las dos cosas y por
eso su respuesta no es neutral: aqui solo hay fuentes publicas y ningun interes en que el nombre
salga ocupado.
