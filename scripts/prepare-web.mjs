import { mkdir, copyFile, readFile, writeFile } from "node:fs/promises";
import { dirname } from "node:path";

await mkdir("www", { recursive: true });
let html = await readFile("web/index.html", "utf8");
// Add a per-stop WhatsApp action beside each order in the active route.
const old = '<b>${money(o.total)}</b>';
const replacement = '<div style="display:flex;align-items:center;gap:8px"><b>${money(o.total)}</b>${o.phone ? `<button class="secondary small" aria-label="WhatsApp" onclick="wa(\'${esc(o.phone)}\')">💬 WhatsApp</button>` : ""}</div>';
if (html.includes(old) && !html.includes('aria-label="WhatsApp"')) html = html.replace(old, replacement);
await writeFile("www/index.html", html);
try { await copyFile("web/icon.png", "www/icon.png"); } catch {}
console.log("Web app preparada; acción WhatsApp integrada en la fila de pedidos cuando hay teléfono.");
