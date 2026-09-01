---
cosmos: pueblo
nombre: coraza
padre: ciberseguridad/defensiva/codigo-defensivo
resumen: Cortafuegos de aplicacion empotrado en el proceso, con las reglas del nucleo de OWASP.
---

https://github.com/corazawaf/coraza · Apache-2.0 · 3.778★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
go get github.com/corazawaf/coraza/v3
```

```go
// el mínimo: motor con las reglas del núcleo de OWASP delante de un manejador HTTP
import (
    "net/http"
    "github.com/corazawaf/coraza/v3"
    txhttp "github.com/corazawaf/coraza/v3/http"
)

waf, err := coraza.NewWAF(coraza.NewWAFConfig().
    WithDirectives(`
        SecRuleEngine On
        Include @coraza.conf-recommended
        Include @crs-setup.conf.example
        Include @owasp_crs/*.conf
    `))
if err != nil { panic(err) }

http.ListenAndServe(":8080", txhttp.WrapHandler(waf, miManejador))
```

Gana a `owasp-modsecurity/ModSecurity` (9.759★, vivo, último push 2026-07-28) para este país
concreto porque **se empotra como biblioteca dentro de la aplicación** en vez de exigir un módulo
nativo de Apache o nginx aparte: validación en la frontera de verdad, en el mismo proceso, y
compatible con la sintaxis de reglas que ya existe.

Ojo: un cortafuegos de aplicación es una **segunda barrera**, no la primera. Las reglas del núcleo
de OWASP en modo estricto generan falsos positivos sobre cualquier aplicación real, así que se
despliega primero en modo de solo detección (`SecRuleEngine DetectionOnly`), se afinan exclusiones
con tráfico propio y solo después se bloquea. Poner esto delante y dejar de sanear la entrada es
cambiar un fallo por otro más difícil de ver.
