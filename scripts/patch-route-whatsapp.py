#!/usr/bin/env python3
from pathlib import Path
import sys
p = Path(sys.argv[1])
s = p.read_text(encoding='utf-8')
if 'aria-label="WhatsApp"' in s:
    print('WhatsApp route button already exists; unchanged.')
    raise SystemExit(0)
anchor = 'onclick="openOrderInGoogleMaps('
pos = s.find(anchor)
if pos < 0:
    raise SystemExit('Expected Google Maps route button not found; no changes made.')
end = s.find('</button>', pos)
if end < 0:
    raise SystemExit('Could not locate end of Google Maps button; no changes made.')
end += len('</button>')
addition = '\n          ${o.phone ? `<button type="button" class="secondary small" title="WhatsApp" aria-label="WhatsApp" onclick="wa(\'${String(o.phone).replace(/\\D/g,"")}\')">💬</button>` : ""}'
s = s[:end] + addition + s[end:]
p.write_text(s, encoding='utf-8')
print('Added WhatsApp icon button after route Google Maps button.')