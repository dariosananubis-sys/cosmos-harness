---
cosmos: pueblo
nombre: correo-smtp
padre: automatizacion/avisos
resumen: Envia correo por su protocolo y ademas lo copia a Enviados, que muchos proveedores no hacen por su cuenta.
---

`scripts/enviar-correo-smtp.py` — herramienta propia, no hay repositorio público. La ruta ES la
referencia.

```bash
# credenciales en ~/.secrets/mail-cuenta.env: MAIL_EMAIL, MAIL_PASSWORD,
# MAIL_SMTP_HOST, MAIL_SMTP_PORT, MAIL_SMTP_ENC, MAIL_IMAP_*   (nunca en el repo)

python3 scripts/enviar-correo-smtp.py \
  --to persona@ejemplo.test --cc otra@ejemplo.test \
  --asunto "Informe mensual" \
  --cuerpo-fichero cuerpo.txt \
  --adjunto "/ruta/Informe.pdf" \
  --dry-run          # prepara el mensaje y NO lo envia; quitalo para enviar de verdad
```

Se prefiere a `smtplib` a pelo y al nodo de correo de `n8n` por el segundo paso, que es su razón de
existir: **después de enviar, sube una copia a la carpeta de Enviados por IMAP**. Un correo mandado
por programa llega al destinatario y no aparece en Enviados de quien lo manda; el efecto es que
nadie en la casa sabe que se envió y el hilo se contesta dos veces. Ningún motor de flujos de este
nicho lo hace: integran servicios y dan por hecho que el correo sale de otro sitio.

Ojo: las cuentas con doble factor necesitan contraseña de aplicación, no la del usuario. Y `--dry-run`
es el modo por defecto recomendado al probar: sin él, el envío es inmediato y no hay deshacer.

A las tres de la mañana: **no reintenta y no tiene cola**. Si el servidor rechaza o la red falla,
sale con error y el correo no se envía; nadie lo reencola. Para envíos desatendidos o masivos, va
detrás de `celery` con `autoretry_for` — no suelto en un `cron`.
