---
cosmos: pueblo
nombre: yara
padre: ciberseguridad/analisis/malware
resumen: Identifica familias por patrones sobre fichero y memoria, donde el de fuente no llega.
---

https://github.com/VirusTotal/yara · BSD-3-Clause · 9.845★ · último push 2026-08-25 (comprobado 2026-09-01)

```bash
brew install yara
git clone --depth 1 https://github.com/Yara-Rules/rules.git   # corpus base, ver aviso
```

```bash
# una regla mínima, escrita a mano
cat > ejemplo.yar <<'YAR'
rule cadena_de_ejemplo {
  meta:
    autor = "auditoria"
  strings:
    $a = "MARCADOR-DE-EJEMPLO" ascii wide
    $b = { 4D 5A 90 00 }
  condition:
    $b at 0 and $a
}
YAR

# recursivo sobre un directorio de muestras
yara -r -s ejemplo.yar ./muestras/

# sobre la memoria de un proceso vivo
yara ejemplo.yar 1234
```

Entra el **motor**, no el corpus. Frontera con el analizador de fuente (`semgrep`): aquel lee
código, este lee bytes, y por eso alcanza a un binario empaquetado o a un volcado de memoria donde
el otro no tiene nada que leer. Frente a `sigma-cli`, mismo par contenido/motor pero otro sustrato:
Sigma casa sobre registros de eventos, YARA sobre ficheros y memoria.

Ojo: el corpus más citado, `Yara-Rules/rules` (4.882★), **lleva sin publicar desde 2024-04-17**. Se
usa como base y se complementa con corpus vivos (`reversinglabs/reversinglabs-yara-rules`, el de
Trellix ATR) antes de fiarse de él en producción. Y una regla mal acotada es un generador de falsos
positivos que después nadie revisa: acotar siempre con `filesize` o con una condición de cabecera
como la del ejemplo, y probar la regla contra un corpus limpio antes de desplegarla.
