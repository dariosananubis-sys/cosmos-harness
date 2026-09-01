---
cosmos: pueblo
nombre: react-native
padre: moviles
resumen: Reutiliza conocimiento y ecosistema de React web a cambio de un puente nativo.
---

https://github.com/react/react-native - MIT - 126.472 estrellas - ultimo push 2026-09-01 (comprobado
por API de GitHub el 2026-09-01).

**Ojo con la URL**: el repositorio canonico ya NO es `facebook/react-native` — Meta movio la
organizacion y ese camino responde con una redireccion permanente. Cualquier documento que enlace al
org antiguo esta desactualizado.

```bash
npx @react-native-community/cli init MiApp
cd MiApp && npm install
```

```bash
npm start                 # el empaquetador
npm run ios               # requiere Xcode + cocoapods
npm run android           # requiere Android SDK + un emulador o aparato
```

```jsx
import React, {useState} from 'react';
import {View, Text, Pressable} from 'react-native';

export default function App() {
  const [n, setN] = useState(0);
  return (
    <View style={{flex: 1, alignItems: 'center', justifyContent: 'center'}}>
      <Text style={{fontSize: 48}}>{n}</Text>
      <Pressable onPress={() => setN(n + 1)}><Text>Sumar</Text></Pressable>
    </View>
  );
}
```

Se elige frente a `flutter/flutter` cuando ya hay equipo o codigo en el ecosistema de la web:
reutiliza React, TypeScript y npm entero, a cambio de un puente nativo que Flutter no necesita. Esa
es la frontera con el vecino, y no hay ganador absoluto. Para convertir una web ya hecha en
aplicacion instalable sin reescribir el frontal, `ionic-team/capacitor` (16,5k estrellas, MIT) es la
via corta; no entra como pueblo propio porque es el mismo hueco resuelto por debajo.

Y lo que no hace bien: el puente. Aunque la arquitectura nueva lo reduce, cualquier cosa que cruce
entre JavaScript y nativo muchas veces por segundo —listas largas, animaciones controladas por
gesto— se nota, y la solucion pasa por bibliotecas nativas aparte (`react-native-reanimated`). Y las
actualizaciones de version mayor son famosas por romper dependencias nativas de terceros: presupuestar
la migracion, no improvisarla.

Aviso de dinero: publicar cuesta cuota de desarrollador en las dos tiendas — anual en Apple, alta
unica en Google. La herramienta es gratis; publicar no.

En la practica casi nadie arranca desde aqui a pelo: `expo` pone el andamiaje que si no se monta a
mano.
