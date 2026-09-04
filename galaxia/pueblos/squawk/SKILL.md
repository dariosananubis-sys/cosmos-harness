---
cosmos: pueblo
nombre: squawk
padre: saas/contrato
resumen: Revisa la migracion antes de aplicarla y para la que bloquea la tabla o borra sin retorno.
---

https://github.com/sbdchd/squawk · Apache-2.0 · 1.164★ · último push 2026-09-01 (comprobado por API de
GitHub el 2026-09-01). Analizador de migraciones de PostgreSQL.

```bash
npm install -g squawk-cli        # o: pip install squawk-cli
# "brew install squawk" NO existe (ni formula ni tap propio): no lo uses, falla
```

```sql
-- migraciones/0007_añadir_estado.sql
ALTER TABLE pedidos ADD COLUMN estado text NOT NULL DEFAULT 'pendiente';
CREATE INDEX idx_pedidos_estado ON pedidos (estado);
```

```bash
squawk migraciones/0007_*.sql
# ...adding-required-field / disallowed-unique-constraint / require-concurrent-index-creation
squawk --exclude=prefer-text-field migraciones/*.sql    # sale distinto de cero si hay hallazgos
```

Lee el SQL con el analizador real de PostgreSQL y avisa de lo que **bloquea o rompe en producción**:
un índice creado sin `CONCURRENTLY` que retiene un bloqueo sobre la tabla entera, una columna
obligatoria añadida sin plan, un cambio de tipo que reescribe millones de filas, un `DROP` que no
tiene vuelta atrás. En una máquina de pruebas con doscientas filas todo eso pasa en un segundo y no se
ve; en la del cliente es la caída.

Gana a `ariga/atlas` (8.694★), que es el rival grande y hace mucho más —versionado, diff de esquemas,
planes—, por una razón de encaje, no de potencia: aquel es una plataforma con una capa de pago del
mismo fabricante, y esto es un binario que se mete en la tubería en dos minutos y no pide nada. Si el
proyecto necesita gestionar el esquema entero, ahí gana Atlas y hay que decirlo.

Es la puerta que le falta al oficio delante de `dlt` y de cualquier ORM: aquellos generan la
migración, esto decide si se puede aplicar en caliente.

Y lo que no hace bien:

- **Solo PostgreSQL.** MySQL, SQLite o SQL Server no son su terreno y ni lo intenta.
- **Es análisis estático, no conoce tu tabla.** Avisa igual de una tabla de diez filas que de una de
  diez millones, así que hay reglas que en tu caso sobran: se silencian a propósito con `--exclude`,
  no se ignora el rojo entero.
- **No ve lo que genera el ORM en tiempo de ejecución.** Si las migraciones no se guardan como `.sql`,
  hay que exportarlas antes (`sqlmigrate` en Django, `--sql` en Alembic) o esto no mira nada.
- **Pasar el análisis no es tener plan de vuelta atrás.** Que una migración no bloquee no significa que
  sea reversible; eso sigue siendo trabajo de la persona.
