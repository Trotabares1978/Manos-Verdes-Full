import { mkdir, copyFile, readFile, writeFile } from "node:fs/promises";

await mkdir("www", { recursive: true });
const html = await readFile("web/index.html", "utf8");
if (!html.includes("function wa(")) throw new Error("Falta la función WhatsApp.");
if (!html.includes("optimizeActiveRoute")) throw new Error("Falta el optimizador de rutas.");
if (!html.includes("WhatsApp</button>")) throw new Error("Falta el botón WhatsApp.");
await writeFile("www/index.html", html);
try { await copyFile("web/icon.png", "www/icon.png"); } catch (error) { if (error.code !== "ENOENT") throw error; }
console.log("Interfaz validada y copiada a www/");
