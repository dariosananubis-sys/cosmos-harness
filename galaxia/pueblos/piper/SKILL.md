---
cosmos: pueblo
nombre: piper
padre: audiovisual/voz
resumen: Motor de voz local con espeak-ng embebido; continuacion mantenida del piper original ya archivado.
---

https://github.com/OHF-Voice/piper1-gpl · GPL-3.0 · 5.438★ · último push 2026-08-29 (comprobado
2026-09-03)

```bash
pip install piper-tts
python3 -m piper.download_voices en_US-lessac-medium
```

```bash
python3 -m piper -m en_US-lessac-medium -f salida.wav -- "Texto de ejemplo para la locucion."
# servidor HTTP para uso repetido, sin recargar el modelo en cada frase:
python3 -m piper.http_server -m en_US-lessac-medium
```

Es la continuación mantenida del `piper` original de Rhasspy (11,3k★), que la propia ficha de
`kokoro` de este catálogo ya señala como **archivado** desde 2025-08-26 — aquí vive bajo la Open Home
Foundation, con el mismo diseño (modelo pequeño, `espeak-ng` embebido para fonemización) pero
commits activos.

Frontera con `kokoro`, el vecino de este mismo país: ese entra por calidad de voz cuando hay algo de
margen de cómputo (82 M de parámetros, dos o tres gigas); `piper` es más ligero y más rápido en una
máquina justa de memoria, y es la elección cuando lo que manda es latencia baja o hardware modesto
(placas embebidas, asistentes de voz locales tipo Home Assistant, que lo usa de fábrica). Frente a
`espeak-ng` a secas, gana en calidad — aquel suena robótico y no vale para una entrega final.

Ojo, y hay que decirlo porque es del mismo tipo de aviso que ya lleva `kokoro`: el propio repositorio
publica un cartel de **«buscando mantenedores»** (Open Home Foundation; el correo de
contacto está en su README). No está parado —hay push la semana de esta comprobación— pero el
proyecto está pidiendo ayuda para seguir así. Revisar en la próxima pasada si el ritmo cambia. Y lo
de siempre en síntesis: no clona voces, la lista de voces es la que hay descargada, y el catálogo en
castellano es más corto que el inglés.
