---
cosmos: pueblo
nombre: rxdb
padre: moviles
resumen: Base de datos local primero que replica en segundo plano: la aplicacion lee y escribe sin esperar a la red.
---

https://github.com/pubkey/rxdb · Apache-2.0 · 23.371★ · último push 2026-09-01 (comprobado por API de GitHub el 2026-09-01).

```bash
npm install rxdb rxjs
```

```js
import { createRxDatabase, addRxPlugin } from 'rxdb';
import { getRxStorageLocalstorage } from 'rxdb/plugins/storage-localstorage';
import { replicateRxCollection } from 'rxdb/plugins/replication';

const db = await createRxDatabase({ name: 'local', storage: getRxStorageLocalstorage() });
await db.addCollections({
  tareas: { schema: { version: 0, primaryKey: 'id', type: 'object',
    properties: { id: { type: 'string', maxLength: 40 }, texto: { type: 'string' },
                  hecha: { type: 'boolean' } }, required: ['id', 'texto'] } }
});

await db.tareas.insert({ id: '1', texto: 'ejemplo', hecha: false });   // instantaneo, sin red
db.tareas.find().$.subscribe(docs => console.log(docs.length));         // reactivo

replicateRxCollection({                                                 // sincroniza en segundo plano
  collection: db.tareas, replicationIdentifier: 'tareas-http',
  push: { handler: async rows => { /* POST a tu API */ return []; } },
  pull: { handler: async cp  => { /* GET desde tu API */ return { documents: [], checkpoint: cp }; } },
});
```

Corre en cualquier entorno de ejecucion de JavaScript —movil, web y servidor— y replica contra el
servicio que ya exista, sin atarse a un proveedor. Gana a `Nozbe/WatermelonDB` (11,8k estrellas, MIT)
y a `realm/realm-kotlin`/`realm-swift` por dos cosas: aquel no recibe un push desde agosto de 2025, y
Realm ata el proyecto a un proveedor concreto. La excepcion honesta: con conjuntos de datos enormes y
necesidad de cargar fila a fila en React Native puro, WatermelonDB sigue siendo mejor.

Y lo que no hace bien, y es importante antes de prometerlo:

- **Parte del producto es de pago.** El nucleo es Apache-2.0, pero varios complementos (algunos
  almacenamientos, cifrado, y el aplanado de estado) estan bajo licencia premium de suscripcion. Hay
  que mirar que complemento necesita el proyecto ANTES de decidir, no despues.
- **La replicacion no resuelve los conflictos por ti.** Da los enganches; la estrategia de fusion la
  escribes tu, y ahi es donde se pierden datos si se despacha con "el ultimo gana".
- **Migrar el esquema exige escribir la migracion.** Cambiar `version: 0` sin `migrationStrategies`
  deja la base local del usuario inservible en su aparato, donde no puedes tocarla.
