# -*- mode: python ; coding: utf-8 -*-
import os, struct

block_cipher = None
SRC = os.path.abspath(SPECPATH)
ICO = os.path.join(SRC, 'atra.ico')
PNG = os.path.join(SRC, 'atra.png')
DB  = os.path.join(SRC, 'koperasi.db')

a = Analysis(
    [os.path.join(SRC, 'koperasi_app.py')],
    pathex=[SRC],
    binaries=[],
    datas=[
        (DB,  '.'),
        (ICO, '.'),
        (PNG, '.'),
        (os.path.join(SRC, 'pages'), 'pages'),
    ],
    hiddenimports=[
        'tkinter', 'tkinter.ttk', 'tkinter.messagebox',
        'tkinter.filedialog', 'tkinter.simpledialog',
        'openpyxl', 'openpyxl.styles', 'openpyxl.utils',
        'openpyxl.writer.excel',
        'PIL', 'PIL.Image', 'PIL.ImageTk',
        'sqlite3', 'calendar', 'datetime', 'decimal',
        'ctypes', 'ctypes.windll', 'ctypes.wintypes',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'pytest'],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ATRA',
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon=ICO,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='ATRA',
)
