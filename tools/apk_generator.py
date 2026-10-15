"""
ULTRON Satellite APK Generator
Constructs standard Android Binary XML (AXML), Dalvik DEX bytecode, web assets, and signs with RSA-2048.
"""

import os
import io
import sys
import struct
import shutil
import zipfile
import subprocess
from pathlib import Path

DATA_DIR = Path.home() / "Documents" / "ULTRON_Data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR = Path.home() / "Downloads"

JDK_BIN = Path(r"C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot\bin")
KEYTOOL = JDK_BIN / "keytool.exe"
JARSIGNER = JDK_BIN / "jarsigner.exe"

APK_OUTPUT_DATA = DATA_DIR / "ULTRON_Satellite.apk"
APK_OUTPUT_DOWNLOADS = DOWNLOADS_DIR / "ULTRON_Satellite.apk"


def build_binary_axml() -> bytes:
    strings = [
        "versionCode", "versionName", "minSdkVersion", "targetSdkVersion",
        "package", "manifest", "uses-sdk", "uses-permission", "application",
        "activity", "intent-filter", "action", "category",
        "name", "label", "icon", "theme", "hardwareAccelerated",
        "android.permission.INTERNET",
        "android.permission.RECORD_AUDIO",
        "android.permission.CAMERA",
        "android.permission.MODIFY_AUDIO_SETTINGS",
        "android.permission.ACCESS_NETWORK_STATE",
        "android.permission.ACCESS_WIFI_STATE",
        "android.permission.VIBRATE",
        "com.ultron.satellite",
        "com.ultron.satellite.MainActivity",
        "ULTRON Satellite",
        "android.intent.action.MAIN",
        "android.intent.category.LAUNCHER",
        "android",
        "http://schemas.android.com/apk/res/android"
    ]
    
    res_ids = [
        0x0101021b, 0x0101021c, 0x0101020c, 0x01010270,
        0, 0, 0, 0, 0,
        0, 0, 0, 0,
        0x01010003, 0x01010001, 0x01010002, 0x01010000, 0x010102d3
    ] + [0] * (len(strings) - 18)

    str_offsets = []
    str_bytes = bytearray()
    for s in strings:
        str_offsets.append(len(str_bytes))
        u16 = s.encode('utf-16le')
        str_bytes.extend(struct.pack('<H', len(s)))
        str_bytes.extend(u16)
        str_bytes.extend(b'\x00\x00')
        
    while len(str_bytes) % 4 != 0:
        str_bytes.extend(b'\x00')
        
    string_pool_header_size = 28
    string_offsets_len = len(strings) * 4
    string_data_start = string_pool_header_size + string_offsets_len
    string_pool_chunk_size = string_data_start + len(str_bytes)
    
    # 1. String Pool Chunk
    str_pool = bytearray()
    str_pool.extend(struct.pack('<HHIIIIII',
        0x0001, 0x001c,
        string_pool_chunk_size,
        len(strings), 0,
        0x00000000,
        string_data_start,
        0
    ))
    for off in str_offsets:
        str_pool.extend(struct.pack('<I', off))
    str_pool.extend(str_bytes)
    
    # 2. Resource IDs Chunk
    res_chunk = bytearray()
    res_chunk_size = 8 + len(res_ids) * 4
    res_chunk.extend(struct.pack('<HHI', 0x0180, 0x0008, res_chunk_size))
    for rid in res_ids:
        res_chunk.extend(struct.pack('<I', rid))
        
    # 3. XML Body Nodes
    xml_body = bytearray()
    
    def add_ns(uri_idx, prefix_idx, is_start=True):
        chunk_type = 0x0100 if is_start else 0x0101
        xml_body.extend(struct.pack('<HHIIIII',
            chunk_type, 0x0010, 0x0018,
            1, 0xFFFFFFFF,
            prefix_idx, uri_idx
        ))

    def make_elem_start(name_idx, line_no, attrs_data, attr_count):
        # Header (16) + Ext (20) + Attrs (len(attrs_data))
        chunk_size = 36 + len(attrs_data)
        return struct.pack('<HHIIIIIHHHHHH',
            0x0102, 0x0010, chunk_size,
            line_no, 0xFFFFFFFF,
            0xFFFFFFFF, name_idx,
            0x0014, 0x0014, attr_count,
            0, 0, 0
        ) + attrs_data

    def make_elem_end(name_idx, line_no):
        return struct.pack('<HHIIIII',
            0x0103, 0x0010, 0x0018,
            line_no, 0xFFFFFFFF,
            0xFFFFFFFF, name_idx
        )

    def make_attr(ns_idx, name_idx, raw_str_idx, type_code, data_val):
        return struct.pack('<IIIHBB I',
            ns_idx, name_idx, raw_str_idx,
            0x0008, 0, type_code,
            data_val
        )
        
    ns_android = 31 # "http://schemas.android.com/apk/res/android"
    prefix_android = 30 # "android"
    
    # Start NS
    add_ns(ns_android, prefix_android, True)
    
    # <manifest package="com.ultron.satellite" versionCode="1" versionName="1.0">
    manifest_attrs = bytearray()
    manifest_attrs.extend(make_attr(0xFFFFFFFF, 4, 25, 0x03, 25))
    manifest_attrs.extend(make_attr(ns_android, 0, 0xFFFFFFFF, 0x10, 1))
    manifest_attrs.extend(make_attr(ns_android, 1, 0xFFFFFFFF, 0x03, 1))
    xml_body.extend(make_elem_start(5, 1, manifest_attrs, 3))
    
    # <uses-permission android:name="..."/>
    permissions = [18, 19, 20, 21, 22, 23, 24]
    for idx, p_idx in enumerate(permissions, start=2):
        p_attr = make_attr(ns_android, 13, p_idx, 0x03, p_idx)
        xml_body.extend(make_elem_start(7, idx, p_attr, 1))
        xml_body.extend(make_elem_end(7, idx))

    # <application android:label="ULTRON Satellite" android:hardwareAccelerated="true">
    app_attrs = bytearray()
    app_attrs.extend(make_attr(ns_android, 14, 27, 0x03, 27))
    app_attrs.extend(make_attr(ns_android, 17, 0xFFFFFFFF, 0x12, 1))
    xml_body.extend(make_elem_start(8, 10, app_attrs, 2))
    
    # <activity android:name="com.ultron.satellite.MainActivity" android:label="ULTRON Satellite">
    act_attrs = bytearray()
    act_attrs.extend(make_attr(ns_android, 13, 26, 0x03, 26))
    act_attrs.extend(make_attr(ns_android, 14, 27, 0x03, 27))
    xml_body.extend(make_elem_start(9, 11, act_attrs, 2))
    
    # <intent-filter>
    xml_body.extend(make_elem_start(10, 12, b'', 0))
    # <action android:name="android.intent.action.MAIN"/>
    xml_body.extend(make_elem_start(11, 13, make_attr(ns_android, 13, 28, 0x03, 28), 1))
    xml_body.extend(make_elem_end(11, 13))
    # <category android:name="android.intent.category.LAUNCHER"/>
    xml_body.extend(make_elem_start(12, 14, make_attr(ns_android, 13, 29, 0x03, 29), 1))
    xml_body.extend(make_elem_end(12, 14))
    # Close <intent-filter>, <activity>, <application>, <manifest>
    xml_body.extend(make_elem_end(10, 15))
    xml_body.extend(make_elem_end(9, 16))
    xml_body.extend(make_elem_end(8, 17))
    xml_body.extend(make_elem_end(5, 18))
    
    # End NS
    add_ns(ns_android, prefix_android, False)
    
    # Total File Header
    total_size = 8 + len(str_pool) + len(res_chunk) + len(xml_body)
    header = struct.pack('<HHI', 0x0003, 0x0008, total_size)
    
    return bytes(header + str_pool + res_chunk + xml_body)


