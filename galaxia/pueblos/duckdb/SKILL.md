---
cosmos: pueblo
nombre: duckdb
padre: ingenieria-datos/motor
resumen: Consulta SQL sobre CSV y Parquet dentro del proceso, derramando a disco cuando no cabe en memoria.
---

Un solo binario, sin servidor. El derrame a disco es lo que lo hace viable con ocho gigas: una
consulta que no cabe se ralentiza en vez de morir.

Descartada la capa de portabilidad entre motores y el traductor de dialectos SQL: utiles, pero son
piezas de este, no huecos propios.
