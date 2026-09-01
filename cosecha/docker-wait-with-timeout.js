// docker-wait-with-timeout.js — límite duro para container.wait() de dockerode.
// Sin límite, un contenedor colgado (proceso zombie, red externa caída, un login que
// espera para siempre) deja `container.wait()` esperando indefinidamente — si ese
// contenedor ocupa el único slot de una cola serial/singleton, la cola entera se congela
// sin auto-recuperación. Al vencer el timeout, se mata el contenedor y se lanza el error:
// quien orqueste puede entonces marcar el job como failed y liberar el slot.
//
// Dep-free (no importa dockerode): `container` solo necesita .wait()/.stop()/.remove()
// (subconjunto de la interfaz dockerode) → testeable con un mock plano, sin Docker real.

/**
 * waitWithTimeout(container, timeoutMs, label): espera al contenedor con límite.
 * Al vencer (o si wait() rompe) → stop + remove del contenedor y lanza.
 * @param {{wait: Function, stop: Function, remove: Function}} container interfaz dockerode
 * @param {number} timeoutMs
 * @param {string} label  para el mensaje de error
 * @returns {Promise<{StatusCode: number}>}
 */
export async function waitWithTimeout(container, timeoutMs, label) {
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(
      () => reject(new Error(`timeout: superó ${Math.round(timeoutMs / 60000)} min`)),
      timeoutMs,
    );
  });
  try {
    return await Promise.race([container.wait(), timeout]);
  } catch (err) {
    await container.stop({ t: 5 }).catch(() => {});
    await container.remove({ force: true }).catch(() => {});
    throw new Error(`contenedor ${label} abortado: ${err.message}`);
  } finally {
    clearTimeout(timer);
  }
}
