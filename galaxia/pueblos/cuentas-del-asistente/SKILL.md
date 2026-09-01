---
cosmos: pueblo
nombre: cuentas-del-asistente
padre: agentes-ia/coste
resumen: Varias cuentas del mismo asistente vivas a la vez: cual gasta la cuota, que ninguna caduque, y matar las zombis.
---

`cosecha/claude-cuenta.sh`, `cosecha/mantener-sesiones-claude.sh` y `cosecha/reap-claude-orphans.sh`
— herramientas propias, no de GitHub.

```bash
chmod +x cosecha/claude-cuenta.sh cosecha/mantener-sesiones-claude.sh cosecha/reap-claude-orphans.sh
export CLAUDE_ACCOUNTS_DIR="$HOME/.claude-accounts"     # una subcarpeta por cuenta
cosecha/claude-cuenta.sh trabajo --model opus           # abre esa cuenta; el resto de flags pasan a claude
cosecha/mantener-sesiones-claude.sh --dry-run           # a cuáles tocaría para que no caduquen
cosecha/reap-claude-orphans.sh --dry                    # qué zombis mataría
```

Cada proceso gasta la cuota de la credencial que tenga cargada, así que arrancar siempre por
`claude-cuenta.sh` deja todas las ventanas gastando **la cuenta elegida** y las demás iniciadas en
reposo, a coste cero. Aísla por `CLAUDE_CONFIG_DIR` y no toca el llavero compartido, que es por donde
dos ventanas rotando el mismo token acaban revocando la sesión. Un alias mal escrito corta con error
en vez de abrir otra cuenta en silencio.

`mantener-sesiones-claude.sh` existe porque el refresh token dura ~9 días: una cuenta que nadie usa
pierde la sesión y pide `/login` a mano el día que hace falta. La renueva con la inferencia más barata
que existe (modelo pequeño, esfuerzo bajo, cero herramientas, cero persistencia) y solo cada varios
días. `reap-claude-orphans.sh` mata lo que quedó colgando de un proceso muerto (`PPID=1`) y sus
servidores MCP; en una máquina de 8 GB esos restos llenan el intercambio y provocan más caídas.

Distinto de preguntar por la cuota (`quota-oficial`): aquello dice cuánta queda, esto decide de quién
sale. Gana a `claude /login` a mano en que el cambio de cuenta no arriesga la sesión de la otra.

Ojo: `auth status` **no renueva** el OAuth, solo inspecciona — por eso mantener viva una cuenta parada
exige gastar una inferencia mínima, no basta con consultarla. Y el refresh token **rota**: escribirlo
a mano desde fuera deja la cuenta sin sesión.