def build_dex_bytecode() -> bytes:
    import hashlib
    import zlib
    
    dex_strings = [
        "Lcom/ultron/satellite/MainActivity;",
        "Landroid/app/Activity;",
        "onCreate",
        "(Landroid/os/Bundle;)V",
        "MainActivity.java",
        "V",
        "VL",
        "android/app/Activity",
        "com/ultron/satellite/MainActivity"
    ]
    
    str_data_buf = bytearray()
    str_offsets = []
    for s in dex_strings:
        str_offsets.append(len(str_data_buf))
        str_data_buf.append(len(s))
        str_data_buf.extend(s.encode('utf-8'))
        str_data_buf.append(0)
        
    while len(str_data_buf) % 4 != 0:
        str_data_buf.append(0)
        
    header_size = 0x70
    string_ids_off = header_size
    string_ids_size = len(dex_strings)
    
    type_ids_off = string_ids_off + string_ids_size * 4
    type_ids_size = 2
    
    proto_ids_off = type_ids_off + type_ids_size * 4
    proto_ids_size = 1
    
    field_ids_off = proto_ids_off + proto_ids_size * 12
    field_ids_size = 0
    
    method_ids_off = field_ids_off
    method_ids_size = 1
    
    class_defs_off = method_ids_off + method_ids_size * 8
    class_defs_size = 1
    
    data_off = class_defs_off + class_defs_size * 32
    
    string_ids_data = bytearray()
    for off in str_offsets:
        string_ids_data.extend(struct.pack('<I', data_off + off))
        
    type_ids_data = bytearray()
    type_ids_data.extend(struct.pack('<I', 0))
    type_ids_data.extend(struct.pack('<I', 1))
    
    proto_ids_data = bytearray()
    proto_ids_data.extend(struct.pack('<III', 2, 5, 0))
    
    method_ids_data = bytearray()
    method_ids_data.extend(struct.pack('<HHI', 0, 0, 2))
    
    class_defs_data = bytearray()
    class_defs_data.extend(struct.pack('<IIIIIIII',
        0, 0x0001, 1, 0, 4, 0, 0, 0
    ))
    
    data_payload = bytearray(str_data_buf)
    total_file_size = data_off + len(data_payload)
    
    body = bytearray()
    body.extend(string_ids_data)
    body.extend(type_ids_data)
    body.extend(proto_ids_data)
    body.extend(method_ids_data)
    body.extend(class_defs_data)
    body.extend(data_payload)
    
    magic = b'dex\n035\x00'
    endian_tag = 0x12345678
    
    header = bytearray()
    header.extend(magic)
    header.extend(b'\x00' * 4)
    header.extend(b'\x00' * 20)
    header.extend(struct.pack('<IIIIIIIIIIIIII',
        total_file_size, header_size, endian_tag,
        0, 0, 0,
        string_ids_size, string_ids_off,
        type_ids_size, type_ids_off,
        proto_ids_size, proto_ids_off,
        field_ids_size, field_ids_off
    ))
    header.extend(struct.pack('<II', method_ids_size, method_ids_off))
    header.extend(struct.pack('<II', class_defs_size, class_defs_off))
    header.extend(struct.pack('<II', len(data_payload), data_off))
    
    full_dex = header + body
    
    sha1 = hashlib.sha1(full_dex[32:]).digest()
    full_dex[12:32] = sha1
    
    adler = zlib.adler32(full_dex[12:]) & 0xFFFFFFFF
    full_dex[8:12] = struct.pack('<I', adler)
    
    return bytes(full_dex)


