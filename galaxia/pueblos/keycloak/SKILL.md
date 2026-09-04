---
cosmos: pueblo
nombre: keycloak
padre: saas/identidad
resumen: El nombre que todo cliente pide de memoria; mas pesado que casdoor pero el que reconoce quien contrata.
---

https://github.com/keycloak/keycloak · Apache-2.0 · 36.579★ · último push 2026-09-03 (comprobado
2026-09-03)

```bash
docker run -d --name keycloak -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=change-me   # cámbiala antes de nada \
  quay.io/keycloak/keycloak:latest start-dev
# http://localhost:8080 — modo start-dev: sin TLS, solo para probar
```

```bash
curl -s http://localhost:8080/realms/master/.well-known/openid-configuration
```

`casdoor` ya vive en este país y su ficha lo deja escrito: gana a `Keycloak` en consumo y tiempo de
arranque, un contenedor Go frente a un servidor Java con base de datos. Esa comparación técnica sigue
siendo cierta y no se revierte aquí. Lo que entra con `keycloak` es otra cosa: es el producto que un
cliente **pide por nombre** — quien ha oído hablar de identidad autoalojada en el mundo Java/empresa
conoce `Keycloak`, casi nadie fuera del nicho ha oído hablar de `casdoor`. Cuando el requisito viene
así de un cliente o de un pliego, discutir la elección técnica no cambia el nombre que hay que
entregar.

Gana a construir lo mismo a mano por ser el estándar de facto detrás de Red Hat SSO: OIDC, OAuth2,
SAML, gestión de roles y federación con LDAP/Active Directory, con el ecosistema de adaptadores más
grande del hueco (hay librería de cliente para prácticamente cualquier framework empresarial).
Frente a `openfga`, la frontera es la pregunta que responde cada uno: `keycloak` dice **quién eres**
(autenticación e identidad); `openfga` dice **qué puedes hacer** una vez identificado
(autorización de grano fino) — se usan juntos, no en lugar del otro.

Ojo, y es el coste real de elegirlo sobre `casdoor`: corre sobre la JVM con una base de datos detrás,
así que el arranque son segundos (no milisegundos) y el consumo de memoria en reposo es varias veces
el de `casdoor`. `start-dev` no lleva TLS y guarda todo en memoria — para producción hace falta una
base de datos externa, TLS delante (`caddy`) y `start` en vez de `start-dev`. Y como `casdoor`: la
imagen trae credenciales de administrador que hay que cambiar en el primer minuto, nunca expuesto a
internet sin proxy delante.
