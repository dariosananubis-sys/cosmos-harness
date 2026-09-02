#!/usr/bin/env python3
"""Apunta en BWS una Application Password de WordPress YA creada a mano en wp-admin.

Hermano de bootstrap-app-pass.py sin la parte de login: el humano crea la
Application Password en Perfil -> Contraseñas de aplicación y deja el valor en
un FICHERO; esto lo lee, guarda APP_<slug> en BWS (JSON {"user","appPassword"}
+ note legible), verifica contra REST y borra el fichero.

El valor NUNCA se imprime ni se pasa por argv de este script (solo la ruta).

Uso: python3 save-app-pass.py <slug> <user> <ruta-fichero>
Requiere: bws CLI con permiso de escritura sobre el proyecto BWS_PROJECT_ID,
BWS_ACCESS_TOKEN en el entorno (ver bootstrap-app-pass.py, mismo módulo).
"""
import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# bootstrap-app-pass.py tiene guion: no es importable por nombre normal.
_spec = importlib.util.spec_from_file_location(
    'bootstrap_app_pass', os.path.join(HERE, 'bootstrap-app-pass.py'))
boot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(boot)


def note_for(slug, domain, user):
    return (f'APPLICATION PASSWORD (REST)\n'
            f'Web: https://{domain}\n'
            f'Usuario: {user}\n'
            f'Nombre en WP: {boot.APP_NAME}\n'
            f'Consumidor: APP_{slug}\n'
            f'Revocar en: wp-admin -> Perfil -> Contraseñas de aplicación')


def main():
    if len(sys.argv) != 4:
        sys.exit('uso: save-app-pass.py <slug> <user> <ruta-fichero>')

    slug, user, path = sys.argv[1], sys.argv[2], sys.argv[3]
    domain = boot.site_domain(slug)

    with open(path) as handle:
        app_pass = handle.read().strip().replace(' ', '')

    if len(app_pass) < 20:
        sys.exit(f'save-app-pass: el fichero no parece una Application Password '
                 f'({len(app_pass)} chars tras limpiar espacios)')

    env = boot.bws_env()
    secrets = boot.bws_list(env)

    saved, why = boot.save_bws(env, secrets, slug, user, app_pass)
    if not saved:
        sys.exit(f'save-app-pass: bws fallo: {why}')

    # note legible junto al secreto, para quien lo encuentre en la bóveda sin contexto
    key = f'APP_{slug}'
    hit = next((s for s in boot.bws_list(env) if s['key'] == key), None)
    if hit:
        subprocess.run(['bws', 'secret', 'edit', hit['id'], '--note', note_for(slug, domain, user)],
                       env=env, capture_output=True, text=True)

    verified, detail = boot.verify_rest(domain, user, app_pass)
    if not verified:
        sys.exit(f'save-app-pass: guardado en BWS pero verify REST fallo ({detail}). '
                 f'Fichero NO borrado: {path}')

    os.remove(path)
    print(f'OK {slug}: {key} guardado en BWS, verify REST {detail}, fichero borrado')


if __name__ == '__main__':
    main()
