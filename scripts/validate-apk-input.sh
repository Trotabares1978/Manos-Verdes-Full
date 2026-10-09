#!/usr/bin/env bash
set -euo pipefail
APK="${1:-input/original.apk}"
if [[ ! -f "$APK" ]]; then
  echo "::error::APK original no encontrada: $APK"
  exit 2
fi
unzip -t "$APK" >/dev/null
echo "APK ZIP válida"
echo "Tamaño: $(stat -c '%s bytes' "$APK")"
echo "Entradas Android relevantes:"
unzip -Z1 "$APK" | grep -E '^(AndroidManifest.xml|assets/capacitor.config.json|assets/public/index.html|META-INF/)' | head -30 || true
unzip -p "$APK" assets/capacitor.config.json 2>/dev/null || true
