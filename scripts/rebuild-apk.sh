#!/usr/bin/env bash
set -euo pipefail
INPUT_APK="${1:-input/original.apk}"
OUT_DIR="${2:-out}"
PACKAGE_ID="${PACKAGE_ID:-com.manosverdes.full}"
APP_LABEL="Manos Verdes Full"

if [[ ! -f "$INPUT_APK" ]]; then
  echo "ERROR: falta $INPUT_APK"
  exit 2
fi
if [[ "$PACKAGE_ID" == "com.manosverdes.integral" ]]; then
  echo "ERROR: el identificador Full debe ser distinto del original."
  exit 3
fi
mkdir -p "$OUT_DIR"
WORK="$OUT_DIR/decoded"
rm -rf "$WORK"

echo "1/7 - Validando APK original"
unzip -t "$INPUT_APK" >/dev/null
echo "2/7 - Decodificando manifiesto y recursos"
apktool d -f "$INPUT_APK" -o "$WORK"

echo "3/7 - Cambiando nombre e identificador Android"
python3 - "$WORK/AndroidManifest.xml" "$PACKAGE_ID" "$APP_LABEL" <<'PY'
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
manifest_path, package_id, label = sys.argv[1:]
p = Path(manifest_path)
tree = ET.parse(p)
root = tree.getroot()
root.set("package", package_id)
android = "{http://schemas.android.com/apk/res/android}"
app = root.find("application")
if app is None:
    raise SystemExit("No se encontró application en el manifiesto")
app.set(android + "label", label)
tree.write(p, encoding="utf-8", xml_declaration=True)
print("Manifest package:", package_id)
PY

echo "4/7 - Actualizando configuración Capacitor"
CONFIG="$WORK/assets/capacitor.config.json"
if [[ -f "$CONFIG" ]]; then
  python3 - "$CONFIG" "$PACKAGE_ID" "$APP_LABEL" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1])
data=json.loads(p.read_text(encoding="utf-8"))
data["appId"]=sys.argv[2]
data["appName"]=sys.argv[3]
p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print("Capacitor appId:", data["appId"])
PY
fi

echo "5/7 - Añadiendo botón WhatsApp a las paradas"
ASSET="$WORK/assets/public/index.html"
if [[ ! -f "$ASSET" ]]; then
  echo "::error::No se encontró assets/public/index.html."
  exit 4
fi
python3 scripts/patch-route-whatsapp.py "$ASSET"

echo "6/7 - Reconstruyendo APK"
apktool b "$WORK" -o "$OUT_DIR/Manos-Verdes-Full-unsigned.apk"

echo "7/7 - Firmando y validando artefacto"
keytool -genkeypair -noprompt -keystore "$OUT_DIR/test-keystore.jks" -storepass changeit \
  -alias mvfull -keypass changeit -keyalg RSA -keysize 2048 -validity 10000 \
  -dname "CN=Manos Verdes Full, OU=Test, O=Manos Verdes, L=Ensenada, ST=Buenos Aires, C=AR"
jarsigner -keystore "$OUT_DIR/test-keystore.jks" -storepass changeit -keypass changeit \
  -signedjar "$OUT_DIR/Manos-Verdes-Full.apk" "$OUT_DIR/Manos-Verdes-Full-unsigned.apk" mvfull
jarsigner -verify "$OUT_DIR/Manos-Verdes-Full.apk"
unzip -p "$OUT_DIR/Manos-Verdes-Full.apk" assets/public/index.html | grep -q 'aria-label="WhatsApp"' || {
  echo "::error::No se detectó el botón WhatsApp en el APK resultante."; exit 5;
}
unzip -p "$OUT_DIR/Manos-Verdes-Full.apk" assets/capacitor.config.json | grep -q "$PACKAGE_ID" || {
  echo "::error::El appId de Capacitor no coincide."; exit 6;
}
echo "APK generada. Verificar instalación y backups en dispositivo antes de darla por lista."
