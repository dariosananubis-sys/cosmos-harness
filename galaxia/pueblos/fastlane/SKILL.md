---
cosmos: pueblo
nombre: fastlane
padre: moviles/publicacion
resumen: Automatiza firma, compilacion y subida a las tiendas sea cual sea el framework.
---

https://github.com/fastlane/fastlane · MIT · 42.046★ · último push 2026-08-31 (comprobado por API de GitHub el 2026-09-01).

```bash
brew install fastlane
```

```ruby
# fastlane/Fastfile
default_platform(:ios)

platform :ios do
  desc "Compila y sube a TestFlight"
  lane :beta do
    match(type: "appstore", readonly: true)     # certificados desde un repo git cifrado
    increment_build_number
    gym(scheme: "MiApp", export_method: "app-store")
    pilot(skip_waiting_for_build_processing: true)
  end
end
```

```bash
fastlane init
fastlane beta
fastlane android supply --track internal     # subir a Play Store
```

Es la unica pieza del nicho que no depende del marco elegido: sirve igual para Flutter, React
Native, Expo o nativo puro. Gana a encadenar `xcodebuild` y `bundletool` a mano —la alternativa
real— en la parte que de verdad duele: `match` guarda los certificados y los perfiles de
aprovisionamiento en un repositorio git cifrado, asi que dejan de vivir en el llavero de una persona
concreta. Frente a `bitrise-io/bitrise`, que es un servicio de integracion continua con plan de
pago, este es una biblioteca local sin cuota.

Aviso de dinero **y de calendario** — no lo cobra la herramienta, y es lo que se olvida al dar una
fecha (leido en las paginas de Apple y de Google el 2026-09-01):

- **Apple: 99 USD por ano de miembro.** Si la cuenta va a nombre de la empresa —y va, si el cliente
  factura— Apple exige ademas un **numero D-U-N-S** de la entidad legal durante el alta. Es gratis,
  pero lo emite un tercero y tiene sus propios dias: no se saca la vispera del lanzamiento.
- **Google: 25 USD de alta unica.** Y las cuentas **personales** creadas despues del 13 de noviembre
  de 2023 tienen que pasar un periodo de pruebas cerradas obligatorio y verificar que hay un aparato
  Android real antes de poder publicar nada. Con cuenta de organizacion no aplica. Cuanto dura ese
  periodo lo fija Google en su centro de ayuda y lo ha movido mas de una vez: se mira ANTES de
  comprometer la fecha, no despues.
- **Compilar para iOS exige una maquina macOS.** Los minutos de macOS en las nubes de integracion
  continua son varias veces mas caros que los de Linux y los planes gratuitos los cuentan aparte.

O sea: el presupuesto de publicar en las dos tiendas son 124 USD el primer ano —calderilla al lado de
las horas—, y el plazo lo marcan el D-U-N-S y el periodo de pruebas, que no se aceleran pagando. Esa
es la parte que rompe un compromiso con el cliente.

Y lo que no hace bien: `match` con permiso de escritura puede revocar certificados en uso y dejar al
equipo sin firmar. En cualquier tuberia automatica va con `readonly: true`, y la creacion de
certificados se hace a mano una vez. Los secretos —clave de la API de App Store Connect, JSON de la
cuenta de servicio de Google— nunca en el `Fastfile`: por variable de entorno.
