---
cosmos: pueblo
nombre: bloodhound
padre: ciberseguridad/ofensiva/post-explotacion
resumen: Convierte el directorio en un grafo y saca el camino corto a administrador.
---

https://github.com/SpecterOps/BloodHound · Apache-2.0 · 3.368★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
# la interfaz corre en contenedores; el recolector es un binario aparte
curl -L https://ghst.ly/getbhce | docker compose -f - up
```

```bash
# 1) recoger desde una máquina del dominio (SharpHound), dentro del alcance
#    produce un .zip que se sube por la interfaz web
# 2) consulta típica en la interfaz, en Cypher: caminos a administrador de dominio
MATCH p=shortestPath(
  (u:User {owned:true})-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMINIO-EJEMPLO"})
) RETURN p
```

Convierte Active Directory en un grafo y saca el camino corto a administrador que a ojo es
invisible. El de al lado (`impacket`) **ejecuta**; este **decide qué ejecutar**. Por eso no se
solapan: uno responde *cómo* y el otro responde *adónde*. Se usa la edición comunitaria (BloodHound
CE), gratuita; la de empresa añade seguimiento continuo que aquí no hace falta.

Ojo: es una herramienta de **análisis**, no toca el objetivo — el ruido y el riesgo están en el
recolector (SharpHound), que consulta el directorio y deja rastro. Y el grafo vale lo que valga la
recogida: si SharpHound corrió con una cuenta de pocos privilegios, faltan aristas y un camino que
existe no aparece — una ausencia de camino no es prueba de que no lo haya. Solo dentro de un dominio
del alcance de un encargo autorizado.