def generate_ultron_satellite_apk():
    print("[1/5] Compiling ULTRON Binary Android Manifest (AXML)...")
    axml_bytes = build_binary_axml()
    
    print("[2/5] Compiling Dalvik Executable Bytecode (classes.dex)...")
    dex_bytes = build_dex_bytecode()
    
    print("[3/5] Bundling Cyberpunk Mobile Web HUD & Assets...")
    html_src = Path.home() / ".gemini" / "antigravity" / "brain" / "fbd594d0-e2ba-4f8a-98c6-03687bf1f910" / "ultron_mobile_apk_ui.html"
    with open(html_src, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    build_dir = DATA_DIR / "apk_bundle"
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
        except Exception:
            pass
    build_dir.mkdir(parents=True, exist_ok=True)
    
    unsigned_apk = build_dir / "ULTRON_Satellite_Unsigned.apk"
    with zipfile.ZipFile(unsigned_apk, 'w', zipfile.ZIP_DEFLATED) as apk:
        apk.writestr("AndroidManifest.xml", axml_bytes)
        apk.writestr("classes.dex", dex_bytes)
        apk.writestr("assets/index.html", html_content.encode("utf-8"))
        apk.writestr("assets/app.html", html_content.encode("utf-8"))
        apk.writestr("resources.arsc", b"\x02\x00\x0C\x00" + b"\x00" * 20)
        
    print("[4/5] Generating RSA-2048 Keystore & Signing APK...")
    keystore_path = DATA_DIR / "ultron_debug.keystore"
    if not keystore_path.exists():
        cmd = [
            str(KEYTOOL if KEYTOOL.exists() else "keytool"),
            "-genkeypair",
            "-v",
            "-keystore", str(keystore_path),
            "-alias", "ultron_key",
            "-keyalg", "RSA",
            "-keysize", "2048",
            "-validity", "10000",
            "-storepass", "ultron123",
            "-keypass", "ultron123",
            "-dname", "CN=ULTRON Satellite, OU=AI, O=Friday, L=London, ST=UK, C=GB"
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
    signed_apk = build_dir / "ULTRON_Satellite.apk"
    sign_cmd = [
        str(JARSIGNER if JARSIGNER.exists() else "jarsigner"),
        "-keystore", str(keystore_path),
        "-storepass", "ultron123",
        "-keypass", "ultron123",
        "-signedjar", str(signed_apk),
        str(unsigned_apk),
        "ultron_key"
    ]
    subprocess.run(sign_cmd, check=True, capture_output=True)
    
    print("[5/5] Deploying Final APK to Output Locations...")
    shutil.copy2(signed_apk, APK_OUTPUT_DATA)
    shutil.copy2(signed_apk, APK_OUTPUT_DOWNLOADS)
    
    size_kb = APK_OUTPUT_DOWNLOADS.stat().st_size / 1024
    print(f"[SUCCESS] ULTRON Satellite APK built and signed ({size_kb:.1f} KB)")
    print(f"[LOCATION 1] {APK_OUTPUT_DOWNLOADS}")
    print(f"[LOCATION 2] {APK_OUTPUT_DATA}")
    return str(APK_OUTPUT_DOWNLOADS)

if __name__ == "__main__":
    generate_ultron_satellite_apk()
