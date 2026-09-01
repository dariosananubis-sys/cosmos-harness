---
cosmos: pueblo
nombre: ghidra
padre: ciberseguridad/analisis/malware
resumen: Desensambla y decompila un binario sin fuente, sin licencia de miles de euros.
---

https://github.com/NationalSecurityAgency/ghidra · Apache-2.0 · 74.192★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
brew install ghidra   # arrastra la JDK que necesita
```

```bash
# modo sin interfaz: analiza y ejecuta un guion, que es como se usa por lotes
"$(brew --prefix)/share/ghidra/support/analyzeHeadless" \
  ./proyecto_ghidra CasoEjemplo \
  -import ./muestra.bin \
  -postScript ListFunctions.java \
  -deleteProject
```

Trae decompilador real, no solo listado de instrucciones, y por eso gana a `radareorg/radare2`
(24.697★) como puerta de entrada: r2 y Cutter son excelentes y de consola primero, pero quien no
vive ya dentro de r2 llega antes al pseudocódigo aquí. Frente a IDA Pro, la comparación es de
precio: aquello es licencia comercial de miles de euros, esto es Apache-2.0.

Ojo: el decompilador **inventa nombres y tipos**. Su salida en C es una hipótesis legible, no el
código original — un `undefined4` mal deducido cambia el sentido de una condición entera. Toda
conclusión que vaya a un informe se contrasta contra el desensamblado. Y el análisis inicial de un
binario grande son minutos y varios GB de RAM: no es una herramienta de tubería rápida.

Contexto de uso legítimo: análisis de muestra propia o entregada en un encargo, investigación y
formación. Nunca ingeniería inversa de software de terceros fuera de lo que permita su licencia.
