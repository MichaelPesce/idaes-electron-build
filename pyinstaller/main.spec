# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path 
import os

sys.setrecursionlimit(5000)

block_cipher = None

## get idaes-flowsheet-processor-ui path
import idaes_flowsheet_processor_ui
pkg_path = Path(idaes_flowsheet_processor_ui.__file__).parent

a = Analysis(
    # ['../electron/idaes-flowsheet-processor-ui/backend/src/idaes_flowsheet_processor_ui/main.py'],
    [os.path.join(pkg_path,"main.py")],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['bson', 'pymongo','psutil','lxml'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=["api-ms-win-core*.dll"],
    name='main',
)