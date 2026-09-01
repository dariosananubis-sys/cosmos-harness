# Medios y creación — producir a escala (vídeo, imagen, audio, documentos)

Barrido GitHub para COSMOS. Dominio: edición/procesado de vídeo automatizado (FFmpeg y capas
encima), generación/edición de imagen, optimización de imágenes para web, audio (limpieza,
transcripción, doblaje, síntesis), generación de documentos (PDF, presentaciones, hojas de
cálculo), plantillas y automatización de diseño, subtítulos, diagramas como código, y
procesamiento por lotes de cientos de ficheros.

Método: API de GitHub autenticada (`/search/repositories` + `/repos/{owner}/{repo}` directos),
sin WebSearch (cupo de la sesión agotado). ~55 consultas de búsqueda (limitadas a 30/min por el
rate-limit propio del endpoint de búsqueda, distinto del general de 5000/h) + ~45 lookups directos
de repositorio para verificar estrellas/licencia/última actividad/issues abiertas en vivo de los
candidatos con más señal. Fecha del barrido: 2026-09-01.

---

## De primera

Máximo 10. Elegidos por: coste cero y ejecución local real, mecanismo de lote verificable por CLI
(nada de "arrastra el fichero a la interfaz"), y encaje con un Mac de 8 GB de RAM (modelos
pequeños/CPU, arquitecturas en streaming, nada que exija VRAM de GPU).

1. **[FFmpeg/FFmpeg](https://github.com/FFmpeg/FFmpeg)** — 63.8k★, C, licencia mixta (LGPL/GPL
   según build), activo (push 2026-08-31). **Por qué gana**: es la base sobre la que se apoya
   prácticamente todo lo demás de este dominio (transcodificación, extracción de audio, recorte,
   subtítulos incrustados, miniaturas). Un binario, cero dependencias de red, procesa cientos de
   ficheros por línea de comandos con un `for` de shell. Mirror oficial del repo canónico
   (`git.ffmpeg.org`).

