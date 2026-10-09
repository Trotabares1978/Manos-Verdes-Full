import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import vm from "node:vm";

const html = await readFile(new URL("../web/index.html", import.meta.url), "utf8");

test("preserva las claves de almacenamiento y pantallas principales", () => {
  for (const key of ["mvi_orders", "mvi_history", "mvi_debts", "mvi_clients", "mvi_route_templates", "mvi_active_route"]) assert.ok(html.includes(key), `falta ${key}`);
  for (const fn of ["saveOrder", "togglePaid", "toggleDelivered", "routePage", "optimizeActiveRoute", "saveCurrentRoute", "confirmSaveRoute", "removeStopFromRoute", "deleteOrder", "historyPage", "debtsPage", "exportBackup", "importBackup"]) assert.ok(html.includes("function " + fn + "("), `falta ${fn}`);
});
test("incluye acciones Maps y WhatsApp en las paradas", () => {
  assert.ok(html.includes("function wa("));
  assert.ok(html.includes("google.com/maps/search/?api=1&query="));
  assert.match(html, /o\.phone\s*\?\s*`<button[^\x60]*WhatsApp<\/button>`\s*:\s*""/s);
});
test("todos los scripts JavaScript inline tienen sintaxis válida", () => {
  const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map(m => m[1]).filter(s => s.trim());
  assert.ok(scripts.length > 0, "no se encontró JavaScript inline");
  for (const [i, source] of scripts.entries()) assert.doesNotThrow(() => new vm.Script(source, { filename: `inline-script-${i}.js` }), `script ${i} tiene errores de sintaxis`);
});
test("los manejadores onclick llaman funciones existentes", () => {
  const handlers = [...html.matchAll(/onclick="\s*(?:return\s+)?(?<![.\w$])([A-Za-z_$][\w$]*)\s*\(/g)].map(m => m[1]);
  const definitions = new Set([...html.matchAll(/(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(/g)].map(m => m[1]));
  const assigned = new Set([...html.matchAll(/(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(/g)].map(m => m[1]));
  const missing = [...new Set(handlers)].filter(name => !definitions.has(name) && !assigned.has(name));
  assert.deepEqual(missing, [], "manejadores sin función: " + missing.join(", "));
});
test("exporta e importa claves compatibles con copias antiguas", () => {
  for (const key of ["mvi_orders:orders", "mvi_history:history", "mvi_debts:debts", "mvi_clients:clients", "mvi_route_templates:routeTemplates", "mvi_active_route:activeRouteId"]) assert.ok(html.includes(key), `falta compatibilidad ${key}`);
});
test("identifica la aplicación como Manos Verdes", () => {
  assert.ok(html.includes("<title>Manos Verdes</title>"));
  assert.ok(html.includes("<h1>Manos Verdes</h1>"));
});
