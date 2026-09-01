---
cosmos: pueblo
nombre: ntfy
padre: infraestructura/vigilancia
resumen: Envia la alerta al movil por HTTP simple, sin cuenta de terceros ni aplicacion cerrada.
---

https://github.com/binwiederhier/ntfy · Apache-2.0 · 33.923★ · push 2026-08-27 (comprobado 2026-09-01)

```bash
brew install ntfy          # trae cliente y servidor

# servidor propio
ntfy serve --listen-http :2586

# publicar desde cualquier guion: una peticion HTTP, sin biblioteca
curl -s -d "Copia nocturna terminada" \
  -H "Title: copias" -H "Priority: high" -H "Tags: warning" \
  http://localhost:2586/mi-canal
```

Una alerta que no llega no existe. Gana a `Gotify`, el otro autoalojado del hueco, porque publicar es
una petición HTTP de una línea sin cabecera de autenticación obligatoria ni SDK: se engancha a un
`cron`, a un `Caddyfile`, a un manejador de error de `celery` o a `uptime-kuma` sin integración
específica. Y gana a Pushover o Telegram porque no hay cuenta de terceros de por medio ni un servicio
que pueda cerrar el grifo.

Frontera con `aviso-por-chat`: aquel llega a la herramienta donde el equipo ya está; este llega al
móvil de quien se suscribe, aunque no tenga cuenta de nada.

Ojo: un canal sin control de acceso **es público para quien adivine su nombre**, y en la instancia
pública lo es para quien lo teclee. Para avisos con datos, servidor propio con `auth-default-access:
deny-all` y credenciales por canal. Y la entrega inmediata en iOS depende del servicio de
notificaciones de Apple: con servidor propio hay que configurar el reenvío a la instancia pública o
aceptar que el aviso llega cuando se abre la aplicación.
