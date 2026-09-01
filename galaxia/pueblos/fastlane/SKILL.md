---
cosmos: pueblo
nombre: fastlane
padre: moviles
resumen: Automatiza firma, compilacion y subida a las tiendas sea cual sea el framework.
---

https://github.com/fastlane/fastlane - MIT - 42.046 estrellas - ultimo push 2026-08-31 (comprobado
por API de GitHub el 2026-09-01).

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

Aviso de dinero que no cuesta la herramienta: publicar exige cuenta de desarrollador de pago en las
dos tiendas — cuota anual en Apple, alta unica en Google. Y compilar para iOS exige una maquina
macOS: los minutos de macOS en las nubes de integracion continua son varias veces mas caros que los
de Linux, y los planes gratuitos los cuentan aparte.

Y lo que no hace bien: `match` con permiso de escritura puede revocar certificados en uso y dejar al
equipo sin firmar. En cualquier tuberia automatica va con `readonly: true`, y la creacion de
certificados se hace a mano una vez. Los secretos —clave de la API de App Store Connect, JSON de la
cuenta de servicio de Google— nunca en el `Fastfile`: por variable de entorno.
