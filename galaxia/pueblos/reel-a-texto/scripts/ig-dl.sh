#!/bin/bash
# ig-dl.sh — descarga posts/reels/carruseles de Instagram con sesion del navegador.
# Uso: scripts/ig-dl.sh <url> [outdir]
# Requiere: login en instagram.com en Chrome o Firefox (una vez). Auto-detecta el perfil con sessionid.
# yt-dlp para video; gallery-dl para carruseles de imagen (yt-dlp los ve como "0 items").
set -euo pipefail

URL="${1:?Uso: ig-dl.sh <url-instagram> [outdir]}"
# default persistente + gitignored: <repo>/notes/inbox/ig-media/
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${2:-$REPO/notes/inbox/ig-media}"
mkdir -p "$OUT"

CH="$HOME/Library/Application Support/Google/Chrome"
FF="$HOME/Library/Application Support/Firefox/Profiles"

# --- detectar navegador:perfil con sessionid de instagram ---
detect() {
  for p in "$CH"/Default "$CH"/Profile\ *; do
    [ -f "$p/Cookies" ] || continue
    n=$(sqlite3 "file:$p/Cookies?mode=ro" \
        "SELECT count(*) FROM cookies WHERE host_key LIKE '%instagram%' AND name='sessionid';" 2>/dev/null || echo 0)
    if [ "${n:-0}" -gt 0 ]; then echo "chrome:$(basename "$p")"; return 0; fi
  done
  for c in "$FF"/*/cookies.sqlite; do
    [ -f "$c" ] || continue
    n=$(sqlite3 "file:$c?mode=ro" \
        "SELECT count(*) FROM moz_cookies WHERE host LIKE '%instagram%' AND name='sessionid';" 2>/dev/null || echo 0)
    if [ "${n:-0}" -gt 0 ]; then echo "firefox:$(basename "$(dirname "$c")")"; return 0; fi
  done
  return 1
}

# --- tier sin-cuenta: embed publico (portada + caption, NO carrusel completo) ---
embed_tier() {
  local code ua
  code=$(echo "$URL" | grep -oE '/(p|reel|tv)/[A-Za-z0-9_-]+' | grep -oE '[A-Za-z0-9_-]+$' | tail -1)
  [ -z "$code" ] && { echo "[ig-dl] no pude extraer el shortcode de la URL" >&2; return 1; }
  ua="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
  curl -sL -A "$ua" "https://www.instagram.com/p/$code/embed/captioned/" -o "$OUT/$code.embed.html"
  EMBED_HTML="$OUT/$code.embed.html" python3 - "$OUT" "$code" <<'PY'
import os,sys,re,html
out,code=sys.argv[1],sys.argv[2]
t=open(os.environ["EMBED_HTML"],encoding="utf-8",errors="ignore").read()
m=re.search(r'class="Caption"[^>]*>(.*?)</div>',t,re.S)
cap=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',m.group(1)))).strip() if m else ""
open(f"{out}/{code}.caption.txt","w").write(cap)
imgs=[html.unescape(i).encode().decode('unicode_escape','ignore') for i in re.findall(r'https://scontent[^"\\\s]+t51\.82787-15[^"\\\s]+',t)]
open(f"{out}/{code}.imgurl","w").write(imgs[0] if imgs else "")
print("CAPTION:", cap[:300])
PY
  local u; u=$(cat "$OUT/$code.imgurl" 2>/dev/null)
  [ -n "$u" ] && curl -sL -A "Mozilla/5.0" "$u" -o "$OUT/$code.cover.jpg" && echo "[ig-dl] portada -> $OUT/$code.cover.jpg"
}

BROWSER="$(detect || true)"
if [ -z "$BROWSER" ]; then
  echo "[ig-dl] sin sesion IG -> tier SIN-CUENTA (solo portada + caption)." >&2
  embed_tier || { echo "ERROR: embed publico fallo. Para carrusel completo haz login IG y reintenta." >&2; exit 3; }
  echo "[ig-dl] NOTA: carrusel completo (slides 2-N) requiere login. Haz login en instagram.com (Chrome/Firefox) y reintenta." >&2
  exit 0
fi
echo "[ig-dl] usando cookies de: $BROWSER"

# --- 1) intento yt-dlp (video/reels) ---
echo "[ig-dl] yt-dlp..."
if yt-dlp --cookies-from-browser "$BROWSER" -o "$OUT/%(uploader_id)s_%(id)s.%(ext)s" "$URL" 2>"$OUT/.yt.log"; then
  if ls "$OUT"/*.* >/dev/null 2>&1; then echo "[ig-dl] OK via yt-dlp -> $OUT"; exit 0; fi
fi
echo "[ig-dl] yt-dlp sin media (probable carrusel de imagenes). Fallback gallery-dl..."

# --- 2) fallback gallery-dl (carruseles/imagenes) ---
if command -v gallery-dl >/dev/null 2>&1; then
  CB="${BROWSER%%:*}"   # gallery-dl: --cookies-from-browser chrome / firefox (sin perfil exacto -> usa default; pasa el nombre completo)
  gallery-dl --cookies-from-browser "$BROWSER" -D "$OUT" "$URL" 2>"$OUT/.gdl.log" || \
  gallery-dl --cookies-from-browser "$CB" -D "$OUT" "$URL" 2>>"$OUT/.gdl.log"
  if ls "$OUT"/* >/dev/null 2>&1; then echo "[ig-dl] OK via gallery-dl -> $OUT"; exit 0; fi
fi

echo "ERROR: ni yt-dlp ni gallery-dl bajaron media. Logs: $OUT/.yt.log $OUT/.gdl.log" >&2
exit 1
