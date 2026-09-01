---
cosmos: pueblo
nombre: shopify-toolkit
padre: web/comercio-electronico
resumen: Kit oficial para trabajar contra la API de administracion y las plantillas de una tienda alojada.
---

https://github.com/Shopify/Shopify-AI-Toolkit · MIT · 527★ · último push 2026-08-28 (comprobado 2026-09-01)

```bash
claude plugin install shopify-ai-toolkit@claude-plugins-official
# alternativa sin plugin:
npx skills add Shopify/shopify-ai-toolkit
```

Oficial de la plataforma. Cubre GraphQL y REST de la Admin API, Liquid, los componentes Polaris, OAuth,
webhooks, Billing API, extensiones de checkout y de admin, extensiones de punto de venta y operaciones
masivas. Entra porque la tienda alojada tiene **modelo de datos y lenguaje de plantillas propios**: lo
aprendido en WooCommerce no se traslada, ni al revés.

Gana a `Shopify/liquid-skills` (32★, oficial pero **sin push desde 2026-03-18**, casi seis meses
parado), que además solo cubre la capa de plantillas. Y gana en adopción a su equivalente de la otra
tienda, `woocommerce/agent-skills` (9★) — aunque ese sea el correcto cuando el encargo es WooCommerce.
Los repositorios sueltos de plantillas y de consultas analíticas del mismo ecosistema son **partes de
este**, no huecos distintos.

Ojo: es conocimiento y andamiaje, no un cliente que ejecute nada — para tocar una tienda real hacen
falta credenciales de una app propia con sus permisos, y ahí el gasto vive en el plan de Shopify del
cliente, no aquí. Que sea oficial no lo hace actual: la Admin API versiona por trimestres y una skill
puede citar una versión ya retirada.
