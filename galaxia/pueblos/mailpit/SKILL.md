---
cosmos: pueblo
nombre: mailpit
padre: entregabilidad
resumen: Servidor SMTP de pruebas con bandeja web: se queda todo lo que envia la aplicacion y no sale nada fuera.
---

https://github.com/axllent/mailpit · MIT · 10.273★ · último push 2026-09-03 (comprobado 2026-09-04,
API de GitHub y `commits/HEAD.atom`: HEAD 2026-09-03T05:08Z; no archivado)

```bash
brew install mailpit          # o: go install github.com/axllent/mailpit@latest
mailpit                       # SMTP en :1025, interfaz web en http://localhost:8025
```

```bash
# la aplicacion apunta ahi y no hace falta ninguna cuenta
export SMTP_HOST=localhost SMTP_PORT=1025

# comprobar desde fuera que captura, sin escribir codigo
python3 -c "import smtplib; from email.message import EmailMessage; m=EmailMessage(); \
m['From']='app@ejemplo.invalid'; m['To']='destino@ejemplo.invalid'; m['Subject']='prueba'; \
m.set_content('hola'); smtplib.SMTP('localhost',1025).send_message(m)"

# la bandeja tiene API: se puede afirmar en una prueba de integracion
curl -s http://localhost:8025/api/v1/messages | python3 -m json.tool | head
```

Releva a `MailHog`, que fue el estándar de este hueco y lleva sin mantenimiento desde 2020: mismo
concepto —un SMTP que no reenvía nada— con interfaz nueva, búsqueda, vista de HTML y texto lado a
lado, comprobación de compatibilidad del HTML con los clientes de correo y una puntuación de spam
con SpamAssassin si se le conecta uno. Y es un binario único en Go, sin dependencias.

Frontera con `checkdmarc` y `parsedmarc`, que están en el mismo oficio: `mailpit` es el único que
mira **lo que la aplicación envía**; aquellos miran lo que el mundo dice de tu dominio. Los tres
hacen falta y ninguno sustituye a otro.

Ojo, y es la trampa: que un mensaje se vea perfecto aquí **no dice nada** sobre si llegaría a una
bandeja real. No hay reputación, ni SPF, ni filtro de spam del receptor: es un buzón que acepta todo.
Un despliegue que pasa las pruebas contra `mailpit` puede acabar íntegro en la carpeta de correo no
deseado.

Ojo de exposición: sin `--listen 127.0.0.1:8025` la interfaz web escucha en todas las direcciones y
**no pide contraseña** — cualquiera de la red lee los correos capturados, que en desarrollo suelen
llevar enlaces de restablecer contraseña de verdad.
