---
cosmos: pueblo
nombre: atomic-red-team
padre: ciberseguridad/gobierno
resumen: Ejecuta de verdad cada tecnica del catalogo para ver si la deteccion salta.
---

https://github.com/redcanaryco/atomic-red-team · MIT · 12.474★ · último push 2026-08-31 (comprobado 2026-09-01)

```powershell
# en la máquina de laboratorio, nunca en producción de nadie
git clone --depth 1 https://github.com/redcanaryco/atomic-red-team.git
Install-Module -Name invoke-atomicredteam -Scope CurrentUser
Import-Module invoke-atomicredteam
```

```powershell
# ver qué prueba hace una técnica ATT&CK antes de lanzarla
Invoke-AtomicTest T1059.001 -ShowDetailsBrief

# ejecutarla, comprobar en el SIEM si saltó la alerta, y limpiar el rastro
Invoke-AtomicTest T1059.001 -TestNumbers 1
Invoke-AtomicTest T1059.001 -TestNumbers 1 -Cleanup
```

No es una lista de comprobación: son **pruebas ejecutables mapeadas 1:1** a las técnicas del marco
público ATT&CK. Gana a `mitre-attack/attack-navigator` (2.451★) para validar la defensa porque
Navigator es una capa de anotación —pinta qué cubres sobre la matriz— y esto **lo comprueba de
verdad**: lanza la técnica y miras si tu detección salta.

Ojo, es el pueblo más peligroso de manejar mal de todo el nicho: **ejecuta acciones ofensivas
reales** (crea usuarios, escribe en el registro, lanza procesos). Se corre solo en laboratorio
aislado, con el `-Cleanup` de cada prueba comprobado, y nunca contra la infraestructura de un
cliente en producción. Segundo aviso: si tu detección **no salta**, puede ser que no exista o que la
prueba no la tocara — leer el detalle de cada técnica para saber qué se estaba ejercitando de verdad.
