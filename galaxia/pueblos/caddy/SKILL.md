---
cosmos: pueblo
nombre: caddy
padre: infraestructura/servidores
resumen: Proxy inverso que saca y renueva el certificado solo, con configuracion de tres lineas.
---

https://github.com/caddyserver/caddy · Apache-2.0 · 75.379★ · push 2026-08-31 (comprobado 2026-09-01)

```bash
brew install caddy

cat > Caddyfile <<'CADDY'
ejemplo.test {
    reverse_proxy localhost:8080
    encode zstd gzip
}
CADDY

caddy validate --config Caddyfile
caddy run --config Caddyfile
```

Gana a `nginx` y a `traefik` por lo mismo: el certificado de Let's Encrypt se saca y se renueva **por
comportamiento por defecto**, no como añadido que hay que recordar. Un certificado caducado es una
caída, y la caída de certificado siempre pasa el domingo. `nginx` necesita `certbot` y su cron
aparte; `traefik` lo trae pero a cambio de una configuración por etiquetas mucho más larga para el
caso simple de un proxy delante de un servicio.

Ojo: para emitir certificado necesita el puerto 80 y 443 accesibles desde fuera y el DNS ya
apuntando. Detrás de otro proxy o de un cortafuegos, el reto HTTP falla en silencio y sirve el
certificado interno de Caddy — el navegador avisa, el registro casi no. En ese caso, reto por DNS
con el módulo del proveedor, que exige recompilar con `xcaddy`.
