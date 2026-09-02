---
cosmos: pueblo
nombre: flutter
padre: moviles
resumen: Un solo codigo compilado a binario nativo que dibuja cada pixel con su propio motor.
---

https://github.com/flutter/flutter · BSD-3-Clause · 178.735★ · último push 2026-09-01 (comprobado 2026-09-01)
(comprobado por API de GitHub el 2026-09-01).

```bash
brew install --cask flutter
flutter doctor          # dice exactamente que falta (Xcode, cocoapods, Android SDK)
```

```bash
flutter create mi_app && cd mi_app
flutter devices
flutter run -d chrome              # sin simulador, para ver que arranca
flutter run -d "iPhone 15"         # requiere Xcode instalado
flutter build apk --release
```

```dart
import 'package:flutter/material.dart';

void main() => runApp(const MaterialApp(home: Contador()));

class Contador extends StatefulWidget {
  const Contador({super.key});
  @override State<Contador> createState() => _ContadorState();
}
class _ContadorState extends State<Contador> {
  int n = 0;
  @override Widget build(BuildContext c) => Scaffold(
    body: Center(child: Text('$n', style: const TextStyle(fontSize: 48))),
    floatingActionButton: FloatingActionButton(
      onPressed: () => setState(() => n++), child: const Icon(Icons.add)),
  );
}
```

Se elige frente a `react/react-native` cuando manda el rendimiento o no se quiere deuda de puente:
un solo codigo Dart compila a binario nativo real y el motor grafico propio (Impeller) dibuja cada
pixel, sin interpretar ni cruzar un puente en tiempo de ejecucion. La frontera con el vecino no
tiene ganador absoluto: equipo que ya vive en JS/TypeScript o que quiere reusar una web React ->
React Native; rendimiento maximo o cero deuda de puente -> aqui.

Y lo que no hace bien: como dibuja sus propios controles en vez de usar los del sistema, la
accesibilidad, el teclado, el texto seleccionable y las convenciones de cada plataforma hay que
cuidarlas a mano, y una actualizacion de iOS que cambia el aspecto de un control no llega gratis. El
tamano minimo del binario tambien es mayor que el de una app nativa equivalente.

Aviso de dinero, que no es de la herramienta: publicar cuesta cuota de desarrollador — Apple cobra
una cuota anual y Google una alta unica. Compilar para iOS ademas exige un Mac con Xcode; no hay
manera de esquivarlo.

Aviso de maquina: `flutter doctor` completo con Xcode y el SDK de Android son decenas de gigas de
disco. En un Mac de 8 GB corre, pero el simulador de iOS y el emulador de Android a la vez, no.
