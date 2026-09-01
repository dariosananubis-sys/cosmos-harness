---
cosmos: pueblo
nombre: evidence
padre: analitica/cuadros-de-mando
resumen: Informes en Markdown con bloques SQL que se compilan a un sitio estatico publicable en cualquier sitio.
---

https://github.com/evidence-dev/evidence - MIT - 6.898 estrellas - ultimo push 2026-08-31
(comprobado por API de GitHub el 2026-09-01).

```bash
npx degit evidence-dev/template mi-informe
cd mi-informe && npm install
```

```markdown
<!-- pages/index.md: Markdown con SQL dentro -->
# Ventas por categoria

```sql ventas
select categoria, count(*) as n, sum(importe) as total
from ventas
where fecha >= '2026-01-01'
group by 1 order by total desc
```

Se vendieron **<Value data={ventas} column=total agg=sum fmt=eur />** en total.

<BarChart data={ventas} x=categoria y=total />
```

```bash
npm run sources     # conecta las fuentes (DuckDB por defecto)
npm run dev         # http://localhost:3000
npm run build       # deja un sitio estatico en build/, que se sube donde sea
```

El otro extremo de `streamlit`: nada que desplegar ni vigilar, la salida es HTML estatico. Se elige
este cuando el informe se **manda** —por correo, en un ZIP, en un hosting cualquiera— y aquel cuando
el informe se **explora**. Y frente a Metabase o Superset, la ventaja que decide en una agencia: el
informe entero vive versionado en Git, asi que se revisa en una PR y se sabe quien cambio que
numero.

Y lo que no hace bien: al ser estatico, los datos son los del momento de compilar. No hay filtros
que consulten en vivo salvo los que el motor de DuckDB en el navegador pueda resolver sobre lo ya
generado, y un informe que se quiere al dia necesita recompilarse y volver a subirse.

Y el aviso que evita el disgusto: **el sitio compilado lleva los datos dentro.** Si el `.parquet` de
origen tiene columnas que no deberian salir de la agencia, salen — cualquiera con el URL las tiene.
Se filtra en el SQL antes de compilar, no en la pagina. Y por lo mismo, `build/` nunca se sube a un
repositorio publico.

Aviso de maquina: es una aplicacion Node con SvelteKit; `npm install` deja unos cuantos cientos de
megas en `node_modules`.
