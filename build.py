"""Build and verify the portable Windows executable: python build.py."""
from pathlib import Path
import os
import subprocess
import sys


def main():
    if sys.platform != 'win32':
        raise SystemExit('Compila este ejecutable desde Windows de 64 bits.')
    root = Path(__file__).resolve().parent
    os.chdir(root)
    python = root / '.venv-build' / 'Scripts' / 'python.exe'
    if not python.is_file():
        subprocess.run([sys.executable, '-m', 'venv', '.venv-build'], check=True)
    subprocess.run([str(python), '-m', 'pip', 'install', '-r', 'requirements-build.txt'], check=True)
    workpath = Path(os.environ.get('TEMP', root / 'tmp')) / 'EatonEDS-pyinstaller'
    subprocess.run([
        str(python), '-m', 'PyInstaller', '--noconfirm', '--clean',
        '--workpath', str(workpath), 'EatonEDS.spec'
    ], check=True)
    exe = root / 'dist' / 'EatonEDS.exe'
    report = root / 'build' / 'verification.json'
    result = subprocess.run([str(exe), '--self-test', str(report)], timeout=180)
    if result.returncode:
        raise SystemExit('Fallo la verificacion. Consulta %LOCALAPPDATA%\\EatonEDS\\error.log')
    print(f'Ejecutable verificado: {exe}')
    print(f'Resultados: {report}')


if __name__ == '__main__':
    main()
