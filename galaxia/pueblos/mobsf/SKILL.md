---
cosmos: pueblo
nombre: mobsf
padre: moviles
resumen: Analiza el paquete ya compilado y dice que permisos, claves y trafico lleva dentro de verdad.
---

https://github.com/MobSF/Mobile-Security-Framework-MobSF · GPL-3.0 · 21.679★ · último push 2026-08-27
(comprobado por API de GitHub el 2026-09-01)

```bash
docker run -d --name mobsf -p 8000:8000 opensecurity/mobile-security-framework-mobsf:latest
# la clave de API sale del log del contenedor la primera vez; NUNCA se escribe en un fichero del repo
docker logs mobsf | grep -i "REST API Key"
```

```bash
# analisis estatico por API, que es como se mete en una tuberia
CLAVE="<CLAVE_DE_LA_API_LOCAL>"
HASH=$(curl -s -F "file=@app.apk" -H "Authorization: $CLAVE" \
        http://localhost:8000/api/v1/upload | python3 -c "import sys,json;print(json.load(sys.stdin)['hash'])")
curl -s -X POST -d "hash=$HASH" -H "Authorization: $CLAVE" http://localhost:8000/api/v1/scan > informe.json
curl -s -X POST -d "hash=$HASH" -H "Authorization: $CLAVE" http://localhost:8000/api/v1/download_pdf -o informe.pdf
```

Mira el artefacto que de verdad se sube a la tienda —el APK, el AAB o el IPA— y no el código fuente,
que es la diferencia que importa: ahí dentro está lo que metieron las dependencias, no solo lo que
escribió el equipo. Saca los permisos declarados, las claves y URL incrustadas, la configuración de
seguridad del tráfico, los componentes exportados y las bibliotecas de terceros con su versión.

Es la pieza que responde a la pregunta real de una agencia antes de firmar: **qué se lleva ese kit de
publicidad o de notificaciones que pidió el cliente**. Gana a leer el manifiesto a mano con
`aapt dump badging`, que es la alternativa, porque aquel enseña los permisos y ya; y gana a un analizador
de código estático corriente porque este ve el binario final, con lo empaquetado dentro.

Toca directamente el agua de custodia del universo: una clave de API incrustada en un APK es pública
el día que se publica, y aquí sale con su fichero y su línea.

Y lo que no hace bien:

- **El análisis dinámico necesita un emulador Android con root o un aparato preparado**, y no está
  incluido en la imagen. Todo lo de arriba es análisis estático, que es el 90 % del valor y el 10 % del
  montaje.
- **Devuelve muchos hallazgos y bastantes son ruido**: cada uso de criptografía sale marcado aunque sea
  correcto. Sin alguien que triaje, el informe se archiva sin leer.
- **Licencia GPL-3.0**: usarlo para auditar es libre; empotrarlo dentro de un producto que se
  distribuye, no sin consecuencias.
- **La clave de la API se genera al arrancar y sale en el log.** No se guarda en el repositorio ni se
  pasa por la línea de comandos en una máquina compartida, y el servicio nunca se expone fuera de la
  máquina: quien lo alcance puede subir y descargar los binarios de cualquier cliente.
