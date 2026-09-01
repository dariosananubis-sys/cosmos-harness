# IA aplicada que se puede vender — barrido GitHub

> Dominio: construir cosas con modelos, no hablar de IA. Cubre servir modelos en local, RAG y
> búsqueda semántica, fine-tuning/LoRA, visión por computador y OCR, voz, modelos pequeños,
> cuantización, evaluación y despliegue en producción. Método: WebSearch + WebFetch sobre
> documentación oficial, repos de GitHub y análisis de terceros (sin clonar repos: estrellas y
> fechas son las que reportan las fuentes, marcadas «no verificado» cuando la fuente es floja).
> Fecha del rastreo: 2026-09-01. Entorno de referencia: Mac de Darío, **8 GB de RAM**, sin API de
> pago, cuenta de suscripción no de uso por token.
>
> Convención (heredada de `research/ESTADO-DEL-ARTE.md`): 🔧 = mecanismo real y verificable ·
> 📝 = solo prosa/lista sin nada ejecutable · ⚠️ = mecanismo real con hueco importante (declarado
> por el propio proyecto, deprecado, o dependencia de pago).

---

## De primera

Máximo 10. Ganan por combinar: corre en local sin tarjeta de crédito, tiene mecanismo verificable
(no prosa), es el estándar de facto de su categoría hoy (no un experimento de tres semanas), sigue
vivo, y — el criterio que descarta a más candidatos — **cabe o tiene una vía clara de caber en 8 GB
de RAM**.

### 1. llama.cpp 🔧 — el motor base
- **URL**: https://github.com/ggml-org/llama.cpp
- **Estrellas**: ~126K · **Última actividad**: commits casi diarios, el más reciente el
  2026-08-31.
- **Qué hace**: motor de inferencia en C/C++ puro para LLMs, sin dependencia de Python ni CUDA
  obligatoria. Corre en CPU, Metal (Apple Silicon), CUDA, Vulkan.
- **Mecanismo**: define el formato **GGUF** y su propio sistema de cuantización (k-quants,
  IQ-quants) que reduce un modelo FP16 a 4-8 bits con pérdida de calidad controlada. Ejecuta el
  grafo de cómputo con kernels a mano, sin framework de por medio — es la razón de que arranque en
  milisegundos y pese megas, no gigas.
- **8 GB de RAM**: el binario en sí no consume nada; el coste es el modelo cargado. Un 7B en Q4_K_M
  ronda 4-4.5 GB — cabe con margen. Un 13B en Q4 ronda 7-8 GB — al límite, no recomendable con el
  sistema operativo abierto encima. **No entra**: nada por encima de ~13B cuantizado en esta
  máquina.
- **Nota de calidad**: es el estándar de facto — Ollama, LM Studio, LocalAI y la mayoría de apps de
  IA local lo usan como backend por debajo. Es infraestructura, no un producto con el que se
  interactúa directamente salvo por CLI.

### 2. Ollama 🔧 — la puerta de entrada
- **URL**: https://github.com/ollama/ollama
- **Estrellas**: ~176K (Series B de 65M$ en julio 2026, sigue siendo software libre) · **Última
  actividad**: viva, con backend MLX en preview desde marzo 2026.
- **Qué hace**: envuelve llama.cpp (y ahora MLX en preview) con `ollama pull <modelo>` y
  `ollama run`, y expone una API REST **compatible con OpenAI** en `localhost:11434`.
- **Mecanismo**: gestor de modelos con manifest + capas tipo Docker (descarga incremental,
  reutiliza capas compartidas entre modelos), cuantización automática al bajar, GPU auto-detectada
  (CUDA/ROCm/Metal).
- **8 GB de RAM**: mismas reglas que llama.cpp por debajo. La ventaja real en 8 GB es la gestión de
  memoria: descarga el modelo de RAM tras un rato de inactividad (`keep_alive`), así no compite con
  el resto del sistema entre usos.
