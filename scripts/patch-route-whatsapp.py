#!/usr/bin/env python3
"""Add one compact WhatsApp button after the route stop Google Maps button."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("Uso: patch-route-whatsapp.py RUTA_A_INDEX_HTML")

path = Path(sys.argv[1])
s = path.read_text(encoding="utf-8")
if 'aria-label="WhatsApp"' in s:
    print("WhatsApp route button already exists; unchanged.")
    raise SystemExit(0)

anchor = 'onclick="openOrderInGoogleMaps(\'${o.id}\')">🗺️ Google Maps</button>'
pos = s.find(anchor)
if pos < 0:
    raise SystemExit("No se encontró el botón Google Maps de las paradas; no se modificó el archivo.")
end = pos + len(anchor)
addition = """
              ${o.phone ? `<button type="button" class="secondary small" title="WhatsApp" aria-label="WhatsApp" onclick="wa(\'${esc(o.phone)}\')">💬</button>` : ""}
"""
s = s[:end] + addition + s[end:]
if s.count('aria-label="WhatsApp"') != 1 or "function wa(phone)" not in s:
    raise SystemExit("Validación fallida: el botón o la función WhatsApp no quedó correctamente definida.")
path.write_text(s, encoding="utf-8")
print("Botón WhatsApp agregado junto a Google Maps en las paradas de ruta.")
