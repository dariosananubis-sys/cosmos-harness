---
cosmos: pueblo
nombre: anchor
padre: blockchain
resumen: La otra cadena: genera la validacion de cuentas y el cliente desde la interfaz, que es donde esta el fallo tipico.
---

https://github.com/otter-sec/anchor - Apache-2.0 - 5.125 estrellas - ultimo push 2026-09-01
(comprobado por API de GitHub el 2026-09-01). El repositorio cambio de organizacion: el antiguo
`coral-xyz/anchor` redirige aqui.

```bash
sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"
cargo install --git https://github.com/coral-xyz/anchor avm --locked
avm install latest && avm use latest
```

```bash
anchor init contador && cd contador
anchor build
anchor test                       # levanta un validador local y corre las pruebas en TypeScript
solana-test-validator &           # el nodo local, a mano
```

```rust
#[program]
pub mod contador {
    use super::*;
    pub fn incrementar(ctx: Context<Incrementar>) -> Result<()> {
        ctx.accounts.contador.n += 1;
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Incrementar<'info> {
    #[account(mut, has_one = duenyo)]      // la comprobacion la genera la macro
    pub contador: Account<'info, Contador>,
    pub duenyo: Signer<'info>,
}
```

Es a Solana lo que `foundry` es a Ethereum, y entra porque el nicho no puede ser de una sola cadena.
Gana a escribir el programa en Rust nativo con el SDK a pelo —que es la alternativa real— porque las
macros generan la comprobacion de cuentas, la serializacion y el cliente en TypeScript a partir de
la interfaz declarada. Y ahi esta el motivo de fondo: el error mas repetido en auditorias de Solana
es aceptar una cuenta que no se ha comprobado, y este marco lo elimina por construccion.

Y lo que no hace bien: "por construccion" tiene letra pequena. `AccountInfo` y `UncheckedAccount`
saltan todas las comprobaciones, y un `#[account(mut)]` sin `has_one` ni `seeds` no valida nada del
duenyo. El falso verde es creer que usar Anchor ya cierra la clase entera de fallo: la cierra solo
en las cuentas que declaras con restricciones.

Aviso de dinero: `anchor test` y `solana-test-validator` corren en local y no cuestan nada.
`anchor deploy` contra la red real si: desplegar un programa cuesta un deposito de renta
proporcional al tamano del binario, y no es simbolico. En `devnet` se pide gratis por `solana
airdrop`.
