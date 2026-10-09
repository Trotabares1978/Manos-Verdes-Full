import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const html = await readFile(new URL("../web/index.html", import.meta.url), "utf8");

test("preserva claves de almacenamiento heredadas", () => {
  for (const key of ["mvi_orders", "mvi_history", "mvi_debts", "mvi_clients", "mvi_route_templates", "mvi_active_route"]) assert.ok(html.includes(key), `falta ${key}`);
});
test("contiene módulos de finalización, deudas y rutas", () => {
  for (const fn of ["finish", "routePage", "optimizeActiveRoute", "saveCurrentRoute", "confirmSaveRoute"]) assert.ok(html.includes(fn), `falta ${fn}`);
});
test("tiene mecanismo WhatsApp y no obliga a contactar pedidos sin teléfono", () => {
  assert.ok(html.includes("function wa("));
  assert.ok(html.includes("o.phone"));
});
