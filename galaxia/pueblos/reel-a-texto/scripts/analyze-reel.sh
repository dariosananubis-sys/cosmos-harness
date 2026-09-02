#!/bin/bash
# tools/analyze-reel.sh — Pipeline análisis Instagram/YouTube reels + carousels.
# Uso: ./tools/analyze-reel.sh <URL> [output_dir] [--high-precision]
# Output: <output_dir>/<id>/{video.mp4, audio.mp3, transcript.txt, frame_NN.jpg, meta.txt, description.txt}
# Robust:
#   - carousel /p/ sin video → extrae description del caption
#   - reel video → yt-dlp + ffmpeg + mlx_whisper (base por defecto, large-v3 con --high-precision)
#   - login required → mensaje user-friendly

set -euo pipefail

URL="${1:?URL requerido}"
OUTDIR="${2:-/tmp/reel-analysis}"
HIGH_PRECISION=0
for arg in "$@"; do
  [ "$arg" = "--high-precision" ] && HIGH_PRECISION=1
done

ID="$(echo "$URL" | sha1sum | cut -c1-12)"
DIR="$OUTDIR/$ID"
mkdir -p "$DIR"
cd "$DIR"

echo "[$ID] URL: $URL"
echo "[$ID] DIR: $DIR"

# Etapa 1: info.json (siempre intenta) — incluso si video falla, caption queda
if [ ! -f *.info.json ] 2>/dev/null; then
  YTDLP_OUTPUT=$(yt-dlp --no-warnings \
    --cookies-from-browser firefox \
    --write-info-json --skip-download \
    -o "info.%(ext)s" \
    "$URL" 2>&1 || true)
  if echo "$YTDLP_OUTPUT" | grep -qE "empty media response|login page"; then
    echo "[$ID] LOGIN_REQUIRED: abre Instagram en Firefox + login, luego retry."
    echo "$YTDLP_OUTPUT" > error.log
    exit 2
  fi
fi

INFO_JSON=$(ls *.info.json 2>/dev/null | head -1)
if [ -z "$INFO_JSON" ]; then
  echo "[$ID] FAIL: no info.json extraído"
  exit 1
fi

# Extraer caption + meta
python3 -c "
import json, pathlib
d = json.load(open('$INFO_JSON'))
meta_lines = [
  f\"TITLE: {(d.get('title') or '')[:120]}\",
  f\"UPLOADER: {d.get('uploader') or '?'} (@{d.get('uploader_id') or '?'})\",
  f\"DURATION: {d.get('duration') or '?'}s\",
  f\"VIEW_COUNT: {d.get('view_count') or '?'}\",
  f\"LIKE_COUNT: {d.get('like_count') or '?'}\",
  f\"TYPE: {d.get('_type') or 'video'}\",
]
pathlib.Path('meta.txt').write_text('\n'.join(meta_lines))
pathlib.Path('description.txt').write_text(d.get('description') or '')
print(f'[meta] {len(meta_lines)} fields | description: {len(d.get(\"description\") or \"\")} chars')
"

# Etapa 2: descargar video si existe (carousels NO tienen video extraíble)
HAS_VIDEO=0
if [ ! -f video.mp4 ]; then
  yt-dlp -q --no-warnings \
    --cookies-from-browser firefox \
    -f "best[ext=mp4]/best" \
    -o "video.%(ext)s" \
    "$URL" 2>&1 | tail -3 || true
fi
[ -f video.mp4 ] && HAS_VIDEO=1

if [ $HAS_VIDEO -eq 0 ]; then
  echo "[$ID] CAROUSEL_NO_VIDEO: description-only extraction OK"
  echo ""
  echo "=== OUTPUT ==="
  echo "DIR: $DIR"
  echo "meta.txt: yes"
  echo "description.txt: $(wc -c < description.txt) bytes"
  ls -lh "$DIR" | tail -5
  exit 0
fi

# Etapa 3: audio + transcript
if [ ! -f audio.mp3 ]; then
  ffmpeg -loglevel error -y -i video.mp4 -vn -ac 1 -ar 16000 -b:a 64k audio.mp3
fi

if [ ! -f transcript.txt ]; then
  # Default: whisper-base-mlx (fast, ~30s/min audio). --high-precision usa large-v3 (~3x slower, ~5x precision).
  # Útil para reels low-signal donde base genera loop hallucinate. Detectar post-hoc: transcript con bigrama
  # repetido >5x consecutivo o ratio token_unique/total < 0.15 → re-run con --high-precision.
  MODEL="mlx-community/whisper-base-mlx"
  if [ $HIGH_PRECISION -eq 1 ]; then
    MODEL="mlx-community/whisper-large-v3-mlx"
    echo "[$ID] HIGH_PRECISION: large-v3 (~3x más lento, ~5x precisión)"
  fi
  python3 -c "
import mlx_whisper, pathlib
res = mlx_whisper.transcribe('audio.mp3', path_or_hf_repo='$MODEL', language='es')
pathlib.Path('transcript.txt').write_text(res.get('text','').strip())
print(f'[transcribe] {len(res.get(\"text\",\"\"))} chars')
" 2>&1 | tail -3
fi

# Etapa 4: 5 frames
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4 2>/dev/null | head -1)
[ -z "$DURATION" ] && DURATION=10
N=5
for i in $(seq 1 $N); do
  T=$(python3 -c "print(round($DURATION * $i / ($N + 1), 2))")
  FRAME="frame_$(printf '%02d' $i).jpg"
  if [ ! -f "$FRAME" ]; then
    ffmpeg -loglevel error -y -ss "$T" -i video.mp4 -frames:v 1 -q:v 3 -vf "scale=720:-1" "$FRAME"
  fi
done

echo ""
echo "=== OUTPUT ==="
echo "DIR: $DIR"
echo "transcript.txt: $(wc -c < transcript.txt 2>/dev/null || echo 0) bytes"
echo "description.txt: $(wc -c < description.txt 2>/dev/null || echo 0) bytes"
echo "frames: $(ls frame_*.jpg 2>/dev/null | wc -l | tr -d ' ')"
ls -lh "$DIR" | tail -8
