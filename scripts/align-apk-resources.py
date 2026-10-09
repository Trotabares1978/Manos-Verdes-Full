#!/usr/bin/env python3
"""Align resources.arsc to a 4-byte boundary without changing signed entry contents.

Run AFTER jarsigner: only ZIP extra-field padding is changed, not file data.
This is a narrow resources.arsc alignment helper, not a replacement for Android SDK zipalign.
"""
from pathlib import Path
import os
import struct
import sys
import tempfile
import zipfile

if len(sys.argv) != 2:
    raise SystemExit("Uso: align-apk-resources.py APK_FIRMADA")
path = Path(sys.argv[1])
if not path.is_file():
    raise SystemExit(f"No existe: {path}")
fd, tmpname = tempfile.mkstemp(prefix=path.stem + "-", suffix=".apk", dir=str(path.parent))
os.close(fd)
try:
    with zipfile.ZipFile(path, "r") as src, zipfile.ZipFile(tmpname, "w") as dst:
        for old in src.infolist():
            data = src.read(old.filename)
            info = zipfile.ZipInfo(old.filename, old.date_time)
            info.compress_type = old.compress_type
            info.comment = old.comment
            info.extra = old.extra
            info.internal_attr = old.internal_attr
            info.external_attr = old.external_attr
            info.create_system = old.create_system
            if old.filename == "resources.arsc":
                if info.compress_type != zipfile.ZIP_STORED:
                    raise SystemExit("resources.arsc debe estar almacenado sin compresión.")
                base = dst.fp.tell() + 30 + len(info.filename.encode("utf-8")) + len(info.extra)
                padding = (-base) % 4
                if padding:
                    total = padding if padding >= 4 else padding + 4
                    info.extra += struct.pack("<HH", 0xD935, total - 4) + b"\0" * (total - 4)
                    while (dst.fp.tell() + 30 + len(info.filename.encode("utf-8")) + len(info.extra)) % 4:
                        info.extra += b"\0"
            dst.writestr(info, data)
    with zipfile.ZipFile(tmpname, "r") as check:
        if check.testzip() is not None:
            raise SystemExit("El APK quedó corrupto al alinear.")
        info = check.getinfo("resources.arsc")
        offset = info.header_offset + 30 + len(info.filename.encode("utf-8")) + len(info.extra)
        if info.compress_type != zipfile.ZIP_STORED or offset % 4:
            raise SystemExit(f"resources.arsc no quedó alineado: offset={offset}, método={info.compress_type}")
    os.replace(tmpname, path)
    print(f"resources.arsc alineado a 4 bytes: {path}")
finally:
    if os.path.exists(tmpname):
        os.unlink(tmpname)
