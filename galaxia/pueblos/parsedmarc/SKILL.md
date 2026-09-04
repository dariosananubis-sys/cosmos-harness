---
cosmos: pueblo
nombre: parsedmarc
padre: entregabilidad/autenticacion
resumen: Convierte los informes DMARC que llegan por correo en filas que se pueden mirar, y descubre quien envia en tu nombre.
---

https://github.com/domainaware/parsedmarc · Apache-2.0 · 1.291★ · último push 2026-09-03 (comprobado
2026-09-04, API de GitHub y `commits/HEAD.atom`: HEAD 2026-09-03T19:51Z; no archivado)

```bash
pip install parsedmarc
```

```bash
# un informe suelto que alguien te reenvio: sin configurar nada, sale JSON por la salida estandar
parsedmarc informe-dmarc.xml.gz

# la forma util: vaciar el buzon de informes cada dia
cat > parsedmarc.ini <<'CFG'
[imap]
host = imap.PROVEEDOR.invalid
user = BUZON-DE-INFORMES
password = "<contrasena-de-aplicacion>"
[mailbox]
watch = True
delete = False
CFG
parsedmarc -c parsedmarc.ini
```

Gana a leer el XML a mano —que es lo que hace todo el mundo el primer mes— en que agrega los
informes de todos los receptores y deja el resultado en JSON o CSV con el nombre del proveedor
resuelto por IP. La pregunta que contesta y que no contesta nada más: **qué servidores están
enviando correo con tu dominio en el remitente**, incluyendo el proveedor de facturación que alguien
dio de alta hace dos años y nunca se declaró en el SPF.

Frontera con `checkdmarc`: aquel valida la configuración publicada antes de enviar; este lee lo que
el mundo responde después. El camino real es `checkdmarc` para publicar `p=none` bien formado,
`parsedmarc` durante unas semanas para descubrir a todos los que envían de verdad, y solo entonces
subir la política a `quarantine` o `reject`.

Ojo, y es la razón de que muchos dominios se queden en `p=none` para siempre: los informes
**agregados** dicen cuántos mensajes pasaron o fallaron por dirección IP, no qué mensaje era ni a
quién iba. Los informes **forenses**, que sí traen la cabecera, casi nadie los manda por privacidad,
así que investigar un fallo concreto normalmente no se puede.

Ojo de credenciales: el modo útil necesita entrar en un buzón. Las cadenas de arriba son marcadores
y se rellenan con una contraseña de aplicación de un buzón dedicado **solo** a recibir informes,
nunca con la del correo personal, y el fichero `.ini` no se commitea.
