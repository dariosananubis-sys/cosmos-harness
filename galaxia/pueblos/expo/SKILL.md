---
cosmos: pueblo
nombre: expo
padre: moviles
resumen: Capa gestionada sobre React Native: recarga en caliente, actualizaciones por aire y firma sin cadena local.
---

https://github.com/expo/expo - MIT - 51.948 estrellas - ultimo push 2026-09-01 (comprobado por API
de GitHub el 2026-09-01).

```bash
npx create-expo-app@latest MiApp
cd MiApp && npm install
npm install -g eas-cli        # solo si vas a compilar en su nube
```

```bash
npx expo start                # abre en Expo Go, en el aparato fisico, sin cadena local
npx expo run:ios              # compilacion nativa local, requiere Xcode
eas build --platform android --profile preview     # en su nube
eas update --branch production                     # actualizacion por radio
```

No compite con `react/react-native`, lo completa: le pone el andamiaje —enrutado por ficheros,
recarga en caliente, acceso a camara, notificaciones, actualizaciones— que de otro modo se monta a
mano pieza a pieza. Lo que de verdad cambia el trabajo es la actualizacion por radio: corregir un
fallo de JavaScript sin volver a pasar por la revision de la tienda, que son dias.

Lo que cuesta dinero, dicho claro y separado en dos:

- **De Expo**: el kit y el desarrollo local son gratis. `eas build` y `eas submit` en su nube tienen
  un plan gratuito con cola compartida y pocas compilaciones al mes; a partir de ahi se paga por
  suscripcion. Para publicar de vez en cuando llega; para un ritmo alto, no. Alternativa a coste
  cero: `npx expo run:ios` / `run:android` compilan en tu maquina, que es gratis pero exige Xcode y
  el SDK de Android instalados.
- **De las tiendas, que no es de Expo**: cuota anual de desarrollador en Apple y alta unica en
  Google. Sin eso no se publica, con Expo o sin el.

Y lo que no hace bien: la actualizacion por radio solo alcanza al JavaScript y a los activos. Si el
cambio toca codigo nativo —una biblioteca nueva, un permiso, la version del SDK— hay que compilar y
volver a pasar por la tienda. Prometer "lo arreglamos sin pasar por revision" sin comprobar si el
cambio es nativo es el falso verde de este pueblo.
