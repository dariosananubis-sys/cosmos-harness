---
cosmos: pueblo
nombre: scancode
padre: cumplimiento/licencias
resumen: Escanea codigo fuente linea a linea y encuentra la licencia aunque no este declarada en ningun fichero central.
---

https://github.com/aboutcode-org/scancode-toolkit · Apache-2.0 AND CC-BY-4.0 (el código bajo
Apache-2.0, los datos de licencias bajo CC-BY-4.0; leído en su `NOTICE`) · 2.617★ · último push
2026-09-04 (comprobado 2026-09-04, API de GitHub y `commits/HEAD.atom`: el último commit de HEAD —la
rama `develop`— es de 2026-08-28, el push más reciente es de otra rama; no archivado)

```bash
pipx install scancode-toolkit
```

```bash
# escaneo de licencias, autoria y copyright, con salida JSON para tuberia
scancode -clip --json-pp resultado.json ./proyecto

# solo licencias, en paralelo con 4 procesos
scancode -l -n 4 --json resultado.json ./proyecto
```

`ort` también lo invoca por dentro como escáner de ficheros, y ahí está la frontera con él: `ort`
resuelve el **grafo de dependencias** del gestor de paquetes y aplica una política de licencias sobre
lo declarado; `scancode` mira el **texto de cada fichero** del árbol, incluido el código copiado que
no aparece en ningún manifiesto. Se encadenan: `ort` para la tubería de dependencias, `scancode`
cuando hay que auditar el código que está dentro del repositorio.

`fossology` **usa este motor por dentro** para detectar licencias en su interfaz de revisión humana
— `scancode` es el escáner suelto, de línea de comandos, sin la base de datos ni el flujo de decisión
firmada que aporta `fossology` encima. Se elige este cuando lo que hace falta es el resultado en una
tubería automática; se elige `fossology` cuando el resultado lo tiene que dar por bueno una persona
con nombre y fecha.

Gana a `reuse` en alcance: `reuse` solo comprueba que cada fichero **declara** su licencia en una
cabecera o en `REUSE.toml`; `scancode` **detecta** la licencia por el texto del fichero aunque nadie
la haya declarado, con un motor de coincidencia de patrones entrenado sobre miles de textos de
licencia conocidos. Es el que encuentra la licencia copiada de un ejemplo sin cabecera, no solo el
fichero sin declarar.

Ojo: el escaneo de un árbol grande es **lento** — el motor de coincidencia recorre cada fichero de
texto contra su base de patrones, y en un repositorio con dependencias vendorizadas dentro (una
carpeta `vendor/` o `node_modules/` sin excluir) el tiempo se dispara sin avisar. Excluir esas
carpetas con `--ignore` antes de lanzar, no después de esperar. Y el falso verde de este en concreto:
una licencia detectada con baja puntuación de coincidencia (`--license-score`) es una pista, no una
certeza — un comentario que menciona "MIT" de pasada puede puntuar bajo y no ser la licencia real del
fichero.
