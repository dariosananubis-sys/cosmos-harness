---
cosmos: pueblo
nombre: metasploit
padre: ciberseguridad/ofensiva/explotacion
resumen: Motor de explotacion con modulos, cargas y post-explotacion en una base actualizada.
---

https://github.com/rapid7/metasploit-framework · BSD-3-Clause (leído en `COPYING`; la API de GitHub la reporta como `NOASSERTION`) · 38.926★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
# no hay fórmula de Homebrew; el instalador oficial (o el cask 'metasploit')
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod +x msfinstall && ./msfinstall
```

```bash
# flujo mínimo por consola de recursos, todo contra un objetivo del alcance
msfconsole -q -x "
use auxiliary/scanner/smb/smb_version;
set RHOSTS 198.51.100.0/24;
run;
exit
"
```

Solo el **framework**, que es libre. Gana su hueco por tener la base de módulos actualizada a diario
y por integrar exploit, carga y post-explotación en un solo motor. La edición «Pro» de Rapid7
(interfaz, informes, trabajo en equipo) es un producto de pago aparte que **no se usa ni se
presupuesta** — importa no confundir uno con otro al cotizar a un cliente.

Ojo, doble uso declarado: esta herramienta solo se usa en **auditoría contratada, laboratorio y
competición**, nunca fuera del alcance escrito. Y en lo técnico: muchos módulos son ruidosos y
cualquier EDR moderno caza sus cargas por defecto, así que un fallo no significa «no es vulnerable»,
significa «esta carga no pasó». `RHOSTS` mal puesto lanza contra una red que no es la del encargo —
verificar el alcance antes de cada `run`.
