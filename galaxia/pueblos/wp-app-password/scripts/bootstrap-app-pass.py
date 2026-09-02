#!/usr/bin/env python3
"""Bootstrap de Application Passwords de WordPress para un lote de sitios.

Por cada slug: lee WP_<slug> de BWS (url login, user, pass), hace login headless
con agent-browser, crea una Application Password en profile.php,
la guarda en BWS como APP_<slug> (JSON {"user", "appPassword"}) y verifica via
REST. NUNCA imprime secretos a stdout.

Uso: python3 bootstrap-app-pass.py <slug> [<slug> ...]
Requiere: bws CLI, agent-browser CLI, BWS_ACCESS_TOKEN en el entorno,
BWS_PROJECT_ID (proyecto BWS con las credenciales WP_<slug>) y, si usas slugs
en vez de `slug=dominio`, SITES_YAML_PATH (ruta a un YAML con entradas
`slug: ... / domain: ...`).
"""
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ID = os.environ.get('BWS_PROJECT_ID', '')
APP_NAME = os.environ.get('APP_PASS_NAME', 'automation')


def bws_env():
    env = dict(os.environ)
    if not env.get('BWS_ACCESS_TOKEN'):
        sys.exit('bootstrap: falta BWS_ACCESS_TOKEN en el entorno')
    if not PROJECT_ID:
        sys.exit('bootstrap: falta BWS_PROJECT_ID en el entorno')
    return env


def bws_list(env):
    out = subprocess.run(['bws', 'secret', 'list', PROJECT_ID, '--output', 'json'],
                         env=env, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f'bootstrap: bws list fallo: {out.stderr[:200]}')
    return json.loads(out.stdout)


