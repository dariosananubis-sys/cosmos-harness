---
cosmos: pueblo
nombre: subfinder
padre: ciberseguridad/ofensiva/reconocimiento
resumen: Descubre subdominios por fuentes pasivas (APIs, certificados), sin tocar el objetivo.
---

https://github.com/projectdiscovery/subfinder · MIT · 14.365★ · último push 2026-08-31 (comprobado 2026-09-03)

```bash
brew install subfinder
```

```bash
# descubrimiento pasivo de subdominios de un dominio del alcance, sin enviarle trafico directo
subfinder -d objetivo-del-alcance.example -silent -o subdominios.txt

# encadenado con httpx para quedarse solo con los que estan vivos
subfinder -d objetivo-del-alcance.example -silent | httpx -mc 200
```

Frontera con `amass`: los dos hacen descubrimiento pasivo por fuentes externas (certificados
Transparency Log, motores de búsqueda, APIs de terceros) sin enviar tráfico directo al objetivo,
pero `subfinder` es más rápido y más simple de configurar — pensado para correr en cadena dentro
de un pipeline (`| httpx | nuclei`) — mientras `amass` cubre más fuentes y suma mapeo de
infraestructura (ASN, relaciones de red) a costa de ser más lento y más pesado de ajustar. Para un
reconocimiento rápido de superficie, `subfinder`; para un mapeo exhaustivo de un objetivo grande,
`amass`.

Ojo: el resultado depende de qué fuentes tengan clave de API configurada (`~/.config/subfinder`)
— sin claves, varias fuentes de pago quedan mudas y el listado sale incompleto sin avisarlo como
tal. Es reconocimiento pasivo: no encuentra subdominios que no estén en ningún registro público
(certificados, DNS histórico), así que un subdominio interno sin certificado público no aparece.
