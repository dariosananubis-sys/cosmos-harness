---
cosmos: pueblo
nombre: stripe-agent-toolkit
padre: saas/cobro
resumen: Kit oficial de la pasarela para cobrar, suscribir y atender avisos desde codigo o desde un agente.
---

https://github.com/stripe/ai · MIT · 1.784★ · push 2026-08-30 (comprobado 2026-09-01)

El repositorio `stripe/agent-toolkit` **se renombró** a `stripe/ai`; el redirect sigue vivo. Los
paquetes publicados mantienen el nombre antiguo.

```bash
pip install stripe-agent-toolkit          # o: npm install @stripe/agent-toolkit

python - <<'PY'
from stripe_agent_toolkit.crewai.toolkit import StripeAgentToolkit
kit = StripeAgentToolkit(
    secret_key="<CLAVE_SECRETA_DE_PRUEBAS>",          # usa siempre la clave de test
    configuration={"actions": {"payment_links": {"create": True}}})
print([t.name for t in kit.get_tools()])
PY

# y como complemento del agente, con las herramientas ya empaquetadas:
claude plugin install stripe@claude-plugins-official
```

Oficial, con bibliotecas reales en Python y TypeScript y adaptadores para los orquestadores de
agentes más usados — no es un fichero de instrucciones. Cubre pago, suscripción, enlaces de pago,
avisos salientes y la autenticación reforzada del cliente que exige la **PSD2** en la Unión Europea,
que es donde se rompen las integraciones caseras. Gana a los servidores de herramientas de Stripe hechos por la comunidad —que envuelven la misma API
sin respaldo del emisor— y a llamar al SDK `stripe` a pelo por lo mismo: la **configuración de
acciones permitidas**. Al agente se le da un subconjunto explícito de operaciones, no la clave
entera. La alternativa del otro proveedor de pagos (`paypal-agent-toolkit`) cubre menos operaciones
y no trae adaptadores para tantos orquestadores.

Nota de coste, que no es menor: **el kit es gratis, pero la pasarela cobra comisión por
transacción**. Eso es una decisión de negocio del cliente, no una instalación, y no se contrata sin su
orden.

Ojo: una clave secreta en manos de un agente es dinero real en manos de un texto que alguien puede
influir. Regla dura: **clave de pruebas mientras se desarrolla**, lista de acciones mínima, y todo lo
que mueva dinero de verdad con confirmación humana antes. Y esto cobra; **contar el consumo es
`lago` y emitir la factura legal es `gobl`** — la pasarela no hace ni una cosa ni la otra.
