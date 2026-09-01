---
cosmos: pueblo
nombre: zaproxy
padre: ciberseguridad/ofensiva/explotacion
resumen: Proxy que intercepta y reescribe peticiones a mano, lo que ninguna plantilla automatiza.
---

https://github.com/zaproxy/zaproxy · Apache-2.0 · 15.715★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
brew install --cask zap
```

```bash
# escaneo automático de línea base contra un objetivo del alcance, con informe
zap.sh -cmd -quickurl https://OBJETIVO-DEL-ALCANCE/ -quickout ./informe-zap.html

# como proxy para tocar a mano: apuntar el navegador a este puerto
zap.sh -daemon -host 127.0.0.1 -port 8080
```

Es la respuesta libre a la suite comercial de proxy de pago (Burp Suite Pro): intercepta, reescribe
y repite peticiones **a mano**, que es lo que ninguna plantilla automatiza. Frontera con el escáner
de plantillas `nuclei`: allí se automatiza lo conocido a escala, aquí se toca lo que ninguna
plantilla describe.

Ojo: su escáner **activo** manda cargas de ataque reales contra el objetivo (puede crear registros,
disparar correos, corromper datos de prueba) — se lanza solo dentro del alcance y sobre entorno de
pruebas, nunca a ciegas sobre producción. El escaneo de línea base (`-quickurl`) es pasivo y seguro;
el activo (`zap-full-scan`) no. Y para una aplicación de una sola página que carga por JavaScript, su
araña clásica ve poco: hay que usar la araña con navegador para que descubra la superficie real.