2. **[ggml-org/whisper.cpp](https://github.com/ggml-org/whisper.cpp)** — 53.3k★, MIT, muy activo
   (push 2026-08-31). **Por qué gana**: transcripción local de audio/vídeo en C++, modelos ggml
   cuantizados que corren en CPU con huella de RAM baja (el modelo `base`/`small` cabe sobrado en
   8 GB) — sin API de pago, sin GPU. Exporta SRT/VTT directamente, así que cubre transcripción Y
   subtítulos en el mismo paso. Mecanismo: `whisper-cli -f audio.wav -osrt` por fichero, batcheable.

3. **[danielgatis/rembg](https://github.com/danielgatis/rembg)** — 24.6k★, MIT, activo (push
   2026-08-18, solo 3 issues abiertas — señal de proyecto sano, no abandonado). **Por qué gana**:
   quitar fondo de imagen con modelos ONNX en CPU, con **modo carpeta nativo**
   (`rembg p ./entrada ./salida`) para cientos de fotos de producto sin tocar una a una. Sin API
   externa, sin cuenta.

4. **[rhasspy/piper](https://github.com/rhasspy/piper)** — 11.3k★, MIT, último push 2025-08-26
   (más de un año sin commit — mantenimiento ralentizado, pero el binario ya es funcional y
   estable, sin dependencias que rompan). **Por qué gana**: TTS neuronal local vía ONNX,
   voces de decenas de MB, corre en CPU en tiempo real o más rápido en un Mac modesto — la opción
   más práctica para narración/doblaje en lote sin GPU ni servicio de pago.

5. **[jgm/pandoc](https://github.com/jgm/pandoc)** — 46.1k★, GPL-2.0, muy activo (push
   2026-09-01). **Por qué gana**: el conversor universal de documentos — Markdown/HTML/DOCX/PDF
   (vía LaTeX)/EPUB/PPTX en cualquier dirección, un solo binario Haskell sin ML de por medio.
   Mecanismo maduro (20 años), predecible, ideal como pieza central de un pipeline de documentos
   por lotes.

6. **[ocrmypdf/OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF)** — 34.6k★, MPL-2.0, activo (push
   2026-08-31). **Por qué gana**: añade capa de texto buscable a PDFs escaneados en lote
   (`ocrmypdf --output-type pdfa *.pdf`), usa Tesseract por debajo, soporta reintento/skip de
   páginas ya OCR'eadas — es la referencia de facto para digitalizar cientos de documentos de
   cliente sin tocar cada uno.

7. **[Kozea/WeasyPrint](https://github.com/Kozea/WeasyPrint)** — 9.5k★, BSD-3-Clause, activo
   (push 2026-08-31). **Por qué gana**: HTML/CSS → PDF respetando CSS Paged Media de verdad
   (saltos de página, cabeceras/pies repetidos, numeración) — permite diseñar UNA plantilla HTML y
   generar cientos de informes/facturas con el motor de layout real de un navegador, no un
   PDF-toolkit de bajo nivel.

8. **[mingrammer/diagrams](https://github.com/mingrammer/diagrams)** — 42.6k★, MIT, activo (push
   2026-08-16). **Por qué gana**: diagrama-como-código en Python puro — describe la arquitectura
   en un script, genera PNG/SVG reproducible en CI, sin abrir ninguna app de dibujo. Encaja
   directo con el patrón COSMOS de "todo verificable por script".

9. **[microsoft/markitdown](https://github.com/microsoft/markitdown)** — 177k★(!), MIT, muy
   activo (push 2026-08-31). **Por qué gana**: convierte Office/PDF/imágenes/audio a Markdown
   limpio con una sola CLI/librería — la pieza que falta para meter documentos de cliente
   heterogéneos en un pipeline de agentes sin escribir un parser por formato. Tracción y velocidad
   de desarrollo muy por encima del resto de conversores.

10. **[lovell/sharp](https://github.com/lovell/sharp)** (Node, 32.6k★, Apache-2.0, activo) sobre
    **[libvips/libvips](https://github.com/libvips/libvips)** (11.6k★, LGPL, activo) — **Por qué
    gana**: la arquitectura de libvips procesa imágenes en streaming (no carga el fichero entero
    en memoria), diseñada explícitamente para huella de RAM baja — el mejor encaje real con un Mac
    de 8 GB para redimensionar/convertir cientos de imágenes a WebP/AVIF para web sin que el
    proceso se coma la RAM.

## Segunda fila

**Vídeo**
- [Zulko/moviepy](https://github.com/Zulko/moviepy) — 14.9k★, MIT, activo. Edición programática
  (cortes, composición, efectos) en Python sobre ffmpeg; capa de guion reproducible por encima del
  binario.
- [Breakthrough/PySceneDetect](https://github.com/Breakthrough/PySceneDetect) — 5.1k★, BSD-3,
  activo. Detección de cortes de escena en lote — útil para auto-clipping de material largo.
- [kkroening/ffmpeg-python](https://github.com/kkroening/ffmpeg-python) — 11k★, Apache-2.0, **sin
  commits desde ago-2024**. Wrapper de filtros complejos de ffmpeg; funciona pero sin
  mantenimiento activo.
- [k4yt3x/video2x](https://github.com/k4yt3x/video2x) — 21.4k★, **AGPL-3.0**, activo. Framework de
  upscaling/interpolación (Real-ESRGAN/RIFE por detrás); el backend de más calidad pide GPU.
- [xinntao/Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) — 36.6k★, BSD-3, **sin commits
  desde ago-2024**. Modelo de referencia para upscaling de imagen/vídeo; huérfano pero base de
  facto de casi todo lo demás en esta subcategoría.
- [jianchang512/pyvideotrans](https://github.com/jianchang512/pyvideotrans) — 18.9k★, GPL-3.0,
  activo. Traducción de vídeo extremo a extremo (voz→texto→traducción→doblaje→subtítulos) con
  motores intercambiables, incluye Whisper local.
- [Huanshere/VideoLingo](https://github.com/Huanshere/VideoLingo) — 18.3k★, Apache-2.0, activo.
  Pipeline de subtitulado/doblaje que corta por sentido (no por tiempo fijo), un-click.

**Audio, transcripción y voz**
- [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) — 25.2k★, **sin commits
  desde nov-2025**. Reimplementación con CTranslate2, más rápida que whisper.cpp en cierto
  hardware; mantenimiento frenado.
- [m-bain/whisperX](https://github.com/m-bain/whisperX) — 23.8k★, BSD-2, activo. Timestamps por
  palabra y diarización de hablantes sobre faster-whisper; más pesado (arrastra pyannote).
- [alphacep/vosk-api](https://github.com/alphacep/vosk-api) — 15.1k★, Apache-2.0, activo. STT
  offline con modelos ~50MB — alternativa mucho más ligera que Whisper cuando no hace falta
  máxima precisión.
- [thewh1teagle/kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) — 2.7k★, MIT, activo
  — y [remsky/Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI) — 5.4k★, Apache-2.0,
  activo. TTS local Kokoro-82M vía ONNX, calidad alta para su tamaño, CPU-friendly.
- [espeak-ng/espeak-ng](https://github.com/espeak-ng/espeak-ng) — 6.8k★, GPL-3.0, activo. TTS
  formante, decenas de idiomas, huella mínima; calidad robótica, no vale para entrega final.
- [nateshmbhat/pyttsx3](https://github.com/nateshmbhat/pyttsx3) — 2.5k★, MPL-2.0, activo.
  Envoltorio Python de los motores TTS del sistema (usa el `say` de macOS); cero modelos que
  descargar.
- [coqui-ai/TTS](https://github.com/coqui-ai/TTS) — 46k★, MPL-2.0, **sin commits desde ago-2024,
  empresa cerrada**. El motor con voice cloning/XTTS-v2 más citado del ecosistema, pero muerto
  como proyecto oficial; hay forks comunitarios si hace falta esa calidad de clonación.
- [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) — 4.6k★, **sin commits
  desde oct-2024**. Reducción de ruido en tiempo real, binario Rust ligero; sigue siendo sólido
  pese a la pausa.
- [tmoroney/auto-subs](https://github.com/tmoroney/auto-subs) — 4.1k★, MIT, activo. Subtítulos
  on-device integrados con DaVinci Resolve/Premiere/After Effects — puente GUI↔motor local.

**Imagen**
- [oxipng/oxipng](https://github.com/oxipng/oxipng) — 4.2k★, MIT, activo. Optimizador PNG sin
  pérdida, Rust, batch nativo por CLI.
- [svg/svgo](https://github.com/svg/svgo) — 22.7k★, MIT, activo. Optimizador SVG en lote, estándar
  de facto.
- [GoogleChromeLabs/squoosh](https://github.com/GoogleChromeLabs/squoosh) — 25.8k★, Apache-2.0,
  activo. Compresión multi-códec (mozjpeg/WebP/AVIF) con CLI (`squoosh-cli`).
- [exiftool/exiftool](https://github.com/exiftool/exiftool) — 5k★, GPL-3.0, activo. Lectura/
  escritura de metadatos EXIF sobre cientos de ficheros; referencia desde hace 20 años.
- [darktable-org/darktable](https://github.com/darktable-org/darktable) — 13k★, GPL-3.0, activo —
  y [RawTherapee/RawTherapee](https://github.com/RawTherapee/RawTherapee) — 4.1k★, GPL-3.0,
  activo. Revelado RAW con modo CLI batch (`darktable-cli`, `rawtherapee-cli`) para aplicar el
  mismo preset a cientos de fotos de una sesión.

**Documentos, diagramas y presentaciones**
- [python-openxml/python-docx](https://github.com/python-openxml/python-docx) — 5.7k★, MIT,
  activo. Generación/edición de Word por plantilla — base de informes de cliente en lote.
- [scanny/python-pptx](https://github.com/scanny/python-pptx) — 3.5k★, MIT, **sin commits desde
  ago-2024** (el propio mantenedor lo da por "feature-complete"; estable, no abandonado a la
  fuerza).
- [py-pdf/fpdf2](https://github.com/py-pdf/fpdf2) — 1.5k★, LGPL-3.0, activo. PDF puro Python sin
  dependencias nativas — ideal para informes/facturas simples generados en lote.
- [jsvine/pdfplumber](https://github.com/jsvine/pdfplumber) — 10.7k★, MIT, activo. Extracción de
  texto/tablas de PDF — dirección inversa: leer documentos de cliente, no solo generarlos.
- [pymupdf/PyMuPDF](https://github.com/pymupdf/PyMuPDF) — 10.6k★, **AGPL-3.0**, activo.
  Manipulación/render de PDF muy rápido; licencia a vigilar si algo de esto se llega a redistribuir.
- [docling-project/docling](https://github.com/docling-project/docling) — 65.8k★, MIT, activo
  (IBM). Convierte cualquier documento a Markdown/JSON con comprensión de layout — más pesado
  (modelos ML) que markitdown pero corre en CPU.
- [datalab-to/marker](https://github.com/datalab-to/marker) — 39.4k★, activo. PDF→Markdown/JSON
  de alta fidelidad, también basado en modelos ML.
- [tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract) — 76.3k★, Apache-2.0,
  activo. Motor OCR base que usa OCRmyPDF por debajo.
- [mermaid-js/mermaid](https://github.com/mermaid-js/mermaid) — 90k★, MIT, activo — y su
  [mermaid-cli](https://github.com/mermaid-js/mermaid-cli) — 5k★, MIT, activo. Diagramas desde
  texto; la CLI exporta a PNG/SVG vía Chromium headless (dependencia pesada en disco, ~300MB, no
  necesaria dentro de un Artifact de este mismo arnés porque ya renderiza Mermaid nativo).
- [marp-team/marp-cli](https://github.com/marp-team/marp-cli) — 3.8k★, MIT, activo. Markdown →
  diapositivas (HTML/PDF/PPTX) por CLI, ligero.
- [slidevjs/slidev](https://github.com/slidevjs/slidev) — 48.4k★, MIT, activo. Diapositivas
  Markdown para developers, más vistoso pero más pesado (stack Vite); exporta headless a
  PDF/PPTX/PNG.

## Humo

- [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
  (164.8k★) — sin commits desde marzo-2026 y pide GPU con VRAM que este Mac de 8 GB no tiene.
- [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI) (131k★, activo, antes
  `comfyanonymous/ComfyUI`) — mismo problema de GPU/VRAM para generación de imagen a escala.
- [invoke-ai/InvokeAI](https://github.com/invoke-ai/InvokeAI) (28.1k★, activo) — ídem, motor de
  generación de imagen que exige GPU.
- [neonbjb/tortoise-tts](https://github.com/neonbjb/tortoise-tts) (14.9k★) — voice cloning de
  calidad alta pero sin commits desde nov-2024 e inferencia lenta, mal encaje para lotes grandes.
- [suno-ai/bark](https://github.com/suno-ai/bark) (39.3k★) — TTS generativo vistoso, sin commits
  desde ago-2024 y no determinista, no vale para producción repetible.
- [resemble-ai/resemble-enhance](https://github.com/resemble-ai/resemble-enhance) (2.4k★) — mejora
  de voz, sin commits desde dic-2024, mucho mejor en GPU.
- [facebookresearch/denoiser](https://github.com/facebookresearch/denoiser) (1.9k★) — reducción de
  ruido, sin commits desde 2023, superado por DeepFilterNet.
- [chaiNNer-org/chaiNNer](https://github.com/chaiNNer-org/chaiNNer) (6k★) — cadena de procesado de
  imagen por nodos, pero es GUI de escritorio, no CLI batch real.
- [GuanYixuan/pyCapCut](https://github.com/GuanYixuan/pyCapCut) (654★) — genera proyectos de
  CapCut por script, sin licencia declarada en el repo y depende de tener CapCut instalado.
- [mikf/gallery-dl](https://github.com/mikf/gallery-dl) (19.4k★) y
  [yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) (188k★) — descargadores de medios, útiles para
  material de referencia pero son *obtención*, no *producción*; fuera del foco de este dominio.

## Mapeo a COSMOS

```
sistema-solar: Trabajo de agencia (cualquier proyecto de cliente)
  continente:  Producción y entrega de contenido
    país:      Medios y documentos a escala          (este dominio — familia de capacidades
                                                        que comparten el modelo mental "cientos
                                                        de ficheros, un solo comando, cero API
                                                        de pago")

      provincia: Vídeo
        pueblo:  Transcodificación y edición programática (FFmpeg, moviepy, ffmpeg-python)
        pueblo:  Subtítulos y doblaje end-to-end (whisper.cpp, pyvideotrans, VideoLingo)
        pueblo:  Upscaling/interpolación (Real-ESRGAN, video2x — casi todo pide GPU)

      provincia: Imagen
        pueblo:  Quitar fondo y recorte en lote (rembg)
        pueblo:  Optimización web (sharp/libvips, squoosh, oxipng, svgo)
        pueblo:  Revelado RAW en lote (darktable-cli, RawTherapee-cli)
        pueblo:  Metadatos EXIF en lote (exiftool)

      provincia: Audio
        pueblo:  Transcripción local (whisper.cpp, faster-whisper, vosk-api)
        pueblo:  Síntesis de voz local (piper, Kokoro, pyttsx3, espeak-ng)
        pueblo:  Limpieza/denoise (DeepFilterNet)

      provincia: Documentos
        pueblo:  Conversión universal (pandoc, markitdown, docling, marker)
        pueblo:  OCR en lote (OCRmyPDF + tesseract)
        pueblo:  Generación por plantilla (WeasyPrint, python-docx, fpdf2)
        pueblo:  Lectura/extracción de PDF (pdfplumber, PyMuPDF)

      provincia: Diagramas y presentaciones
        pueblo:  Diagrama como código (diagrams, mermaid + mermaid-cli)
        pueblo:  Slides desde Markdown (marp-cli, slidev)
```

Nota: a diferencia de otros dominios de este barrido (ej. WordPress/WooCommerce en
`web-ecommerce.md`), aquí no hay un "país orquestador" que empaquete varias provincias a la vez —
cada pueblo es una pieza suelta que se combina a mano en un pipeline. El candidato más cercano a
orquestador transversal es `microsoft/markitdown` (entra cualquier formato, sale Markdown), pero
solo cubre la provincia Documentos.

## Lo que falta

- **Doblaje/clonación de voz de producción sin GPU**: todo lo de primera calidad en esta subcategoría
  (Coqui/XTTS, tortoise-tts, bark, resemble-enhance) o está muerto como proyecto o rinde mal en
  CPU. La opción real en un Mac de 8 GB es Kokoro (calidad media-alta, ligero), pero no hay un
  candidato maduro Y mantenido Y CPU-only de calidad "de primera fila" — hueco real, no solo falta
  de búsqueda.
- **Generación de imagen por texto (text-to-image) en local**: los tres motores serios
  (stable-diffusion-webui, ComfyUI, InvokeAI) piden GPU/VRAM que este equipo no tiene. Dominio
  efectivamente bloqueado en local; la alternativa sería un servicio externo de pago, y la regla
  de "nunca pagar sin orden" lo deja fuera de este barrido.
- **Marca de agua/branding en lote sobre fotos**: no apareció un candidato dedicado con tracción
  real — se resuelve a mano con Pillow o un filtro de ffmpeg, sin librería "de primera" que lo
  cubra como caso de uso propio.
- **Un índice maestro tipo `awesome-selfhosted` específico de medios/creación** no salió con fuerza
  en las consultas — sería el complemento natural para no tener que repetir un barrido así cada
  vez que aparezca una herramienta nueva en esta familia.
- **mermaid-cli y el peso real de Chromium headless en 8 GB bajo uso simultáneo** (con otros
  procesos de agente corriendo a la vez) no se midió en vivo — marcar `UNVERIFIED` hasta probarlo
  con el Mac bajo carga real, no solo en reposo.
