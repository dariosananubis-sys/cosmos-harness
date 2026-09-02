// Origen HTTP donde vive la REST de un sitio WordPress.
//
// La mayoría de sitios tienen WordPress en la raíz del dominio, así que la REST cae en
// `https://<dominio>/wp-json`. Pero no siempre: una web con front legacy sin CMS en la raíz
// puede tener WordPress instalado en un subdirectorio (p.ej. `/blog/`), con la REST en
// `https://<dominio>/blog/wp-json`.
//
// `rest_base` es opcional y solo lo rellenan los sitios así. Sin él, el resultado es idéntico
// al de antes de que existiera este fichero. Conviene centralizar esta función: si la URL se
// construye en varios sitios del pipeline (publicar, verificar, adjuntar imagen...) y arreglas
// solo uno, el ciclo publica bien pero verifica contra una URL que no existe.
export function restBase(site) {
  return site.rest_base ? String(site.rest_base).replace(/\/+$/, '') : `https://${site.domain}`;
}
