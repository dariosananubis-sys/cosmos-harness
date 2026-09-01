---
cosmos: pueblo
nombre: tauri
padre: moviles
resumen: Escritorio con el motor web del sistema: binarios de megas donde otros gastan cientos.
---

https://github.com/tauri-apps/tauri - Apache-2.0 (dual con MIT) - 110.725 estrellas - ultimo push
2026-09-01 (comprobado por API de GitHub el 2026-09-01).

```bash
brew install rust
npm create tauri-app@latest
cd mi-app && npm install
```

```bash
npm run tauri dev            # ventana nativa con recarga en caliente
npm run tauri build          # binario firmable, unos pocos MB
npm run tauri android init   # movil, desde la v2
```

```rust
// src-tauri/src/lib.rs — una funcion de Rust invocable desde el frontal
#[tauri::command]
fn saludar(nombre: &str) -> String { format!("hola, {nombre}") }

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![saludar])
        .run(tauri::generate_context!())
        .expect("error al arrancar");
}
```

```js
import { invoke } from '@tauri-apps/api/core'
await invoke('saludar', { nombre: 'ejemplo' })
```

Gana a Electron —el rival, y se nombra— por lo que decide en una maquina de 8 GB: Electron empaqueta
un Chromium entero por aplicacion (binarios de mas de 100 MB y cientos de megas de RAM por app
abierta); aqui se usa el motor web del sistema operativo y el binario baja a unos pocos MB. Con dos
o tres aplicaciones de escritorio abiertas, la diferencia es la maquina usable o no.

Y lo que no hace bien, que es la otra cara exacta de por que gana: **usar el motor del sistema
significa que no todos los usuarios tienen el mismo motor**. WebKit en macOS, WebView2 en Windows,
WebKitGTK en Linux — con versiones distintas segun el sistema del usuario. Un CSS o una API de
navegador que funciona en tu Mac puede fallar en el Linux del cliente, y no lo veras sin probar en
cada plataforma. Electron, con su Chromium empotrado, no tiene ese problema: esa es su ventaja real.

Y el otro coste: compilar exige la cadena de Rust y, para firmar, cuota de desarrollador de Apple
(la anual) si se quiere distribuir en macOS sin el aviso de "desarrollador no identificado", y el
certificado de firma de Windows aparte. El movil de la v2 sigue siendo mas joven que el escritorio.