- **Nota de calidad**: es hoy «la respuesta por defecto» a «cómo corro un LLM en local» — el mayor
  ecosistema de integraciones de terceros. Punto débil real: el catálogo de 200+ modelos invita a
  bajar cosas que no caben; hay que elegir el tag `:Xb-q4` a mano.

### 3. MLX / mlx-lm (Apple) 🔧 — el nativo del Mac
- **URL**: https://github.com/ml-explore/mlx · https://github.com/ml-explore/mlx-lm
- **Estrellas**: MLX ~27K, mlx-lm ~4.3K · **Última actividad**: v0.31.2 (abril 2026), Apple publicó
  investigación sobre los Neural Accelerators del M5 con MLX en enero 2026.
- **Qué hace**: framework de arrays de Apple para Apple Silicon (equivalente a NumPy/PyTorch pero
  con memoria unificada CPU/GPU nativa) + `mlx-lm`, paquete para generar texto **y hacer
  fine-tuning LoRA/QLoRA** sobre esa base.
- **Mecanismo**: aprovecha la memoria unificada del Mac (no hay copia CPU↔GPU como en una discreta)
  y los Neural Accelerators del M5. `mlx-community` en HuggingFace ya trae ~4.300 modelos
  pre-convertidos, así que casi nunca hace falta convertir uno a mano.
- **8 GB de RAM**: es el framework que mejor exprime la RAM unificada de un Mac de 8 GB — un 3B en
  4-bit corre con soltura, un 7B en 4-bit (~4 GB) es factible pero deja poco margen para el resto
  del sistema. **Para fine-tuning LoRA en este Mac, `mlx_lm.lora` es la vía real** — a diferencia
  de Unsloth (ver Segunda fila), que exige NVIDIA/CUDA y no corre aquí.
- **Nota de calidad**: Ollama migrando a MLX como backend en Apple Silicon (marzo 2026, en preview)
  es la señal de madurez más fuerte — el propio estándar de facto lo adopta.

### 4. LocalAI 🔧 — el "todo en uno" sin GPU
- **URL**: https://github.com/mudler/LocalAI
- **Estrellas**: ~48.8K · **Última actividad**: viva, 7.744 commits acumulados.
- **Qué hace**: motor de IA que expone una API compatible con OpenAI para texto, visión, voz e
  imagen, sin exigir GPU.
- **Mecanismo**: arquitectura de backends modulares — cada uno envuelve un motor especializado
  (llama.cpp, vLLM, whisper.cpp, stable-diffusion, MLX…) que se descarga bajo demanda, más de 60
  backends en el catálogo. Es la capa que unifica «texto + voz + visión» bajo un único puerto y un
  único contrato de API.
- **8 GB de RAM**: el motor en sí es ligero (imagen Docker de 1-2 GB); el límite lo pone, otra vez,
  el modelo que cargues por debajo — mismas reglas que llama.cpp/whisper.cpp.
- **Nota de calidad**: MIT, "privacy-first" real (nada sale de la máquina salvo que tú lo
  configures). Es la pieza que responde a "quiero UNA API para todo lo de IA local" sin escribir el
  pegamento a mano.

### 5. whisper.cpp 🔧 — transcripción en local
- **URL**: https://github.com/ggml-org/whisper.cpp
- **Estrellas**: ~37K · **Última actividad**: viva, del mismo equipo que llama.cpp (ggml-org).
- **Qué hace**: reimplementación en C/C++ puro de Whisper (OpenAI) para transcripción de audio a
  texto, sin Python ni GPU obligatoria.
- **Mecanismo**: mismo motor `ggml` que llama.cpp, aprovecha Metal en Apple Silicon. Benchmark
  citado en M5 Pro: large-v3 a ~10× tiempo real (60 min de audio en ~6 min).
  **En Mac es la opción por defecto** frente a `faster-whisper` (que brilla más con GPU NVIDIA).
- **8 GB de RAM**: los modelos van de 75 MB (tiny) a ~3 GB (large-v3); incluso el grande cabe sin
  apuros porque el audio no exige mantener contexto de "conversación" en RAM como un chat LLM.
