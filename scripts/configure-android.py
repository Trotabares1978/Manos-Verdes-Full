#!/usr/bin/env python3
"""Configure native Android permissions, launcher icons, and the contacts picker."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from PIL import Image

ANDROID = "{http://schemas.android.com/apk/res/android}"
manifest = Path("android/app/src/main/AndroidManifest.xml")
if not manifest.exists():
    raise SystemExit("No se encontró AndroidManifest.xml")

tree = ET.parse(manifest)
root = tree.getroot()
permissions = {
    "android.permission.INTERNET",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.READ_CONTACTS",
}
present = {node.get(ANDROID + "name") for node in root.findall("uses-permission")}
for permission in sorted(permissions - present):
    node = ET.Element("uses-permission")
    node.set(ANDROID + "name", permission)
    root.insert(0, node)
tree.write(manifest, encoding="utf-8", xml_declaration=True)

main_files = list(Path("android/app/src/main/java").rglob("MainActivity.java"))
if len(main_files) != 1:
    raise SystemExit(f"Se esperaba un MainActivity.java y se encontraron {len(main_files)}")
main = main_files[0]
source = main.read_text(encoding="utf-8")
match = re.search(r"^\s*package\s+([\w.]+)\s*;", source, re.M)
if not match:
    raise SystemExit("No se pudo identificar el package de MainActivity")
package = match.group(1)
plugin_dir = Path("android/app/src/main/java") / Path(*package.split("."))
plugin_dir.mkdir(parents=True, exist_ok=True)
plugin_file = plugin_dir / "RuteroideContactsPlugin.java"
plugin_file.write_text(r'''package PACKAGE_NAME;

import android.app.Activity;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.provider.ContactsContract;
import androidx.activity.result.ActivityResult;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.annotation.ActivityCallback;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.getcapacitor.annotation.PluginMethod;

@CapacitorPlugin(name = "RuteroideContacts")
public class RuteroideContactsPlugin extends Plugin {
    @PluginMethod
    public void pickContact(PluginCall call) {
        Intent intent = new Intent(
            Intent.ACTION_PICK,
            ContactsContract.CommonDataKinds.Phone.CONTENT_URI
        );
        startActivityForResult(call, intent, "pickContactResult");
    }

    @ActivityCallback
    private void pickContactResult(PluginCall call, ActivityResult result) {
        if (call == null) return;
        if (result.getResultCode() != Activity.RESULT_OK ||
            result.getData() == null ||
            result.getData().getData() == null) {
            call.reject("No se seleccionó ningún contacto.");
            return;
        }
        Uri uri = result.getData().getData();
        String[] projection = {
            ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,
            ContactsContract.CommonDataKinds.Phone.NUMBER
        };
        try (Cursor cursor = getContext().getContentResolver().query(
            uri, projection, null, null, null
        )) {
            if (cursor != null && cursor.moveToFirst()) {
                String name = cursor.getString(0);
                String phone = cursor.getString(1);
                if (phone == null || phone.trim().isEmpty()) {
                    call.reject("El contacto seleccionado no tiene teléfono.");
                    return;
                }
                JSObject resultObject = new JSObject();
                resultObject.put("name", name == null ? "" : name);
                resultObject.put("phone", phone);
                call.resolve(resultObject);
            } else {
                call.reject("No se pudo leer el contacto.");
            }
        } catch (Exception error) {
            call.reject("Error leyendo el contacto.", error);
        }
    }
}
'''.replace("PACKAGE_NAME", package), encoding="utf-8")

if "RuteroideContactsPlugin.class" not in source:
    if "import android.os.Bundle;" not in source:
        source = source.replace("import com.getcapacitor.BridgeActivity;", "import android.os.Bundle;\nimport com.getcapacitor.BridgeActivity;")
    if re.search(r"public\s+void\s+onCreate\s*\(", source):
        if "super.onCreate(savedInstanceState);" not in source:
            raise SystemExit("onCreate existe pero no se encontró super.onCreate(savedInstanceState)")
        source = source.replace(
            "super.onCreate(savedInstanceState);",
            "registerPlugin(RuteroideContactsPlugin.class);\n        super.onCreate(savedInstanceState);",
            1
        )
    else:
        class_match = re.search(r"(public\s+class\s+MainActivity\s+extends\s+BridgeActivity\s*\{)", source)
        if not class_match:
            raise SystemExit("No se pudo insertar el registro del plugin en MainActivity")
        method = (
            class_match.group(1) + "\n"
            "    @Override\n"
            "    public void onCreate(Bundle savedInstanceState) {\n"
            "        registerPlugin(RuteroideContactsPlugin.class);\n"
            "        super.onCreate(savedInstanceState);\n"
            "    }\n"
        )
        source = source.replace(class_match.group(1), method, 1)
    main.write_text(source, encoding="utf-8")

icon_path = Path("www/icon.png")
if not icon_path.exists():
    raise SystemExit("Falta www/icon.png")
icon = Image.open(icon_path).convert("RGBA")
sizes = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
for density, size in sizes.items():
    folder = Path(f"android/app/src/main/res/mipmap-{density}")
    folder.mkdir(parents=True, exist_ok=True)
    resized = icon.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(folder / "ic_launcher.png")
    resized.save(folder / "ic_launcher_round.png")

# Force Android to use the generated raster icons rather than Capacitor's
# default adaptive-icon XML resources.
for adaptive in (
    Path("android/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml"),
    Path("android/app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml"),
):
    if adaptive.exists():
        adaptive.unlink()

print("Permisos, iconos y selector nativo de contactos configurados.")
