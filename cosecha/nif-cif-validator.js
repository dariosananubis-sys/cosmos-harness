// nif-cif-validator.js — normalización y resolución de NIF/CIF español → slug de negocio.
// Sin dependencias externas (puro y testeable).

// Normaliza un NIF/CIF: mayúsculas + solo alfanumérico. "b-039.72221 " → "B03972221".
export function normalizeNif(v) {
  return String(v || '').toUpperCase().replace(/[^0-9A-Z]/g, '');
}

// Resuelve el slug de una lista de negocios [{slug,nif}] cuyo NIF normalizado coincide.
// Sin NIF o sin coincidencia → null. Útil para mapear un NIF suelto (de una hoja, un
// formulario, un import) a la ficha interna correspondiente sin depender del formato exacto
// con que se tecleó (mayúsculas, guiones, puntos).
export function resolveSlugFromList(list, nif) {
  const key = normalizeNif(nif);
  if (!key) return null;
  const hit = (list || []).find((b) => normalizeNif(b && b.nif) === key);
  return hit ? hit.slug : null;
}
