import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const html = await readFile(new URL("../web/index.html", import.meta.url), "utf8");

test("preserva las claves de almacenamiento heredadas presentes en la interfaz", () => {
  for (const key of ["mvi_orders", "mvi_history", "mvi_debts", "mvi_clients", "mvi_route_templates", "mvi_active_route"]) assert.ok(html.includes(key), `falta ${key}`);
});
test("incluye funciones principales de pedidos y rutas", () => {
  for (const fn of ["saveOrder", "togglePaid", "toggleDelivered", "routePage", "optimizeActiveRoute", "saveCurrentRoute", "confirmSaveRoute"]) assert.ok(html.includes(fn), `falta ${fn}`);
});
test("incluye WhatsApp condicional en la lista de paradas", () => {
  assert.ok(html.includes("function wa("));
  assert.match(html, /o\.phone\s*\?\s*`<button[^`]*WhatsApp<\/button>`\s*:\s*""/s);
});
test("identifica la app como Manos Verdes Full", () => {
  assert.ok(html.includes("<title>Manos Verdes Full</title>"));
});
