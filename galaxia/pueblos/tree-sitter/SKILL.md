---
cosmos: pueblo
nombre: tree-sitter
padre: extraccion
resumen: Analiza sintaxis de forma incremental y tolerante a errores mientras se edita.
---

https://github.com/tree-sitter/tree-sitter · MIT · 26.815★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
pip install tree-sitter tree-sitter-python      # una gramática por lenguaje, aparte
```

```python
from tree_sitter import Language, Parser
import tree_sitter_python as tspython

parser = Parser(Language(tspython.language()))
arbol = parser.parse(b"def suma(a, b):\n    return a + b\n")
print(arbol.root_node.sexp())
print("con errores:", arbol.root_node.has_error)
```

Análisis incremental y **tolerante a errores**: sigue devolviendo un árbol usable con el fichero a
medio escribir, que es lo que permite consultarlo mientras se edita. Es el sustrato de media docena de
herramientas del catálogo, no una más.

Gana a `antlr/antlr4` (18.989★, último push 2026-02-16) para el caso de leer código ajeno: ANTLR sigue
siendo mejor para **implementar un lenguaje entero** desde su gramática formal, pero exige gramática
completa y no tolera entrada rota. Queda citado para ese caso y no entra.

Ojo: el paquete base no trae ningún lenguaje — hay que instalar la gramática de cada uno
(`tree-sitter-python`, `tree-sitter-javascript`…) y las versiones de gramática y núcleo **se
desincronizan**: un `Language()` que falla con un error de ABI es eso, no un fallo de código. Y
`has_error` hay que mirarlo a mano: el árbol de un fichero roto se parece mucho al de uno bueno.
