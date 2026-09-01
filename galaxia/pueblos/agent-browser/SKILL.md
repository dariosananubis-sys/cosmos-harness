---
cosmos: pueblo
nombre: agent-browser
padre: agentes-ia/herramientas
resumen: Navegador real por protocolo de depuracion desde consola: navega, rellena, captura y verifica barato.
---

Estandar de la casa para ver con los ojos. Sesion con nombre estable, cambio de ancho reutilizando
pestana, coste muy inferior al de un servidor de herramientas de navegador.

Alternativa descartada: el agente de navegador que conduce la pagina con un modelo. Es mas autonomo y
mucho mas caro por tarea; se reserva para lo que no se puede describir con selectores.

De la cosecha propia compiten dos y pierden las dos, pero dejan su leccion aqui:
`cosecha/navegador_seguro.py`, una envoltura que nunca reutiliza sesion ajena y comprueba direccion y
ancho antes de fiarse de una medicion —eso es politica de uso de esta herramienta, no otra
herramienta—, y `cosecha/cdp-client.py`, un cliente del mismo protocolo escrito a mano sin
dependencias, util solo si algun dia hace falta hablar el protocolo sin este.