- **Nota de calidad**: componente maduro, sin dependencias raras, es lo que hay debajo de la mayoría
  de apps de dictado local en Mac.

### 6. Kokoro-82M (TTS) 🔧 — voz sintética que cabe en cualquier sitio
- **URL modelo**: https://huggingface.co/hexgrad/Kokoro-82M · **CLI**:
  https://github.com/nazdridoy/kokoro-tts
- **Estrellas**: el wrapper CLI es pequeño (cientos de estrellas, no verificado con precisión); el
  modelo en sí es el que importa y está ampliamente re-empaquetado (varios wrappers activos:
  `kokoro-tts`, `Kokoro-TTS-Local`).
- **Qué hace**: síntesis de voz (texto → audio) con solo **82M parámetros**, licencia Apache-2.0.
- **Mecanismo**: modelo compacto entrenado específicamente para eficiencia — no es un LLM grande
  recortado, es arquitectura pensada para correr en CPU.
- **8 GB de RAM**: cabe de sobra — corre en 2-3 GB de RAM/VRAM o menos, incluso en CPU pura. Es de
  las pocas piezas de este dominio que **no** obliga a elegir entre calidad y memoria.
- **Nota de calidad**: calidad de voz señalada como notablemente buena para su tamaño en las
  comparativas de 2026; el punto flojo es que "Kokoro" en sí no es un proyecto con gobierno único —
  hay varios wrappers de comunidad, hay que elegir uno mantenido y revisar su fecha de commit antes
  de fiarse.

### 7. sentence-transformers + BGE-M3 / bge-small 🔧 — embeddings locales
- **URL**: https://github.com/UKPLab/sentence-transformers ·
  https://github.com/FlagOpen/FlagEmbedding (familia BGE)
- **Estrellas**: sentence-transformers ~16K+ (no verificado con precisión) · BGE es el modelo
  estándar citado en toda comparativa 2026 de embeddings open-source.
- **Qué hace**: convierte texto en vectores para búsqueda semántica — la pieza de entrada de
  cualquier RAG.
- **Mecanismo**: librería Python que carga modelos de HuggingFace y expone `.encode()`; BGE-M3
  añade soporte multilingüe y **búsqueda híbrida** (denso + disperso + multi-vector) en un solo
  modelo, entrenado sobre 1.6B de pares contrastivos (variante Nomic v2, comparable en objetivo).
- **8 GB de RAM**: `all-MiniLM-L6-v2` (22M parámetros, ~90 MB) es la opción segura y trivial en
  cualquier RAM; `BGE-M3` (~560M parámetros, ~2.2 GB en fp32) sigue cabiendo en 8 GB pero es
  bastante más pesado — para este Mac, empezar por el modelo pequeño y subir solo si la calidad de
  recuperación lo pide.
- **Nota de calidad**: es la capa de entrada estándar de facto en todo pipeline RAG local — no hay
  debate real sobre si usarla, solo sobre qué modelo concreto cargar encima.

### 8. LanceDB 🔧 — base vectorial que no pelea por la RAM
- **URL**: https://github.com/lancedb/lancedb
- **Estrellas**: no verificado con precisión (citado como opción madura en comparativas 2026 junto
  a Qdrant/Chroma/Milvus).
- **Qué hace**: base de datos vectorial embebida — corre **dentro** del proceso Python, sin
  servidor aparte que levantar.
- **Mecanismo**: formato columnar propio (Lance), lee y escribe directo a disco con acceso
  zero-copy — a diferencia de Qdrant/Milvus (procesos servidor que quieren su propia porción de
  RAM), LanceDB no mantiene todo el índice en memoria por diseño, pensado para datasets más grandes
  que la RAM disponible.
- **8 GB de RAM**: es la elección más segura del dominio para esta máquina precisamente por eso —
  ningún servicio adicional compitiendo por RAM residente, el disco absorbe lo que no cabe.
- **Nota de calidad**: gana en "prototipo o proyecto en un Mac modesto"; para un caso de escala
  real (billones de vectores, filtrado complejo en producción) Qdrant sigue siendo la referencia
  (ver Segunda fila) — no es sustituto en todos los escenarios, es el mejor **para este entorno
  concreto**.

