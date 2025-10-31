# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all


cv2_datas, cv2_binaries, cv2_hiddenimports = collect_all('cv2')


a = Analysis(
    ['pc_app\\omnicall_app.py'],
    pathex=['pc_app'],
    binaries=cv2_binaries,
    datas=[
        # Template image for detection
        ('Accept.png', '.'),
        
        # App icons
        ('docs\\icon-192.png', 'docs'),
        ('docs\\icon-512.png', 'docs'),
        ('docs\\support_page.jpeg', 'docs'),
        
        # Tab icons
        ('pc_app\\Track.png', 'pc_app'),
        ('pc_app\\stats.png', 'pc_app'),
        ('pc_app\\feedback.png', 'pc_app'),
        ('pc_app\\support.png', 'pc_app'),
        
        # Support page images
        ('pc_app\\support_page.jpeg', 'pc_app'),
        ('pc_app\\paypal.png', 'pc_app'),
        ('pc_app\\binance.png', 'pc_app'),
    ] + cv2_datas,
    hiddenimports=cv2_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OmniCall',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['pc_app\\omnicall.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OmniCall',
)
