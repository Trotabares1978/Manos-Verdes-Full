#!/usr/bin/env bash
set -euo pipefail

INPUT_APK="${1:-input/original.apk}"
OUT_DIR="${2:-out}"
PACKAGE_ID="${PACKAGE_ID:-com.manosverdes.full}"
APP_LABEL="Manos Verdes Full"

if [[ ! -f "$INPUT_APK" ]]; then
  echo "ERROR: falta $INPUT_APK"
  echo "Subí la APK original de Manos Verdes Integral a input/original.apk para ejecutar la reconstrucción."
  exit 2
fi

mkdir -p "$OUT_DIR"
WORK="$OUT_DIR/decoded"
rm -rf "$WORK"

echo "1/5 - Verificando APK de entrada"
unzip -t "$INPUT_APK" >/dev/null
echo "APK ZIP íntegro."

echo "2/5 - Decodificando manifiesto y recursos"
apktool d -f "$INPUT_APK" -o "$WORK"

echo "3/5 - Cambiando identidad de paquete"
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

echo "4/5 - Recompilando"
apktool b "$WORK" -o "$OUT_DIR/Manos-Verdes-Full-unsigned.apk"

echo "5/5 - Firmando APK con clave temporal de CI"
keytool -genkeypair -noprompt -keystore "$OUT_DIR/test-keystore.jks" -storepass changeit \
  -alias mvfull -keypass changeit -keyalg RSA -keysize 2048 -validity 10000 \
  -dname "CN=Manos Verdes Full, OU=Test, O=Manos Verdes, L=Ensenada, ST=Buenos Aires, C=AR"
jarsigner -keystore "$OUT_DIR/test-keystore.jks" -storepass changeit -keypass changeit \
  -signedjar "$OUT_DIR/Manos-Verdes-Full.apk" "$OUT_DIR/Manos-Verdes-Full-unsigned.apk" mvfull
jarsigner -verify -verbose "$OUT_DIR/Manos-Verdes-Full.apk" >/dev/null

echo "APK firmada: $OUT_DIR/Manos-Verdes-Full.apk"
echo "AVISO: firma de prueba nueva; la importación de backups y el arranque deben validarse en un dispositivo."