### 9. PaddleOCR 🔧 — OCR maduro y con buen benchmark
- **URL**: https://github.com/PaddlePaddle/PaddleOCR
- **Estrellas**: no verificado con precisión, referencia constante en todas las comparativas OCR
  2026.
- **Qué hace**: detección + reconocimiento de texto en imágenes/documentos, con foco en layouts
  complejos (tablas, facturas, documentos escaneados).
- **Mecanismo**: pipeline en dos etapas (detección de región + reconocimiento de carácter), con la
  variante **PaddleOCR-VL-1.5** (enero 2026) añadiendo un modelo visión-lenguaje que sube la
  precisión a 94.5% en el benchmark OmniDocBench v1.5.
- **8 GB de RAM**: la variante clásica (no-VL) corre bien en CPU con RAM modesta; la variante VL
  pesa más por ser un modelo de visión-lenguaje — para esta máquina, empezar por el pipeline
  clásico y reservar la VL para casos que de verdad lo necesiten.
- **Nota de calidad**: gana a Tesseract en layouts complejos y a los OCR basados en VLM completo
  (olmOCR, Qwen2.5-VL) en coste de cómputo — es el punto medio maduro.

### 10. lm-evaluation-harness 🔧 — el estándar de evaluación
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Estrellas**: ~13.9K · **Última actividad**: refactor de CLI e instalación más ligera en
  diciembre 2025 — vivo.
- **Qué hace**: evalúa modelos generativos contra 60+ benchmarks académicos estándar con cientos de
  subtareas, con prompts públicos para que los resultados sean comparables entre papers.
- **Mecanismo**: soporta múltiples backends de ejecución — HuggingFace local, vLLM local, o APIs
  comerciales — así que **se puede evaluar 100% en local**, sin pagar por juez-LLM (a diferencia de
  Ragas, ver Segunda fila).
- **8 GB de RAM**: el propio harness es ligero; el coste real es el modelo evaluado + el dataset —
  mismas reglas que servir el modelo, elegir tareas y tamaños de modelo acordes.
- **Nota de calidad**: es el backend real del "Open LLM Leaderboard" de HuggingFace, usado
  internamente por NVIDIA, Cohere y MosaicML — no es una alternativa entre varias, es la referencia
  cuando alguien pide "¿esto se puede comparar con otros benchmarks publicados?".

---

## Segunda fila

Sólidos, con mecanismo real, pero no son el pick por defecto en este entorno (piden servidor
aparte, piden GPU NVIDIA, cobran por el juez-LLM, o son la alternativa nº2 de una categoría ya
cubierta arriba).

- **Qdrant** 🔧 — https://github.com/qdrant/qdrant — vector DB en Rust, mejor filtrado y mejor free
  tier de las bases servidor; pide un proceso aparte (Docker), más pesado en RAM que LanceDB pero
  más potente en producción real.
- **Chroma** 🔧 — https://github.com/chroma-core/chroma — la API más simple para prototipos RAG;
  migración habitual a Qdrant/pgvector cuando el filtrado crece.
- **Milvus** 🔧 — https://github.com/milvus-io/milvus — pensado para miles de millones de vectores;
  sobredimensionado para un proyecto de un solo Mac de 8 GB.
- **LangChain** 🔧 — https://github.com/langchain-ai/langchain — ~92K estrellas, 350+ integraciones;
  capa de orquestación sobre embeddings+vectorDB+LLM, no imprescindible pero acelera el pegamento.
  Fama de complejidad excesiva para RAG simple.
- **LlamaIndex** 🔧 — https://github.com/run-llama/llama_index — mejor que LangChain cuando el
  trabajo es sobre todo ingesta/recuperación de documentos (300+ conectores).
- **Haystack** 🔧 — https://github.com/deepset-ai/haystack — arquitectura más auditable, menos
  ecosistema; opción cuando se prioriza claridad sobre cobertura.
