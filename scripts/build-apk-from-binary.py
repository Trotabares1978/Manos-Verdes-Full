#!/usr/bin/env python3
"""Patch the supplied Manos Verdes Integral APK into a parallel-installable Full APK."""
import json, os, subprocess, sys, zipfile
from pathlib import Path

src = Path(sys.argv[1] if len(sys.argv) > 1 else "input/original.apk")
out = Path(sys.argv[2] if len(sys.argv) > 2 else "out/Manos-Verdes-Full-unsigned.apk")
old, new = b"com.manosverdes.integral", b"com.manosverdes.fulltest"
old_label, new_label = b"Manos Verdes Integral", b"Manos Verdes Full    "
if not src.is_file():
    raise SystemExit(f"No se encuentra la APK original: {src}")
if len(old) != len(new) or len(old_label) != len(new_label):
    raise SystemExit("Los identificadores/etiquetas deben conservar la longitud binaria.")
out.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(src) as zin:
    entries = {}
    for info in zin.infolist():
        leaf = info.filename.rsplit("/", 1)[-1].upper()
        if info.filename.startswith("META-INF/") and leaf in {"CERT.SF", "CERT.RSA", "CERT.DSA", "CERT.EC", "MANIFEST.MF"}:
            continue
        entries[info.filename] = (info, zin.read(info.filename))
html_info, raw_html = entries["assets/public/index.html"]
html = raw_html.decode("utf-8")
needle = """              <button type="button" class="primary small" onclick="openOrderInGoogleMaps('${o.id}')">🗺️ Google Maps</button>"""
if 'aria-label="WhatsApp"' not in html:
    if html.count(needle) != 1 or "function wa(phone)" not in html:
        raise SystemExit("No se encontró el botón Google Maps/función WhatsApp esperados en la APK.")
    html = html.replace(needle, needle + """
              ${o.phone ? `<button type="button" class="secondary small" title="WhatsApp" aria-label="WhatsApp" onclick="wa('${esc(o.phone)}')">💬</button>` : ""}""", 1)
if html.count('aria-label="WhatsApp"') != 1:
    raise SystemExit("La validación del botón WhatsApp falló.")
entries["assets/public/index.html"] = (html_info, html.encode())
for name in ("AndroidManifest.xml", "resources.arsc"):
    info, data = entries[name]
    if name == "AndroidManifest.xml":
        data = data.replace(old, new).replace(old.decode().encode("utf-16le"), new.decode().encode("utf-16le"))
        data = data.replace((new.decode()+".MainActivity").encode("utf-16le"), (old.decode()+".MainActivity").encode("utf-16le"))
    else:
        data = data.replace(old, new)
        if data.count(old_label) != 1:
            raise SystemExit("No se pudo identificar exactamente el nombre original en resources.arsc.")
        data = data.replace(old_label, new_label, 1)
    entries[name] = (info, data)
info, raw = entries["assets/capacitor.config.json"]
config = json.loads(raw.decode())
config.update(appId="com.manosverdes.fulltest", appName="Manos Verdes Full")
entries["assets/capacitor.config.json"] = (info, (json.dumps(config, indent=2)+"\n").encode())
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
    for name, (info, data) in entries.items():
        zout.writestr(info, data)
    zout.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\r\nCreated-By: Manos Verdes Full rebuild\r\n\r\n")
with zipfile.ZipFile(out) as z:
    if z.testzip() is not None:
        raise SystemExit("ZIP/APK dañado.")
    assert 'aria-label="WhatsApp"' in z.read("assets/public/index.html").decode()
    assert json.loads(z.read("assets/capacitor.config.json"))["appId"] == "com.manosverdes.fulltest"
print(f"APK sin firmar creada: {out} ({out.stat().st_size} bytes)")
print("IMPORTANTE: firmar con jarsigner/apksigner antes de instalar.")
