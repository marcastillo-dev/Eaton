from pathlib import Path
from importlib.util import find_spec
from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

root = Path(SPECPATH)
datas = [(str(root / 'app.py'), '.')]
for folder in ('assets', 'data'):
    datas.append((str(root / folder), folder))
# Streamlit executes app.py dynamically, so its imports need explicit collection.
hiddenimports = collect_submodules('src') + [
    'openpyxl', 'xlsxwriter', 'reportlab', 'pandas',
]
# Cython extensions import each other dynamically (including _cyutility).
pandas_root = Path(find_spec('pandas').origin).parent
hiddenimports += [
    'pandas.' + '.'.join(path.relative_to(pandas_root).parts[:-1] + (path.name.split('.')[0],))
    for path in pandas_root.rglob('*.pyd')
]
binaries = []
for package in ('streamlit', 'altair', 'pydeck'):
    package_data, package_binaries, package_imports = collect_all(package)
    datas += package_data
    binaries += package_binaries
    hiddenimports += package_imports
datas += copy_metadata('streamlit', recursive=True)

a = Analysis(['launcher.py'], pathex=[str(root)], binaries=binaries,
             datas=datas, hiddenimports=hiddenimports, hookspath=[],
             runtime_hooks=[], excludes=[], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='EatonEDS',
          debug=False, bootloader_ignore_signals=False, strip=False,
          upx=False, console=False, icon=str(root / 'assets' / 'eaton_logo.ico'))
