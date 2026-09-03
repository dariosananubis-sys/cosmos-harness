---
cosmos: pueblo
nombre: casdoor
padre: saas/identidad
resumen: Identidad autoalojada con inicio de sesion unico y los protocolos estandar ya hechos.
---

https://github.com/casdoor/casdoor · Apache-2.0 · 14.307★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
docker run -d --name casdoor -p 8000:8000 casbin/casdoor-all-in-one
# http://localhost:8000 — usuario admin, contrasena por defecto: CAMBIARLA antes de nada

# el cliente OIDC estandar vale tal cual; los metadatos estan en:
curl -s http://localhost:8000/.well-known/openid-configuration
```

Identidad autoalojada con inicio de sesión único y los protocolos estándar ya hechos: OIDC, OAuth2,
SAML, CAS y LDAP, más multiinquilino por organización. Gana a `Keycloak` en consumo y en tiempo de
arranque —un contenedor frente a un servidor Java con su base de datos— y a `Authentik` por traer
SAML y CAS de serie sin edición de pago.

Frontera con `panel-auth-cookie`, y es la que decide cuál se usa: para un panel con uno o dos
administradores, levantar un servidor de identidad completo es desproporcionado y gana el otro. **En
cuanto aparecen usuarios, roles o inicio de sesión único, gana este** y el otro se retira.

Ojo de procedencia, y hay que decirlo: **entra desde la segunda fila de su barrido, no de la
primera**, porque el hueco de identidad no tenía ningún candidato de primera fila y dejarlo vacío era
peor. Revisar en la próxima pasada. Sigue sin pueblo el aislamiento por inquilino: el único candidato
del barrido tenía dieciséis estrellas y un año parado.

Ojo operativo: la imagen «todo en uno» trae base de datos dentro y **credenciales de administrador
publicadas en su documentación**. Sirve para probar; para producción, base de datos aparte,
contraseña cambiada en el primer minuto y nunca expuesto a internet sin proxy con TLS delante
(`caddy`).
