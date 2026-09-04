---
cosmos: pueblo
nombre: compose-multiplatform
padre: moviles/marcos
resumen: Comparte logica y pantallas en Kotlin sin renunciar a llamar a la API nativa cuando toca.
---

https://github.com/JetBrains/compose-multiplatform · Apache-2.0 · 19.329★ · último push 2026-09-01
(comprobado por API de GitHub el 2026-09-01). Sobre Kotlin Multiplatform, de JetBrains.

```bash
# el generador oficial deja el esqueleto de Android + iOS + escritorio
open https://kmp.jetbrains.com          # elige objetivos y descarga el proyecto
# o con el asistente de linea de comandos de la version instalada de Kotlin:
brew install kotlin
```

```kotlin
// composeApp/src/commonMain/kotlin/App.kt — una sola pantalla para todos los objetivos
@Composable
fun App() {
    var n by remember { mutableStateOf(0) }
    MaterialTheme {
        Column(Modifier.fillMaxSize(), Arrangement.Center, Alignment.CenterHorizontally) {
            Text("$n", fontSize = 48.sp)
            Button(onClick = { n++ }) { Text("Sumar") }
        }
    }
}

// lo que cambia por plataforma se declara y se implementa aparte, sin puente en ejecucion
expect fun idDelAparato(): String
```

```bash
./gradlew :composeApp:assembleDebug          # Android
./gradlew :composeApp:run                    # escritorio
# iOS: se abre iosApp/iosApp.xcodeproj en Xcode, que sigue haciendo falta
```

Es la tercera respuesta al mismo problema que resuelven `flutter` y `react-native`, y gana en un caso
concreto que los otros dos no cubren bien: **el proyecto ya es Android nativo**. Aquí se empieza
compartiendo solo la lógica —red, base de datos, reglas de negocio— y se deja la interfaz de cada
plataforma como está; la pantalla compartida se adopta después, o nunca. Frente a `flutter`, que dibuja
sus propios controles con motor propio, y frente a `react-native`, que cruza un puente de JavaScript en
ejecución, aquí se compila a código nativo de cada plataforma y llamar a una API del sistema es
`expect`/`actual`, no un módulo puente que alguien tiene que escribir en Swift.

Y lo que no hace bien:

- **iOS es el objetivo más joven.** La interfaz compartida en iOS lleva menos rodaje que en Android, y
  el desplazamiento y los gestos no se sienten idénticos a los de SwiftUI: para una app en la que la
  sensación nativa de iOS es el producto, sigue ganando escribir esa pantalla en Swift.
- **Gradle es lo que aprieta, no el marco**: el demonio de compilación más Android Studio más el
  simulador de iOS agotan la memoria libre de un portátil de desarrollo normal si van los tres a
  la vez. Un solo entorno abierto por sesión.
- **El ecosistema de bibliotecas compartidas es mucho más pequeño** que el de npm o el de pub.dev:
  bastante cosa hay que envolver a mano por plataforma, y eso es tiempo que en el presupuesto no
  aparece.
- **Compilar y firmar para iOS sigue exigiendo un Mac con Xcode**, y publicar sigue costando cuota de
  desarrollador en las dos tiendas — el calendario y las cifras están en `fastlane`.
