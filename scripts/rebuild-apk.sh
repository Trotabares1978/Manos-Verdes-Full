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

echo "1/6 - Verificando APK de entrada"
unzip -t "$INPUT_APK" >/dev/null
echo "2/6 - Decodificando APK"
apktool d -f "$INPUT_APK" -o "$WORK"

echo "3/6 - Agregando botón WhatsApp en las paradas (si se reconoce la plantilla)"
ASSET="$WORK/assets/public/index.html"
if [[ -f "$ASSET" ]]; then
  python3 scripts/patch-route-whatsapp.py "$ASSET"
else
  echo "::error::No se encontró assets/public/index.html. Se detiene para no publicar una app sin el cambio solicitado."
  exit 4
fi

echo "4/6 - Cambiando identificador y nombre de la app"
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
    raise SystemExit("No se encontró el nodo application en el manifiesto")
app.set(android + "label", label)
tree.write(p, encoding="utf-8", xml_declaration=True)
print("package =", package_id)
print("application label =", label)
PY

echo "5/6 - Recompilando"
apktool b "$WORK" -o "$OUT_DIR/Manos-Verdes-Full-unsigned.apk"

echo "6/6 - Firmando y verificando APK"
keytool -genkeypair -noprompt -keystore "$OUT_DIR/test-keystore.jks" -storepass changeit \
  -alias mvfull -keypass changeit -keyalg RSA -keysize 2048 -validity 10000 \
  -dname "CN=Manos Verdes Full, OU=Test, O=Manos Verdes, L=Ensenada, ST=Buenos Aires, C=AR"
jarsigner -keystore "$OUT_DIR/test-keystore.jks" -storepass changeit -keypass changeit \
  -signedjar "$OUT_DIR/Manos-Verdes-Full.apk" "$OUT_DIR/Manos-Verdes-Full-unsigned.apk" mvfull
jarsigner -verify "$OUT_DIR/Manos-Verdes-Full.apk"
unzip -p "$OUT_DIR/Manos-Verdes-Full.apk" assets/public/index.html | grep -q 'aria-label="WhatsApp"' || {
  echo "::error::No se detectó el botón WhatsApp en el APK resultante."
  exit 5
}
echo "APK reconstruida y firmada: $OUT_DIR/Manos-Verdes-Full.apk"
echo "::warning::Debe probarse en un teléfono antes de considerarla lista; la firma es nueva y temporal."
