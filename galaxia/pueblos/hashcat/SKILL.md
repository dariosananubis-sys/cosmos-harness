---
cosmos: pueblo
nombre: hashcat
padre: ciberseguridad/ofensiva/post-explotacion
resumen: Recuperacion de claves por GPU; el estandar tras volcar hashes con bloodhound u otros.
---

https://github.com/hashcat/hashcat · MIT · 26.695★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
brew install hashcat
```

```bash
# ataque de diccionario contra un fichero de hashes obtenido en una auditoria autorizada
hashcat -m 0 -a 0 hashes.txt rockyou.txt

# ataque de mascara (fuerza bruta acotada) para contraseñas de 8 digitos
hashcat -m 0 -a 3 hashes.txt ?d?d?d?d?d?d?d?d
```

Es el paso que viene después de conseguir hashes en una auditoría autorizada (volcado de
credenciales, `bloodhound` para el camino de ataque en AD, un dump de base de datos): sin
`hashcat`, un hash capturado no dice nada sobre si la contraseña es débil. Gana a `John the
Ripper` en velocidad bruta cuando hay GPU disponible — su motor OpenCL/CUDA prueba órdenes de
magnitud más combinaciones por segundo que una CPU, y soporta más de 300 tipos de hash.

Ojo: sin GPU dedicada el rendimiento cae mucho y se acerca al de una CPU normal — en un portátil
sin GPU discreta, un ataque de diccionario grande puede tardar horas donde una máquina con GPU
tarda minutos. Solo sobre hashes obtenidos con autorización explícita del cliente o del alcance
del pentest: usarlo contra credenciales ajenas sin permiso es delito. Un hash con sal por usuario
(bcrypt, scrypt bien configurado) hace inviable la fuerza bruta a cualquier velocidad razonable —
la eficacia real depende del algoritmo de hash, no solo de la potencia de cómputo.
