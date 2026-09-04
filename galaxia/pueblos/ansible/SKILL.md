---
cosmos: pueblo
nombre: ansible
padre: infraestructura/despliegue
resumen: Configura servidores existentes por SSH sin agente; declarativo, YAML, idempotente.
---

https://github.com/ansible/ansible · GPL-3.0 · 70.568★ · último push 2026-09-02 (comprobado 2026-09-03)

```bash
brew install ansible
```

```bash
# playbook minimo: instala nginx y lo deja arrancado en los hosts del inventario
# ---
# - hosts: RUTA/AL/INVENTARIO
#   become: true
#   tasks:
#     - name: instalar nginx
#       apt: {name: nginx, state: present}
#     - name: servicio activo
#       service: {name: nginx, state: started, enabled: true}

ansible-playbook -i inventario.ini playbook.yml --check   # dry-run: que cambiaria, sin tocar nada
ansible-playbook -i inventario.ini playbook.yml
```

Es la respuesta al hallazgo de que este nicho no tenía ninguna herramienta de infraestructura
como código: sin ella, la configuración de un servidor vive en la memoria de quien lo tocó por
SSH la última vez, y no hay forma de reproducirla ni de auditarla. Gana a `opentofu`/`terraform`
en que **no aprovisiona recursos nuevos, configura los que ya existen** — por SSH, sin agente
que instalar en el destino — mientras que `opentofu` crea y destruye infraestructura declarada
contra un proveedor cloud. La frontera práctica: `opentofu` para que el servidor exista, `ansible`
para que llegue ya configurado.

Ojo: es idempotente **si los módulos usados lo son** — una tarea con `shell:`/`command:` crudo se
ejecuta cada vez, no solo cuando hace falta, salvo que se le añada `changed_when`/`creates`
explícito. `--check` no detecta todo lo que un cambio real dispararía (algunas tareas no soportan
modo simulación). Y un inventario grande sin `--limit` puede aplicar un cambio a producción
entera de una tacada: siempre `--check` primero contra el alcance real.
