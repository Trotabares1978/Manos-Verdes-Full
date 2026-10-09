import { mkdir, copyFile, readFile, writeFile } from "node:fs/promises";
import vm from "node:vm";

await mkdir("www", { recursive: true });
const html = await readFile("web/index.html", "utf8");
for (const [needle, message] of [
  ["function wa(", "Falta la función WhatsApp."],
  ["optimizeActiveRoute", "Falta el optimizador de rutas."],
  ["WhatsApp</button>", "Falta el botón WhatsApp."],
  ["function historyPage(", "Falta la pantalla Historial."],
  ["function debtsPage(", "Falta la pantalla Deudas."],
  ["function exportBackup(", "Falta la exportación de copias de seguridad."],
  ["function importBackup(", "Falta la importación de copias de seguridad."]
]) if (!html.includes(needle)) throw new Error(message);

const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map(m => m[1]).filter(s => s.trim());
if (!scripts.length) throw new Error("No se encontró JavaScript ejecutable.");
scripts.forEach((source, i) => new vm.Script(source, { filename: `inline-script-${i}.js` }));

const handlers = [...html.matchAll(/onclick="\s*(?:return\s+)?(?<![.\w$])([A-Za-z_$][\w$]*)\s*\(/g)].map(m => m[1]);
const definitions = new Set([...html.matchAll(/(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(/g)].map(m => m[1]));
const assigned = new Set([...html.matchAll(/(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(/g)].map(m => m[1]));
const missing = [...new Set(handlers)].filter(name => !definitions.has(name) && !assigned.has(name));
if (missing.length) throw new Error("Manejadores sin función: " + missing.join(", "));

await writeFile("www/index.html", html);
await copyFile("web/icon.svg", "www/icon.svg");
console.log("Interfaz validada (sintaxis y manejadores) y copiada a www/");
