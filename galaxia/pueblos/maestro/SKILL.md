---
cosmos: pueblo
nombre: maestro
padre: moviles
resumen: Prueba la aplicacion en el aparato con flujos en YAML que esperan solos, sin importar el marco.
---

https://github.com/mobile-dev-inc/Maestro · Apache-2.0 · 15.473★ · último push 2026-08-31 (comprobado
por API de GitHub el 2026-09-01)

```bash
brew tap mobile-dev-inc/tap && brew install maestro
```

```yaml
# .maestro/entrar.yaml
appId: <IDENTIFICADOR_DE_LA_APP>
---
- launchApp:
    clearState: true
- tapOn: "Entrar"
- inputText: "usuario@ejemplo.test"
- tapOn:
    id: "campo_password"
- inputText: "<CLAVE_DE_PRUEBAS>"
- tapOn: "Continuar"
- assertVisible: "Mis pedidos"          # espera sola: no hace falta ningun sleep
- takeScreenshot: entrada-ok
```

```bash
maestro test .maestro/          # sale distinto de cero si una asercion falla
maestro studio                  # graba el flujo tocando la pantalla y escribe el YAML
```

Cierra el hueco más grande que tenía este oficio: no había ninguna forma de comprobar que la
aplicación funciona de verdad en el aparato. Y la pieza que lo hace usable es la **espera implícita**:
cada orden reintenta hasta que el elemento aparece, así que desaparecen los `sleep` a ojo que hacen que
una prueba de móvil falle un día sí y otro no.

Gana a `wix/Detox` (12.022★), que es el rival directo y el que recomienda casi todo el mundo, en
alcance: aquel es específico de React Native —enlaza con su hilo de JavaScript, y ahí es
excelente— mientras que esto habla con la pantalla, así que el **mismo flujo** vale para Flutter, para
React Native, para Expo y para una app nativa. En una agencia que no usa siempre el mismo marco, esa es
la diferencia. Y gana a Appium por lo obvio: un fichero de veinte líneas frente a un proyecto de
pruebas con su servidor.

Y lo que no hace bien:

- **La parte de la nube es de pago.** `maestro test` en local y `maestro studio` son gratis; Maestro
  Cloud, que es donde corren las pruebas en aparatos ajenos, se factura. No se contrata sin orden.
- **Prueba por texto y por identificador visible**, así que un cambio de copy rompe la prueba. Los
  elementos que se van a probar llevan identificador propio (`testID`, `Semantics`), o cada traducción
  es una prueba rota.
- **En iOS necesita un Mac con Xcode**, igual que todo lo demás del oficio; y el aparato o el simulador
  tienen que estar levantados antes.
- **Que la prueba pase no significa que la pantalla esté bien**: comprueba que el elemento existe y se
  puede tocar, no que esté colocado, ni que se lea, ni que sea accesible.
