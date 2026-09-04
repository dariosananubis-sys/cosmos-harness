---
cosmos: pueblo
nombre: ollama
padre: modelos-locales/servir
resumen: Gestor que descarga, versiona y sirve modelos con API compatible, sin compilar nada a mano.
---

https://github.com/ollama/ollama · MIT · 179.880★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
brew install ollama
ollama serve &                       # API compatible OpenAI en http://localhost:11434
ollama pull qwen3:4b-q4_K_M          # el tag decide si cabe: elegirlo a mano
ollama run qwen3:4b-q4_K_M "Resume este parrafo en una linea"
curl http://localhost:11434/v1/chat/completions -H 'Content-Type: application/json' \
  -d '{"model":"qwen3:4b-q4_K_M","messages":[{"role":"user","content":"hola"}]}'
```

**Memoria**: mismas reglas que el motor que lleva debajo — un 7B en `Q4_K_M` ronda 4-4,5 GB y un 13B
en Q4 ronda 7-8 GB: **se compara con la memoria libre real**, con el sistema abierto encima. La
ventaja propia aquí es la gestión de memoria: descarga el modelo de la RAM tras un rato de inactividad
(`keep_alive`), así que entre usos no compite con el resto de la máquina.

Gana a `mudler/LocalAI` (48.802★) en solape de alcance para el mismo caso — servir un modelo con
API compatible —: aquel añade backends que aquí no hacen falta. Con sus dos vecinos de este mismo
país la relación es de reparto de tareas, no de descarte: `llama-cpp` (pueblo vecino, 126.862★) es
el motor que lleva por debajo — define GGUF y es el estándar de facto —, y ollama es la capa de
conveniencia encima (descarga, versión, `keep_alive`) a cambio de menos control fino que el que da
usar `llama-cpp` suelto. Y `vllm` (pueblo vecino, 90.859★) gana en el caso que ollama no cubre:
muchas peticiones concurrentes a la vez sobre `PagedAttention`, arquitectura pensada para servir
tráfico de producción, no un único uso local.

Ojo, el punto flojo real: el catálogo invita a bajar cosas que **no caben**, y `ollama run modelo` sin
tag elige por su cuenta. Hay que escribir el `:Xb-qN` a mano. Un modelo que no entra no falla limpio:
se arrastra intercambiando a disco y parece «lento», no «no cabe». Y `ollama serve` escucha en un
puerto local sin autenticación — no exponerlo fuera de la máquina. Su vecino `vllm` pide además GPU
dedicada (NVIDIA/CUDA o AMD/ROCm) para arrancar en modo acelerado; sin ella no es una alternativa
viable, solo un pueblo que existe para cuando sí la haya.
