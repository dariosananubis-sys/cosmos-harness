# Móviles — apps para móvil y escritorio

Barrido GitHub para COSMOS. Nicho `moviles` (#8 de 20, `UNIVERSO.md`): desarrollo nativo y
multiplataforma, ciclo de vida y publicación en tiendas, notificaciones, almacenamiento local y
sincronización, rendimiento/batería, pruebas en dispositivo, distribución interna. Su propio código
vive dentro (país `codigo-nativo` y `codigo-multiplataforma`), no en una capa aparte.

Método: API de GitHub autenticada (`search/repositories`, ordenado por estrellas) sobre las 11
consultas del encargo (flutter, react native, tauri, swiftui, jetpack compose, fastlane, mobile ci
cd, app store deployment, mobile testing framework, offline first sync, expo) + lookups directos
(`/repos/{owner}/{repo}`) para completar huecos que la búsqueda por frase no cubría bien (bases de
datos offline, distribución interna, testing). Estrellas/licencia/`pushed_at` en vivo,
2026-09-01. Las listas «awesome» que aparecieron en la búsqueda (awesome-flutter,
awesome-react-native, open-source-ios-apps…) se usaron solo para descubrir candidatos — no entran
como recurso, tal y como pide el filtro.

**Aviso de coste, antes de nada**: nada de lo de abajo cuesta dinero para desarrollar. Pero
**publicar** sí: Apple Developer Program son ~99 $/año (obligatorio para subir a la App Store o
probar en un iPhone físico más de 7 días) y Google Play Console son ~25 $ únicos. Cifras de memoria,
ampliamente conocidas, **no verificadas en vivo hoy** — confirmar en developer.apple.com y
play.google.com/console antes de presupuestar a cliente.

**Aviso de máquina**: Xcode + simulador iOS y Android Studio + emulador + demonio Gradle son pesados
en un Mac de 8 GB — cada uno por separado va bien, los dos abiertos a la vez con VS Code detrás
aprieta. Recomendado: un solo IDE nativo abierto por sesión, dispositivo físico en vez de emulador
cuando se pueda, y cerrar el simulador al terminar.

---

## De primera

Máximo 10. Elegidos por: se ejecuta de verdad, cero coste para desarrollar, vivo, y cuando dos
herramientas compiten por el mismo hueco (Flutter/React Native) se explica cuándo gana cada una en
vez de forzar un único ganador.

1. **[Flutter](https://github.com/flutter/flutter)** — 178.7k★, BSD-3-Clause, activo (push de hoy).
   **Por qué gana su hueco**: un solo código Dart compila a binario nativo real en iOS, Android,
   web, Windows, macOS y Linux — no interpreta ni pasa por un puente JS en tiempo de ejecución, así
   que el rendimiento se acerca más a nativo que el de React Native. Mecanismo: motor gráfico propio
   (Skia/Impeller) que dibuja cada píxel, sin depender de los widgets del sistema operativo.

2. **[React Native](https://github.com/react/react-native)** — 126.5k★, MIT, activo. **Nota rara**:
   el repo canónico ya NO vive en `facebook/react-native` (devuelve 404) sino en `react/react-native`
   — Meta movió el org de GitHub; si algo enlaza al org antiguo, está desactualizado. **Por qué gana
   su hueco frente a Flutter**: cuando el equipo o el cliente ya tiene código/talento en
   JS/TypeScript/React web, reutiliza ese conocimiento y el ecosistema npm entero, a cambio de un
   puente nativo que Flutter no necesita. Regla práctica: equipo JS o quiere reusar una web React →
   React Native; rendimiento máximo o cero deuda de puente → Flutter.

3. **[Tauri](https://github.com/tauri-apps/tauri)** — 110.7k★ (contando apps hechas con Tauri que
   apuntan al framework, el propio repo con mayor tracción del ecosistema), Apache-2.0, activo.
   **Por qué gana**: apps de escritorio (y creciendo en móvil desde v2) usando el motor web nativo
   del sistema operativo en vez de empaquetar un Chromium entero como Electron — binarios de unos
   pocos MB frente a 100+ MB, y RAM muy por debajo. Es la opción correcta en un Mac de 8 GB para
   cualquier app de escritorio que antes se haría con Electron.

4. **[Expo](https://github.com/expo/expo)** — 51.9k★, MIT, activo. **Por qué gana su propio hueco
   (no compite con React Native, lo completa)**: capa gestionada sobre React Native con hot reload,
   OTA updates (EAS Update) y build/submit en la nube (EAS Build/Submit). **Coste**: el SDK y el
   desarrollo local son gratis; EAS Build/Submit en la nube tiene un plan gratuito limitado
   (cola compartida, pocos builds/mes) y sube de precio a partir de ahí — para una agencia que
   publica pocas apps al mes el gratuito suele bastar.

5. **[Fastlane](https://github.com/fastlane/fastlane)** — 42.0k★, MIT, activo. **Por qué gana**: es
   el estándar de facto para automatizar build+firma+subida a App Store/Play Store sin depender de
   ningún framework concreto (sirve igual para Flutter, RN o nativo puro). Mecanismo: `Fastfile` en
   Ruby con "lanes" que encadenan `gym`/`match`/`supply`/`deliver`; corre en cualquier runner macOS
   (los de GitHub Actions incluyen minutos gratis limitados — el build de iOS solo puede correr en
   macOS, es la única pieza que no se evita).

6. **[Capacitor](https://github.com/ionic-team/capacitor)** — 16.5k★, MIT, activo (Ionic Team). **Por
   qué gana frente a Cordova** (su predecesor directo, `apache/cordova-android`, con mucho menos
   ritmo de commits): puente nativo moderno con soporte de WebView nativo del sistema y API de
   plugins más simple. Encaja bien con el perfil de agencia: convierte una web ya hecha en app
   nativa instalable sin reescribir el frontend.

7. **[Ionic Framework](https://github.com/ionic-team/ionic-framework)** — 52.6k★, MIT, activo.
   **Por qué gana su hueco propio**: componentes UI con aspecto nativo (iOS/Android/web) construidos
   en HTML/CSS/JS estándar — la pareja natural de Capacitor (Capacitor pone el puente nativo, Ionic
   pone la interfaz) cuando no se quiere depender de React Native/Flutter para una app sencilla.

8. **[RxDB](https://github.com/pubkey/rxdb)** — 23.4k★, Apache-2.0, activo (push de hoy). **Por qué
   gana frente a WatermelonDB y Realm**: funciona en cualquier runtime JS (RN, web, Node), es
   "local-first" de raíz — la app lee/escribe siempre local y replica en segundo plano contra
   cualquier backend existente, sin vendor lock-in. WatermelonDB (11.8k★, MIT, sin push desde
   ago-2025 — más parado) sigue siendo mejor opción específica cuando el dataset es enorme y hace
   falta *lazy loading* fila a fila en React Native puro; se cita en segunda fila.

9. **[Detox](https://github.com/wix/Detox)** — 12.0k★, MIT, activo (Wix). **Por qué gana su hueco**:
   testing E2E "gray box" hecho a medida para React Native/Expo — sincroniza automáticamente con el
   hilo de JS y las animaciones nativas (evita los `sleep()` frágiles de Appium/WebdriverIO).
   WebdriverIO (9.8k★, más genérico, cubre también web) queda en segunda fila para cuando el mismo
   test tiene que correr también en navegador.

10. **[MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF)** — 21.7k★, GPL-3.0, activo.
    **Por qué gana**: análisis de seguridad automatizado (estático y dinámico) de un APK/IPA/AAB en
    un solo comando — útil antes de aceptar un SDK de terceros o un plugin de push en una app de
    cliente, sin depender de un servicio de pago. Encaja con el mar `custodia` del universo COSMOS
    (nunca secretos/datos personales de más).

---

## Segunda fila

- **[NativeScript](https://github.com/NativeScript/NativeScript)** — 25.6k★, MIT. Acceso directo a
  las APIs nativas desde JS/TS sin puente (arquitectura distinta a RN); usar cuando el rendimiento de
  RN se queda corto pero reescribir a Flutter no compensa.
- **[Dioxus](https://github.com/DioxusLabs/dioxus)** — 38.9k★, Apache-2.0. Framework Rust "fullstack"
  para web/escritorio/móvil con sintaxis tipo React; emergente, para equipos que ya trabajan en Rust
  (p. ej. si el motor de juegos del nicho `juegos` ya usa Bevy).
- **[WatermelonDB](https://github.com/Nozbe/WatermelonDB)** — 11.8k★, MIT, último push ago-2025 (más
  de un año) — vigilar que no se archive. Base offline-first construida específicamente para React
  Native con SQLite y *lazy loading*; mejor que RxDB cuando el dataset es grande y solo en RN.
- **[Realm](https://github.com/realm/realm-swift)** (+ [realm-kotlin](https://github.com/realm/realm-kotlin)) —
  16.6k★ / 1.1k★, Apache-2.0. Base de datos embebida nativa madura (ahora MongoDB Atlas Device SDK);
  el SDK local es gratis, la sincronización en la nube de Atlas es el producto de pago —usar solo la
  parte local si no se quiere esa dependencia.
- **[PowerSync](https://github.com/powersync-ja/powersync-js)** — 720★, Apache-2.0. SQLite
  embebido + sync en tiempo real contra Postgres/Supabase existente; más joven que RxDB, interesante
  si el backend ya es Postgres.
- **[Tuist](https://github.com/tuist/tuist)** — 5.8k★. Generación y gestión de proyectos Xcode desde
  config declarativa — evita los conflictos de merge eternos de `.pbxproj` en equipo.
- **[Bitrise CLI](https://github.com/bitrise-io/bitrise)** — 897★, MIT. El runner de Bitrise se
  puede ejecutar en local/self-hosted gratis; el producto Bitrise Cloud (con macOS a demanda) es de
  pago — usar el CLI en un runner propio evita esa factura.
- **[Zealot](https://github.com/tryzealot/zealot)** — 1.4k★, MIT, activo. Distribución interna de
  builds (alternativa self-hosted a TestFlight interno/Firebase App Distribution) para que el
  cliente pruebe una beta sin pasar por la tienda.
- **[OneSignal Android SDK](https://github.com/OneSignal/OneSignal-Android-SDK)** — push
  notifications con plan gratuito generoso; para no depender de él, Expo trae `expo-notifications`
  integrado sin coste adicional cuando ya se usa Expo.
- **[Sentry React Native](https://github.com/getsentry/sentry-react-native)** — 1.8k★, MIT. Crash
  reporting; el SaaS de Sentry tiene capa gratuita, el self-hosted completo (`getsentry/self-hosted`)
  exige Postgres+Redis+ClickHouse — desproporcionado para una sola app de cliente.

## Humo

- **[TCA](https://github.com/pointfreeco/swift-composable-architecture)** — arquitectura de estado
  para apps SwiftUI, cuando el `@State` a pelo se queda corto.
- **[react-native-reanimated](https://github.com/software-mansion/react-native-reanimated)** —
  animaciones que corren en el hilo de UI nativo, no en el hilo de JS.
- **[react-native-web](https://github.com/necolas/react-native-web)** — el mismo código RN
  renderizado como web, para compartir componentes entre app y sitio.
- **[compose-samples](https://github.com/android/compose-samples)** — ejemplos oficiales de Google
  de Jetpack Compose (Compose en sí no es un repo independiente, va dentro de AndroidX).
- **[Danger](https://github.com/danger/danger)** — bot de revisión de PR (checklist automático:
  "¿falta el CHANGELOG?") útil en cualquier repo de app.
- **[WebdriverIO](https://github.com/webdriverio/webdriverio)** — E2E web+móvil vía Appium, cuando
  el mismo test debe correr en navegador y en la app.
- **apache/cordova-android** — el hybrid-app original; en desuso frente a Capacitor, se cita solo
  porque aún hay apps de cliente heredadas sobre él.

---

## Mapeo a COSMOS

```
sistema-solar  moviles
├── continente  desarrollo-nativo
│   ├── pais  ios                     provincias: UI declarativa (SwiftUI) · arquitectura (TCA)
│   ├── pais  android                 provincias: UI declarativa (Jetpack Compose) · ejemplos oficiales
│   └── pais  codigo-nativo           ← su propio código vive aquí
│              provincias: patrones Swift/Kotlin · testing en dispositivo físico
├── continente  desarrollo-multiplataforma
│   ├── pais  frameworks-app          provincias: Flutter · React Native · NativeScript · Dioxus
│   ├── pais  hibrido-web-a-app       provincias: Capacitor · Ionic Framework · Cordova (legado)
│   ├── pais  escritorio-ligero       provincias: Tauri
│   └── pais  codigo-multiplataforma  ← y aquí
│              provincias: gestión de estado · puentes nativos · componentes compartidos
├── continente  ciclo-de-vida-y-publicacion
│   ├── pais  ci-cd-movil             provincias: Fastlane · Tuist · Bitrise CLI self-hosted
│   └── pais  distribucion            provincias: tiendas (coste €) · Zealot (interna) · EAS Update (OTA)
└── continente  datos-y-calidad
    ├── pais  almacenamiento-local-y-sync   provincias: RxDB · WatermelonDB · Realm · PowerSync
    ├── pais  notificaciones                provincias: OneSignal · expo-notifications
    └── pais  pruebas-en-dispositivo         provincias: Detox · WebdriverIO · MobSF (seguridad)
```

Los mares del universo (`criterio`, `pruebas`, `resistencia`, `accesibilidad`, `custodia`) mojan
este nicho igual que a los otros 19: nadie los invoca a mano, pero MobSF y el testing E2E son donde
más se nota `pruebas` y `custodia` en concreto.

## Lo que falta

- **Ninguna herramienta de esta lista se ha probado en vivo hoy** (regla 5 del filtro, "se ha usado
  una vez") — esto es un barrido de metadata GitHub (estrellas/licencia/actividad), no una prueba de
  campo. Antes de adoptar una para un cliente, un `flutter create` / `npx create-expo-app` real.
- **iOS exige macOS sí o sí** para compilar y firmar — no hay forma de evitarlo con ninguna
  herramienta gratuita; Fastlane/Tuist automatizan el proceso pero no eliminan la dependencia de
  tener un Mac (que ya se tiene) o pagar minutos de CI macOS.
- **No apareció un ganador claro para "mobile ci cd" 100% gratis y maduro** buscando la frase
  literal — la pieza real que resuelve esto es Fastlane + runners macOS gratuitos limitados de
  GitHub Actions, no un producto dedicado sin coste.
- **CodePush** (`microsoft/react-native-code-push`, 9.1k★) apareció con fuerza pero está **archivado**
  (`archived: true`, sin commits desde may-2025) — no se incluye como "de primera" a propósito; el
  sustituto vivo es EAS Update, con las limitaciones de cuota gratuita ya dichas.