def ab(*args, timeout=40):
    """agent-browser wrapper en sesión aislada. Devuelve (rc, stdout)."""
    env = {**os.environ, 'AGENT_BROWSER_SESSION': os.environ.get('AGENT_BROWSER_SESSION_NAME', 'bootstrap-app-pass')}
    try:
        r = subprocess.run(['agent-browser', *args], capture_output=True, text=True,
                           timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return 124, ''
    return r.returncode, (r.stdout or '').strip()


def site_domain(slug):
    yaml_path = os.environ.get('SITES_YAML_PATH', os.path.join(HERE, 'sites.yaml'))
    text = open(yaml_path).read()
    m = re.search(rf'slug:\s*{re.escape(slug)}\s*\n\s*domain:\s*(\S+)', text)
    if not m:
        sys.exit(f'bootstrap: slug {slug} no está en {yaml_path}; usa slug=dominio')
    return m.group(1)


def parse_target(arg):
    """`slug` (lo busca en SITES_YAML_PATH) o `slug=dominio` (para sitios sueltos que no
    están en el YAML de sitios activos)."""
    if '=' in arg:
        slug, domain = arg.split('=', 1)
        return slug, domain
    return arg, site_domain(arg)


def login(url, user, password):
    ab('open', url, timeout=60)
    ab('wait', '--load', 'networkidle', timeout=45)
    _, cur = ab('get', 'url')
    if cur in ('', 'about:blank'):
        ab('open', url, timeout=60)
        ab('wait', '--load', 'networkidle', timeout=45)
    # hasta 2 intentos: el 1º puede fallar por el test de cookies de WP
    for attempt in range(2):
        rc, _ = ab('fill', '#user_login', user)
        if rc != 0:
            return False, 'sin campo #user_login (login oculto o captcha)'
        ab('fill', '#user_pass', password)
        ab('click', '#wp-submit')
        for _poll in range(12):
            time.sleep(2)
            _, cur = ab('get', 'url')
            if '/wp-admin' in cur:
                return True, 'ok'
        ab('wait', '--load', 'networkidle', timeout=20)
    _, cur = ab('get', 'url')
    return False, f'no llegó a /wp-admin (quedó en {cur})'


def create_app_password():
    # derivar del wp-admin real post-login (respeta www vs no-www, donde vive la cookie)
    _, cur = ab('get', 'url')
    if '/wp-admin' not in cur:
        return None, f'sin sesión wp-admin (url: {cur})'
    profile = cur.split('/wp-admin')[0] + '/wp-admin/profile.php'
    ab('open', profile)
    ab('wait', '--load', 'networkidle', timeout=45)
    rc, _ = ab('wait', '#new_application_password_name', timeout=15)
    if rc != 0:
        return None, 'sección Application Passwords no disponible'
    ab('fill', '#new_application_password_name', APP_NAME)
    ab('click', '#do_new_application_password')
    rc, _ = ab('wait', '#new-application-password-value', timeout=20)
    if rc != 0:
        # nombre duplicado u otro error: reintento con sufijo
        ab('fill', '#new_application_password_name', f'{APP_NAME}-2')
        ab('click', '#do_new_application_password')
        rc, _ = ab('wait', '#new-application-password-value', timeout=20)
        if rc != 0:
            return None, 'no apareció el valor de la Application Password'
    rc, value = ab('get', 'value', '#new-application-password-value')
    value = value.replace(' ', '').strip()
    if rc != 0 or not value:
        return None, 'no se pudo leer el valor'
    return value, 'ok'


def save_bws(env, secrets, slug, user, app_pass):
    key = f'APP_{slug}'
    payload = json.dumps({'user': user, 'appPassword': app_pass}, ensure_ascii=False)
    hit = next((s for s in secrets if s['key'] == key), None)
    if hit:
        r = subprocess.run(['bws', 'secret', 'edit', hit['id'], '--value', payload],
                           env=env, capture_output=True, text=True)
    else:
        r = subprocess.run(['bws', 'secret', 'create', key, payload, PROJECT_ID],
                           env=env, capture_output=True, text=True)
    return r.returncode == 0, (r.stderr[:150] if r.returncode != 0 else 'ok')


def verify_rest(domain, user, app_pass):
    # /wp/v2/settings, no /users/me: algunas webs capan /wp/v2/users contra la
    # enumeración de usuarios y devuelven 403 aunque la credencial sea buena.
    # /settings da 401 sin auth y 200 con ella — verdicto fiable pase lo que pase con /users.
    token = base64.b64encode(f'{user}:{app_pass}'.encode()).decode()
    req = urllib.request.Request(
        f'https://{domain}/wp-json/wp/v2/settings',
        headers={'Authorization': f'Basic {token}', 'User-Agent': 'bootstrap-app-pass'})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status == 200, f'HTTP {resp.status}'
    except Exception as e:
        code = getattr(e, 'code', None)
        return False, f'HTTP {code}' if code else f'error: {e}'


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit('uso: bootstrap-app-pass.py <slug|slug=dominio> [...]')
    env = bws_env()
    secrets = bws_list(env)
    results = []
    for arg in args:
        slug, domain = parse_target(arg)
        wp = next((s for s in secrets if s['key'] == f'WP_{slug}'), None)
        if not wp:
            results.append((slug, 'FAIL', f'sin WP_{slug} en BWS'))
            continue
        creds = json.loads(wp['value'])
        url, user, password = creds.get('url'), creds.get('user'), creds.get('pass')
        if not (url and user and password):
            results.append((slug, 'FAIL', f'WP_{slug} incompleto (url/user/pass)'))
            continue
        ok, why = login(url, user, password)
        if not ok:
            results.append((slug, 'FAIL', f'login: {why}'))
            continue
        app_pass, why = create_app_password()
        if not app_pass:
            results.append((slug, 'FAIL', f'app-pass: {why}'))
            continue
        saved, why = save_bws(env, secrets, slug, user, app_pass)
        if not saved:
            results.append((slug, 'FAIL', f'bws: {why}'))
            continue
        verified, detail = verify_rest(domain, user, app_pass)
        results.append((slug, 'OK' if verified else 'WARN', f'guardado en BWS; verify REST {detail}'))
    ab('close')
    print()
    for slug, status, detail in results:
        print(f'{status:5} {slug}: {detail}')
    sys.exit(0 if all(s != 'FAIL' for _, s, _ in results) else 1)


if __name__ == '__main__':
    main()
