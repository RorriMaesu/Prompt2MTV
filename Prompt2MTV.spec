# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_all


APP_NAME = 'Prompt2MTV'
APP_VERSION = '1.2.0'
APP_COMPANY = 'Prompt2MTV'
APP_DESCRIPTION = 'Prompt2MTV Local AI Music Video Studio'

project_root = Path(globals().get('SPECPATH', Path.cwd())).resolve()
imageio_datas, imageio_binaries, imageio_hiddenimports = collect_all('imageio_ffmpeg')
dnd_datas, dnd_binaries, dnd_hiddenimports = collect_all('tkinterdnd2')
workflow_datas = [
    (str(project_root / 'video_ltx2_3_t2v.json'), '.'),
    (str(project_root / 'ACE_Step_AI_Music_Generator_Workflow.json'), '.'),
    (str(project_root / 'model_manifest.json'), '.'),
]
app_icon = str(project_root / 'Prompt2MTV.ico')
version_file = str(project_root / 'Prompt2MTV_version_info.txt')


a = Analysis(
    [str(project_root / 'ltx_queue_manager.py')],
    pathex=[str(project_root)],
    binaries=imageio_binaries + dnd_binaries,
    datas=workflow_datas + imageio_datas + dnd_datas,
    hiddenimports=imageio_hiddenimports + dnd_hiddenimports,
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
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    icon=app_icon,
    version=version_file,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)
