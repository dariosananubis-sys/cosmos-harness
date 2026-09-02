"""
Extractor de keyframes de vídeos cortos (reels/shorts) para combinar con
transcripción de audio (p.ej. Whisper).

Uso:
    # Sobre todos los vídeos en resultados/ cuya transcripción sea < 300 chars
    python extract_frames.py --auto

    # Sobre IDs concretos
    python extract_frames.py --ids ID1 ID2

    # Con threshold custom
    python extract_frames.py --auto --min-chars 500

Salida: resultados/<id>_frame_NN.jpg (4 keyframes por defecto).

Razón: una transcripción de audio resuelve el habla, pero algunos vídeos son
música sin habla o texto en pantalla. Extraer keyframes permite combinar visión +
transcripción para no perder la parte del contenido que solo se ve.

Requiere: yt-dlp y ffmpeg accesibles en PATH (o vía la variable FFMPEG_PATH).
Espera en <output_dir>/<id>_meta.json un campo "url" y en
<output_dir>/<id>_transcripcion.txt la transcripción de cada vídeo — ajusta
list_candidates_auto/get_url_for_id si tu convención de ficheros es otra.
"""

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

OUTPUT_DIR = Path(os.environ.get("EXTRACT_FRAMES_DIR", "resultados"))
DEFAULT_MIN_CHARS = 300
DEFAULT_N_FRAMES = 4


def _detect_ffmpeg_dir() -> str:
    env_val = os.environ.get("FFMPEG_PATH")
    if env_val:
        return env_val
    binary = shutil.which("ffmpeg")
    if binary:
        return str(Path(binary).parent)
    sys.exit(
        "No encuentro ffmpeg en PATH. Instálalo (brew install ffmpeg / apt install ffmpeg) "
        "o exporta FFMPEG_PATH=<carpeta con ffmpeg.exe/ffmpeg>."
    )


FFMPEG_PATH = _detect_ffmpeg_dir()
os.environ["PATH"] = FFMPEG_PATH + os.pathsep + os.environ.get("PATH", "")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extrae frames de vídeos cortos para análisis visual.")
    parser.add_argument(
        "--auto",
        action="store_true",
        help=f"Modo automático: procesa todos los vídeos con transcripción <--min-chars (default {DEFAULT_MIN_CHARS}).",
    )
    parser.add_argument("--ids", nargs="+", help="Procesa IDs concretos.")
    parser.add_argument(
        "--min-chars",
        type=int,
        default=DEFAULT_MIN_CHARS,
        help=f"En modo --auto, umbral de chars para considerar transcripción insuficiente (default {DEFAULT_MIN_CHARS}).",
    )
    parser.add_argument(
        "--n-frames",
        type=int,
        default=DEFAULT_N_FRAMES,
        help=f"Frames por vídeo (default {DEFAULT_N_FRAMES}).",
    )
    parser.add_argument(
        "--keep-video",
        action="store_true",
        help="No borra el .mp4 temporal tras extraer frames.",
    )
    args = parser.parse_args()
    if not args.auto and not args.ids:
        parser.error("Pasa --auto o --ids <ID1> <ID2> ...")
    return args


def list_candidates_auto(min_chars: int) -> list[str]:
    candidates = []
    for meta_path in sorted(OUTPUT_DIR.glob("*_meta.json")):
        try:
            json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        content_id = meta_path.stem.replace("_meta", "")

        transcript_path = OUTPUT_DIR / f"{content_id}_transcripcion.txt"
        if not transcript_path.exists():
            continue
        text = transcript_path.read_text(encoding="utf-8", errors="ignore")
        body = text.split("-" * 60, 1)[-1].strip() if "-" * 60 in text else text
        body = re.sub(r"\s+", " ", body).strip()
        if len(body) < min_chars:
            candidates.append(content_id)
    return candidates


def get_url_for_id(content_id: str) -> str | None:
    meta_path = OUTPUT_DIR / f"{content_id}_meta.json"
    if not meta_path.exists():
        return None
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return meta.get("url")


def extract_frames_for_id(content_id: str, n_frames: int, keep_video: bool):
    existing = list(OUTPUT_DIR.glob(f"{content_id}_frame_*.jpg"))
    if existing:
        print(f"[=] {content_id}: ya hay {len(existing)} frame(s). Skip.")
        return

    url = get_url_for_id(content_id)
    if not url:
        print(f"[X] {content_id}: no se encontró URL en meta.json")
        return

    video_template = str(OUTPUT_DIR / f"{content_id}_vid.%(ext)s")
    print(f"[v] {content_id}: descargando vídeo baja calidad...")
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--no-playlist",
                "--format",
                "worstvideo[ext=mp4]/worst[ext=mp4]/worst",
                "--ffmpeg-location",
                FFMPEG_PATH,
                "-o",
                video_template,
                url,
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            print(f"[X] {content_id}: yt-dlp falló: {result.stderr[:200]}")
            return
    except subprocess.TimeoutExpired:
        print(f"[X] {content_id}: timeout descargando vídeo")
        return

    video_candidates = [
        p for p in OUTPUT_DIR.glob(f"{content_id}_vid.*")
        if p.is_file() and p.suffix.lower() not in {".part", ".ytdl", ".temp"}
    ]
    if not video_candidates:
        print(f"[X] {content_id}: no se encontró vídeo descargado")
        return

    video_path = sorted(video_candidates, key=lambda p: p.name.lower())[0]
    print(f"[v] {content_id}: extrayendo {n_frames} keyframes con ffmpeg...")
    frame_template = str(OUTPUT_DIR / f"{content_id}_frame_%02d.jpg")
    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-i",
                str(video_path),
                "-vf",
                r"select=eq(pict_type\,I)",
                "-vframes",
                str(n_frames),
                "-q:v",
                "2",
                frame_template,
                "-y",
            ],
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode != 0:
            print(f"[X] {content_id}: ffmpeg falló: {result.stderr[:200]}")
            return
    except subprocess.TimeoutExpired:
        print(f"[X] {content_id}: timeout ffmpeg")
        return
    finally:
        if not keep_video:
            try:
                video_path.unlink()
            except Exception:
                pass

    frames = sorted(OUTPUT_DIR.glob(f"{content_id}_frame_*.jpg"))
    print(f"[OK] {content_id}: {len(frames)} frame(s) extraídos")


def main():
    args = parse_args()
    if args.ids:
        ids = args.ids
    else:
        ids = list_candidates_auto(args.min_chars)
        if not ids:
            print(f"[i] No hay candidatos con transcripción <{args.min_chars} chars.")
            return
        print(f"[i] {len(ids)} vídeo(s) con transcripción <{args.min_chars} chars:")
        for cid in ids:
            print(f"  - {cid}")

    print()
    for content_id in ids:
        extract_frames_for_id(content_id, args.n_frames, args.keep_video)


if __name__ == "__main__":
    main()
