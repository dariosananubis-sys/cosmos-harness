---
cosmos: pueblo
nombre: sops
padre: infraestructura
resumen: Cifra solo los valores del fichero de configuracion para poder versionarlo sin servidor de secretos.
---

https://github.com/getsops/sops · MPL-2.0 · 22.982★ · push 2026-08-31 (comprobado 2026-09-01)

```bash
brew install sops age

age-keygen -o ~/.config/sops/age/keys.txt      # la clave privada se queda FUERA del repositorio
export SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt
CLAVE_PUB=$(grep 'public key' ~/.config/sops/age/keys.txt | awk '{print $NF}')

sops --encrypt --age "$CLAVE_PUB" --encrypted-regex '^(password|token|secret)' \
  config.yaml > config.enc.yaml     # este SI se commitea

sops --decrypt config.enc.yaml | head
sops config.enc.yaml               # abre el editor y vuelve a cifrar al guardar
```

Gana a Vault y a los gestores alojados cuando **no hay equipo que mantenga un servidor de secretos**:
aquí no hay servicio que levantar, ni que vigilar, ni que pagar. Y gana a `git-crypt` porque cifra
**solo los valores** —las claves siguen en claro—, así que el `git diff` de un cambio de
configuración sigue siendo legible y revisable en vez de un bloque binario.

De la cosecha propia quedan fuera tres clientes de gestores alojados: `scripts/bws-token-set.sh`
(guarda y rota el testigo comprobando antes que funciona), `scripts/bws-secret-get.js` (busca un
secreto por clave en varios proyectos) y `scripts/gh-token-set.sh` (deja el testigo del repositorio
en el ayudante de credenciales del sistema). Son clientes de un servicio concreto, con su cuenta y su
plan; esto cubre el hueco sin depender de ninguno.

Ojo: no hay rotación ni caducidad. Si un secreto se filtra, hay que rotarlo a mano en el origen —y
el valor antiguo sigue descifrable en todo el historial de Git para quien tenga la clave. Sin
`--encrypted-regex`, cifra también las claves y el diff deja de valer. Y la clave privada perdida es
el fichero perdido: al vault, con copia.