- **rerankers (lib unificada) + BGE-reranker-v2-m3** 🔧 —
  https://github.com/AnswerDotAI/rerankers ·
  https://huggingface.co/BAAI/bge-reranker-v2-m3 — cross-encoder multilingüe, distilado de BGE-M3;
  mejora precisión del top-k tras la recuperación por embeddings, coste extra de cómputo por
  consulta pero modelo base pequeño.
- **vLLM** 🔧⚠️ — https://github.com/vllm-project/vllm — motor de inferencia de alto rendimiento
  (paged attention, batching continuo), estándar de producción a escala. **No entra en 8 GB de RAM
  de forma razonable ni es su terreno** — está pensado para GPU dedicada con lotes concurrentes;
  se cita porque es lo que se usaría el día que el proyecto salga del Mac a un servidor con GPU.
- **Axolotl** 🔧⚠️ — https://github.com/axolotl-ai-cloud/axolotl — fine-tuning multi-GPU vía YAML,
  interopera con adaptadores LoRA entrenados en Unsloth. Requiere GPU NVIDIA — no corre en Mac.
- **Unsloth** 🔧⚠️ — https://github.com/unslothai/unsloth — kernels Triton para acelerar fine-tuning
  LoRA/QLoRA en GPU consumer; **CUDA-only, no corre en Apple Silicon** — para este Mac, la vía real
  de fine-tuning es `mlx-lm` (ver De primera #3), no Unsloth.
- **PEFT + TRL (HuggingFace)** 🔧 — https://github.com/huggingface/peft ·
  https://github.com/huggingface/trl — librerías base de LoRA/QLoRA/RLHF sobre las que Axolotl y
  Unsloth se apoyan; usables directamente pero con más código propio que escribir.
- **LLaMA-Factory** 🔧 — https://github.com/hiyouga/LLaMA-Factory — UI + CLI para fine-tuning sin
  escribir YAML a mano, buena puerta de entrada antes de Axolotl.
- **text-embeddings-inference (TEI, HuggingFace)** 🔧 —
  https://github.com/huggingface/text-embeddings-inference — servidor dedicado de embeddings/
  reranking de alto rendimiento (Flash Attention, batching dinámico); útil si vas a servir
  embeddings como servicio propio en vez de llamarlos desde el mismo proceso Python.
- **Tesseract** 🔧 — https://github.com/tesseract-ocr/tesseract — el OCR más simple de desplegar,
  peor con documentos ruidosos que PaddleOCR/Surya/EasyOCR.
- **EasyOCR** 🔧 — https://github.com/JaidedAI/EasyOCR — buen manejo de documentos reales
  desordenados, más lento que Tesseract.
- **docTR** 🔧 — https://github.com/mindee/doctr — deja ajustar a mano el compromiso
  precisión/latencia; opción cuando PaddleOCR no encaja con el caso.
- **Surya** 🔧 — https://github.com/VikParuchuri/surya — OCR tipo VLM de una sola pasada
  (imagen completa → markdown/JSON), mejor con documentos degradados que el pipeline clásico.
- **olmOCR** 🔧 — https://github.com/allenai/olmocr — OCR vía LLM multimodal, preserva tablas y
  estructura markdown; más caro en cómputo que los pipelines clásicos.
- **faster-whisper** 🔧 — https://github.com/SYSTRAN/faster-whisper — misma precisión que Whisper,
  4× más rápido en GPU NVIDIA / 2× en CPU; en Mac, whisper.cpp sigue siendo la opción por defecto
  (ver De primera #5).
- **Piper TTS** 🔧 — repo histórico `rhasspy/piper` (movimiento reciente de mantenimiento
  documentado en foros, **no verificado con precisión el repo activo actual**) — TTS pequeño
  pensado para dispositivos de borde (Raspberry Pi incluido); voz más robótica que Kokoro pero
  huella mínima.
- **Coqui TTS / XTTS v2** 🔧⚠️ — https://github.com/coqui-ai/TTS — clonado de voz multilingüe (17
  idiomas) de calidad alta; **la empresa Coqui cerró** — el repo original quedó sin mantenimiento
  activo, hay forks de comunidad (p. ej. `idiap/coqui-ai-TTS`) que siguen vivos. Usar con esa
  reserva.
- **openedai-speech** 🔧 — https://github.com/matatonic/openedai-speech — servidor TTS compatible
  con la API de OpenAI usando XTTS v2 o Piper por debajo; capa de pegamento útil si el resto del
  stack ya habla "API estilo OpenAI".
- **LiteLLM** 🔧 — https://github.com/BerriAI/litellm — ~57.7K estrellas; proxy/gateway que unifica
  100+ proveedores de LLM (locales y de pago) bajo una sola interfaz, con seguimiento de coste y
  panel propio. El gateway en sí es gratis y local; sirve para no reescribir código si mañana se
  mezcla un modelo local con uno de pago puntual.
- **promptfoo** 🔧 — https://github.com/promptfoo/promptfoo — ~24.7K estrellas; testing de prompts
  y red-teaming de seguridad, corre 100% local (compatible con Ollama), sin depender de una API de
  pago para evaluar.
- **ragas** 🔧⚠️ — https://github.com/explodinggradients/ragas — ~15.6K estrellas; framework de
  evaluación de RAG específico (fidelidad, relevancia de contexto). El quickstart oficial usa
  GPT-4o de pago como juez — no hay evidencia clara en la documentación de una vía 100% local sin
  tocar una API externa, aunque la arquitectura modular (`llm_factory`) sugiere que sería posible
  con más trabajo de configuración.
- **DeepEval** 🔧 — https://github.com/confident-ai/deepeval — alternativa a Ragas con más énfasis
  en "unit testing" de LLMs al estilo pytest; mismo patrón de depender de un LLM-juez, revisar antes
  de usar si exige API de pago o admite un juez local.
- **Ultralytics YOLO** 🔧⚠️ — https://github.com/ultralytics/ultralytics — ~61.1K estrellas;
  detección/segmentación/pose en tiempo real, exportable a ONNX para CPU. **Licencia AGPL-3.0** —
  gratis para investigación, pero uso comercial en producción exige licencia Enterprise de pago; si
  el plan es vender un producto cerrado con YOLO dentro, revisar el término de licencia antes de
  construir sobre él.
- **SAM2 (Segment Anything 2, Meta)** 🔧⚠️ — https://github.com/facebookresearch/sam2 — ~19.8K
  estrellas; segmentación de imagen y vídeo por prompt (clic/caja). Pide GPU real (benchmarks en
  A100, PyTorch ≥2.5.1) — no es candidato para 8 GB de RAM sin GPU dedicada.

---

## Humo

- **Rapid-MLX** — https://github.com/raullenchai/Rapid-MLX — afirma "4.2× más rápido que Ollama" en
  Apple Silicon; repo joven, cifras propias sin benchmark independiente, vigilar antes de apostar.
- **vllm-mlx** — https://github.com/waybarrios/vllm-mlx — puerto de vLLM a MLX/Apple Silicon,
  proyecto de comunidad reciente, no el vLLM oficial.
- **Mac-MLX** — https://github.com/magicnight/mac-mlx — app nativa macOS sobre MLX, sin señal de
  tracción todavía.
- **awesome-local-ai-agents** — https://github.com/Supersynergy/awesome-local-ai-agents — lista
  curada útil como mapa, pero es lista de enlaces sin mecanismo propio: filtrada por el criterio
  "sin piedad" del encargo, no cuenta como recurso.
- **awesome-ocr-2026** — https://github.com/WalidHadri-Iron/awesome-ocr-2026 — mismo caso: lista,
  no herramienta.

---

## Mapeo a COSMOS

Este dominio entero encaja como **país** (GOAL.md §3 / TAXONOMIA.md: "familia de capacidades que
comparten tecnología o modelo mental" — aquí, construir con modelos). Las **provincias** agrupan
skills hermanas por sub-tarea; los **pueblos** son las herramientas atómicas concretas de este
rastreo. Ninguna de ellas tiene hoy partes que se carguen por separado, así que ninguna sube a
ciudad todavía — si en el futuro una integra sub-guías propias (p. ej. una skill de "RAG local" que
documente por separado embeddings/vectorDB/reranking como casas), esa sería la señal de ascenderla.

| País | Provincia | Pueblos (de este rastreo) |
|---|---|---|
| **IA aplicada** | Servir modelos en local | llama.cpp, Ollama, MLX/mlx-lm, LocalAI, vLLM |
| | RAG y búsqueda semántica | sentence-transformers/BGE, LanceDB, Qdrant, Chroma, Milvus, rerankers/BGE-reranker, LangChain, LlamaIndex, Haystack |
| | Fine-tuning y adaptadores | mlx-lm (LoRA nativo Mac), Unsloth, Axolotl, PEFT, TRL, LLaMA-Factory |
| | Visión y OCR | PaddleOCR, Tesseract, EasyOCR, docTR, Surya, olmOCR, Ultralytics YOLO, SAM2 |
| | Voz | whisper.cpp, faster-whisper, Kokoro-82M, Piper, Coqui/XTTS v2, openedai-speech |
| | Cuantización | GGUF (mecanismo propio de llama.cpp), AutoAWQ (deprecado) |
| | Evaluación de modelos | lm-evaluation-harness, promptfoo, ragas, DeepEval |
| | Despliegue en producción | LiteLLM, LocalAI, vLLM, text-embeddings-inference |

Nota de contención: **cuantización no tiene pueblo propio maduro fuera de llama.cpp** — hoy es un
mecanismo (GGUF) más que una provincia con varios pueblos vivos independientes (AWQ está deprecado,
GPTQ no se pudo verificar en este rastreo por agotamiento del presupuesto de búsqueda). Si al
construir la provincia real esto no cambia, la provincia correcta podría ser "Cuantización" como
**mar** (regla transversal: "cuantiza con llama.cpp salvo que uses vLLM en GPU") en vez de provincia
con pueblos propios — la pregunta de TAXONOMIA.md ("¿contiene cosas, o atraviesa cosas?") apunta más
a agua que a sólido aquí.

---

## Lo que falta

- **Presupuesto de WebSearch agotado a mitad de rastreo** (límite de sesión, compartido con otras
  tareas activas del mismo canal): se completaron RAG, servir en local, voz, fine-tuning, OCR con
  búsqueda directa; evaluación, cuantización, CV y despliegue se completaron por WebFetch dirigido
  a repos ya conocidos, sin ronda de búsqueda propia — así que puede haber un competidor mejor de
  2026 en esas categorías que no se descubrió por no poder buscar "¿qué hay nuevo en cuantización
  2026?" a ciegas.
- **Chunking (troceado de texto para RAG)**: el encargo lo pide explícitamente y no se encontró un
  recurso independiente con mecanismo propio digno de entrada aparte — hoy vive dentro de los
  text-splitters de LangChain/LlamaIndex. Falta decidir si merece su propio pueblo o si de verdad es
  una función, no un proyecto.
- **GPTQ / GPTQModel**: no se pudo verificar el estado 2026 del sucesor de AutoGPTQ (AutoAWQ sí se
  confirmó deprecado). Pendiente de una búsqueda dedicada.
- **Modelos pequeños especializados** (el punto del encargo sobre "modelos pequeños") se cubrió de
  forma indirecta vía el catálogo de Ollama (Qwen 0.5-3B, Gemma3 270M, Phi-4-mini 3.8B, Llama3.2
  1-3B) pero no se investigó cada familia como proyecto propio (benchmark, licencia, caso de uso) —
  se trataron como "el modelo que cargas en llama.cpp/Ollama/MLX", no como recursos de primera
  clase separados.
- **Sin verificación cruzada de estrellas**: varias cifras (sentence-transformers, LanceDB, Kokoro
  wrappers, Piper) vienen de resúmenes de terceros, no de la página del repo leída directamente —
  quedan marcadas "no verificado con precisión" en vez de inventar un número.
