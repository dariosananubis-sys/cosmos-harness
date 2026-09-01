---
cosmos: pueblo
nombre: openfga
padre: saas
resumen: Decide quien puede ver que en un producto multiinquilino, y trae pruebas que lo demuestran.
---

https://github.com/openfga/openfga · Apache-2.0 · 5.685★ · último push 2026-08-31 (comprobado por API
de GitHub el 2026-09-01). Proyecto de la CNCF, implementación abierta del modelo Zanzibar.

```bash
brew install openfga/tap/fga
docker run -d --name openfga -p 8080:8080 openfga/openfga run     # memoria; para produccion, Postgres
```

```yaml
# tienda.fga.yaml — el modelo Y sus pruebas, en el mismo fichero
model: |
  model
    schema 1.1
  type usuario
  type organizacion
    relations
      define miembro: [usuario]
  type documento
    relations
      define propietaria: [organizacion]
      define editor: [usuario]
      define lector: [usuario] or editor or miembro from propietaria

tuples:
  - user: usuario:ana         ; relation: miembro    ; object: organizacion:cliente-a
  - user: organizacion:cliente-a ; relation: propietaria ; object: documento:informe-1

tests:
  - name: aislamiento entre inquilinos
    check:
      - user: usuario:ana
        object: documento:informe-1
        assertions: { lector: true }
      - user: usuario:beto            # de otra organizacion: NO debe poder
        object: documento:informe-1
        assertions: { lector: false, editor: false }
```

```bash
fga model test --tests tienda.fga.yaml     # sale distinto de cero si una asercion falla
```

Este pueblo entra porque `casdoor` dejó el hueco escrito: allí se resuelve **quién eres**, y el
aislamiento por inquilino se quedó sin herramienta. Esto resuelve **qué puedes**, que es la otra
mitad y la que produce la fuga: un `WHERE tenant_id = ?` olvidado en una consulta de treinta.

Gana a `casbin/casbin`, el rival directo y mucho más instalado, en lo que decide aquí: aquel evalúa
políticas de roles y atributos, y para «esta persona ve este documento porque pertenece a la
organización que lo posee» hay que escribir la consulta a mano. Esto modela **relaciones**, así que la
herencia sale del modelo y no de código repartido. Y sobre todo, `fga model test` convierte el
aislamiento en una **prueba que se puede ver fallar**: se escribe el caso del inquilino que NO debe
ver, y si algún día lo ve, la tubería se pone roja. Un documento que dice «usa fila a fila» no hace
eso.

Y lo que no hace bien:

- **Es un servicio más que mantener**, con su base de datos y su latencia por cada comprobación. Para
  un panel con dos administradores es desproporcionado: ahí manda `panel-auth-cookie`.
- **No guarda tus datos, guarda relaciones.** Hay que escribir las tuplas cuando algo cambia de dueño;
  si el código olvida borrar una tupla al eliminar un documento, el permiso sobrevive al objeto.
- **Un modelo con muchos saltos indirectos se vuelve lento** y difícil de razonar; hay que medir con
  datos reales, porque el coste no se ve con tres tuplas de ejemplo.
- **La imagen de un solo contenedor guarda en memoria**: al reiniciar, todo el modelo y todas las
  tuplas desaparecen. Para cualquier cosa que no sea probar, base de datos aparte.
- No sustituye a la comprobación en la base de datos: la seguridad a nivel de fila de Postgres sigue
  siendo la red de abajo, y esta es la de arriba.
