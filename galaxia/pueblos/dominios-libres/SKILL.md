---
cosmos: pueblo
nombre: dominios-libres
padre: web/construccion-de-sitios
resumen: Dice si un dominio esta libre cruzando tres fuentes publicas, y admite no saberlo en vez de inventarselo.
---

`cosecha/domain-suggester.py` — herramienta propia, no de GitHub. Solo fuentes públicas, sin API de
pago ni cuenta de registrador.

```bash
python3 cosecha/domain-suggester.py ejemplo-de-marca.es      # dominio exacto -> LIBRE / PILLADO / ?
python3 cosecha/domain-suggester.py "taller de bicicletas"   # base -> hasta 5 variantes .es/.com libres
```

Cruza tres fuentes —servidores de nombres publicados, RDAP y la consulta clásica de titularidad— y
devuelve **tres estados, no dos**: libre, pillado e **incierto**. Ese tercero es la razón de existir
del guion: cuando las fuentes no coinciden o la extensión no responde, un «libre» donde debería decir
«no lo sé» acaba en una compra equivocada, y un «pillado» acaba descartando un nombre que estaba
disponible.

Gana al buscador de cualquier registrador en lo que no se puede arreglar: **su respuesta no es
neutral** —vende el dominio y vende las alternativas— y muchos hacen las dos cosas a la vez, comprobar
y ofrecer. Aquí solo hay fuentes públicas y ningún interés en que el nombre salga ocupado. La compra
queda deliberadamente fuera, y eso es una decisión de diseño, no una carencia.

Ojo: un dominio libre en RDAP puede estar en periodo de gracia o reservado por el registro, así que
«LIBRE» no garantiza que se pueda comprar. Y `?` **no es una respuesta útil que se pueda ignorar**: es
la que obliga a mirar a mano. Comprar cuesta dinero: eso lo autoriza una persona, siempre.
