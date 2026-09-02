---
cosmos: pueblo
nombre: miniaudio
padre: juegos
resumen: Un solo fichero en C y cero dependencias para reproducir y capturar sonido en cualquier plataforma.
---

https://github.com/mackron/miniaudio · dominio publico (Unlicense) o MIT-0 a eleccion, licencia doble declarada en el propio fichero (la API de GitHub devuelve `NOASSERTION`) · 7.216★ · último push 2026-08-19 (comprobado por API de GitHub el 2026-09-01).

```bash
curl -O https://raw.githubusercontent.com/mackron/miniaudio/master/miniaudio.h
# no hay instalacion: un unico fichero de cabecera que se copia al proyecto
```

```c
#define MINIAUDIO_IMPLEMENTATION
#include "miniaudio.h"

int main(void) {
    ma_engine motor;
    if (ma_engine_init(NULL, &motor) != MA_SUCCESS) return -1;
    ma_engine_play_sound(&motor, "sonidos/salto.wav", NULL);
    getchar();                       // el sonido va en su propio hilo
    ma_engine_uninit(&motor);
    return 0;
}
```

```bash
cc juego.c -o juego -lm -lpthread && ./juego
```

Se copia al proyecto y ya esta: no hay biblioteca que enlazar ni motor de audio que configurar.
Encaja directo en un proyecto de `raylib` o de `bevy` sin traerse un subsistema entero. Gana a
`jarikomppa/soloud` (2,2k estrellas), la alternativa clasica de su hueco, por estar viva: aquella no
recibe un push desde agosto de 2024. Aqui hay reproduccion, captura, mezcla y decodificacion de
WAV/FLAC/MP3 sin dependencias.

Y lo que no hace bien: no es un motor de audio de juego completo. No hay grafo de efectos avanzado,
ni bancos de sonido, ni la integracion con middleware que dan FMOD o Wwise — que ademas son de pago
por licencia comercial, asi que fuera de este catalogo. Y el fichero es enorme (mas de 90.000 lineas
en una sola cabecera): compilarlo alarga cada build, asi que conviene aislar el
`MINIAUDIO_IMPLEMENTATION` en su propia unidad de compilacion.

Licencia sin letra pequena: dominio publico o MIT-0, sin atribucion obligatoria. Es de lo mas
permisivo que hay.
