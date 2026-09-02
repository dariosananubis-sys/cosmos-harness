#!/usr/bin/env python3
"""wp-cli remoto con red de seguridad: si el host no trae el cliente `mariadb`,
las consultas SQL se hacen por PHP con $wpdb en su lugar.

Encima de wp-ssh.sh (--sitio <slug>, que resuelve el sitio desde un índice JSON
de tipo ~/.wp-sites/sites.json). Pensado para compartirse entre varios scripts
que necesiten wp-cli o SQL sin repetir el mismo apaño en cada uno.
"""
import re
import subprocess
import tempfile
from pathlib import Path

WP_SSH = Path(__file__).resolve().parent / "wp-ssh.sh"


def wp(slug, argumentos, tiempo=180):
    proceso = subprocess.run(
        [str(WP_SSH), "--sitio", slug] + list(argumentos),
        capture_output=True, text=True, timeout=tiempo,
    )
    if proceso.returncode:
        raise SystemExit(f"wp-cli falló en {slug}: {proceso.stderr.strip()[:300]}")
    return proceso.stdout


def consulta(slug, sql):
    """Algunos hosts no tienen el cliente `mariadb` y `wp db query` revienta; ahí se
    pregunta por PHP con $wpdb, que siempre está disponible."""
    try:
        return wp(slug, ["db", "query", sql, "--skip-column-names"])
    except SystemExit as error:
        if "mariadb" not in str(error) and "mysql" not in str(error):
            raise
    return php(slug, f"""<?php
global $wpdb;
$filas = $wpdb->get_results('{sql.replace("'", "\\'")}', ARRAY_N);
foreach ($filas as $fila) {{ echo implode("\t", array_map('strval', $fila)), "\n"; }}
""")


def ejecuta(slug, sql):
    try:
        wp(slug, ["db", "query", sql])
        return
    except SystemExit as error:
        if "mariadb" not in str(error) and "mysql" not in str(error):
            raise
    php(slug, f"""<?php
global $wpdb;
$wpdb->query('{sql.replace("'", "\\'")}');
""")


def php(slug, codigo):
    with tempfile.NamedTemporaryFile("w", suffix=".php", delete=False, encoding="utf-8") as tmp:
        tmp.write(codigo)
        ruta = tmp.name
    try:
        return wp(slug, ["--php", ruta], tiempo=240)
    finally:
        Path(ruta).unlink(missing_ok=True)


def prefijo(slug):
    """`db prefix` devuelve ruido en algunos hosts: si no parece un prefijo, wp_."""
    for linea in reversed(wp(slug, ["db", "prefix"]).splitlines()):
        candidato = linea.strip()
        # No todos los prefijos acaban en "_": algunos hosts usan uno propio corto.
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", candidato):
            return candidato
    return "wp_"
