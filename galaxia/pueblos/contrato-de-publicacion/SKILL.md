---
cosmos: pueblo
nombre: contrato-de-publicacion
padre: infraestructura
resumen: Ocho puertas y un permiso que caduca deciden si se publica; sin copia ni vuelta atras verificadas, no sale.
---

Rescatado de la skill `release-publication` de un arnes propio. El contrato viaja con el pueblo:
`scripts/release_contract.py` (516 lineas, sin dependencias) y un `ejemplo-publicacion.json` valido.

```bash
python3 scripts/release_contract.py ready ejemplo-publicacion.json
#   {"grant_consumed": false, "receipt_recorded": false, "violations": []}   -> rc 0
```

Ocho puertas, todas obligatorias: `scope_confirmed`, `candidate_verified`,
`read_only_preflight_passed`, `backup_verified`, `rollback_verified`, `authorization_verified`,
`exact_target_verified`, `target_identity_verified`. Falta una y sale `gate_missing` con su nombre y
codigo `1`. Comprobado el 2026-09-02: quitando `backup_verified` del ejemplo, deniega.

Tres detalles que valen mas que el resto del guion:

- **La revision tiene que ser exacta**: 40 o 64 caracteres hexadecimales. Un `main`, un `latest` o un
  `v2` sale `revision_not_exact`. Publicar «lo ultimo» es como se publica algo que nadie miro.
- **El permiso caduca y es de un solo uso.** Lleva `issued_at`, `expires_at`, el efecto exacto
  (`publish_release`), el origen de destino y la revision. Autorizado hace dos horas para otra
  revision no vale: sale `grant_not_current`. Con `consume` se gasta contra un almacen y no se puede
  gastar dos veces.
- **El destino se comprueba dos veces**: la direccion y ademas la identidad del servidor. Publicar en
  el sitio correcto de la maquina equivocada es un fallo que la direccion sola no ve.

Gana a los entornos protegidos de una plataforma de integracion continua —revisores obligatorios
antes de desplegar—, que es el rival real: aquello comprueba que **alguien dijo que si**, y no que
exista copia verificada, vuelta atras probada y destino exacto. Gana a un checklist en un manual en
que un checklist no devuelve un codigo de salida.

Ojo, y es el limite entero: esto es un **arbitro de datos**, no un publicador. Comprueba que lo que le
cuentas es coherente; no verifica por su cuenta que la copia exista de verdad ni que la vuelta atras
funcione. Quien pone `backup_verified: true` sin haber restaurado nunca esa copia se ha mentido a si
mismo con mas ceremonia. Empareja cada puerta con una comprobacion real —una restauracion de prueba
para la copia, `despliegue-reanudable` para las fases— o esto es papeleo.
