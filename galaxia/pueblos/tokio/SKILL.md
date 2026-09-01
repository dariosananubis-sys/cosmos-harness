---
cosmos: pueblo
nombre: tokio
padre: rendimiento/velocidad
resumen: Planificador multihilo, temporizadores y entrada y salida no bloqueante para concurrencia.
---

https://github.com/tokio-rs/tokio · MIT · 33.046★ · push 2026-08-31 (comprobado 2026-09-01)

```bash
cargo add tokio --features full

cat > src/main.rs <<'RS'
#[tokio::main]
async fn main() {
    let t = tokio::spawn(async { tokio::time::sleep(std::time::Duration::from_millis(50)).await; 7 });
    let r = tokio::time::timeout(std::time::Duration::from_secs(1), t).await;
    println!("{:?}", r);
}
RS
cargo run
```

Es el país de código de este nicho: con esto **se escribe** software concurrente, no se mide. Trae
planificador multihilo con robo de trabajo, temporizadores, entrada y salida no bloqueante y
primitivas de sincronización pensadas para tareas asíncronas.

Gana a `async-std`, su rival directo, por adopción: la mayoría de las bibliotecas asíncronas del
ecosistema solo funcionan sobre este tiempo de ejecución, así que elegir el otro es quedarse fuera de
media biblioteca. El paralelismo de datos con uso intensivo de procesador es otro problema y otra
biblioteca (`rayon`); no se sustituyen.

Ojo: **una tarea que bloquea el hilo hunde el planificador entero**. Una llamada síncrona a disco, un
`std::thread::sleep` o un cálculo largo dentro de una tarea asíncrona paran a todas las demás del
mismo hilo, y el síntoma es latencia inexplicable, no un error. Eso va en `tokio::task::spawn_blocking`.
Para verlo, `tokio-console` (del mismo proyecto) muestra las tareas que no ceden.
