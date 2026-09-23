"""Portable Windows entry point; Streamlit runs in a managed child process."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import traceback
import urllib.request
import webbrowser

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
LOG_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "EatonEDS"


def serve(port):
    from streamlit.web import bootstrap

    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT))
    options = {
        "server.address": "127.0.0.1",
        "server.port": port,
        "server.headless": True,
        "server.fileWatcherType": "none",
        "server.runOnSave": False,
        "browser.gatherUsageStats": False,
        "global.developmentMode": False,
    }
    bootstrap.load_config_options(options)
    bootstrap.run(str(ROOT / "app.py"), False, [], options)


def self_test(output):
    """Exercise the packaged application without requiring a browser."""
    import json
    from io import BytesIO
    from streamlit.testing.v1 import AppTest
    from src.eaton.config.settings import ASSETS_DIR, CATALOGO
    from src.eaton.services.catalogo_service import CatalogoService
    from src.eaton.services.export_service import generar_excel
    import openpyxl

    sys.path.insert(0, str(ROOT))
    catalog = CatalogoService(CATALOGO)
    assert catalog.hojas
    for name in (
        "eaton_logo.ico",
        "eaton_logo.png",
        "BZM.png",
        "PDG.png",
        "F.png",
        "J.png",
        "K.png",
        "L.png"
    ):
        assert (ASSETS_DIR / name).is_file(), name
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    assert not app.exception, str(app.exception)
    capacities = list(app.selectbox[0].options)
    for capacity in capacities:
        app.selectbox[0].select(capacity).run()
        assert not app.exception, f"{capacity}: {app.exception}"
    content = generar_excel([{"Catalogo": "PRUEBA", "Descripcion": "Prueba", "Cantidad": 2, "Precio": 100}], 0.9)
    sheet = openpyxl.load_workbook(BytesIO(content)).active
    assert sheet.cell(2, 6).value == 180
    Path(output).write_text(json.dumps({"ok": True, "sheets": list(catalog.hojas), "capacities": capacities, "excel": "ok"}, indent=2), encoding="utf-8")


def launch():
    import ctypes

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    command = [sys.executable]
    if not getattr(sys, "frozen", False):
        command.append(str(Path(__file__).resolve()))
    command.extend(["--server", str(port)])
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"session-{os.getpid()}.log"
    log = log_path.open("w", encoding="utf-8")
    child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=log,
                             creationflags=subprocess.CREATE_NO_WINDOW)

    def close():
        if child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
        log.close()

    started = time.monotonic()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    try:
        while child.poll() is None:
            if time.monotonic() - started > 120:
                raise RuntimeError(
                    f"Se agotó el tiempo de inicio. Consulta: {log_path}"
                )

            try:
                with opener.open(url + "/_stcore/health", timeout=0.5) as response:
                    if response.status == 200:
                        if not webbrowser.open(url):
                            ctypes.windll.user32.MessageBoxW(
                                0,
                                f"Abre esta dirección en tu navegador:\n{url}",
                                "Eaton EDS",
                                0x40
                            )
                        break
            except OSError:
                pass

            time.sleep(0.25)

        if child.poll() is not None:
            raise RuntimeError(
                f"La aplicación se detuvo. Consulta: {log_path}"
            )

        while child.poll() is None:
            time.sleep(1)
    finally:
        close()


if __name__ == "__main__":
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    # Windowed executables have no stdout/stderr; libraries still expect streams.
    if sys.stdout is None:
        sys.stdout = (LOG_DIR / f"launcher-{os.getpid()}.log").open("a", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = sys.stdout
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--server":
            serve(int(sys.argv[2]))
        elif len(sys.argv) > 1 and sys.argv[1] == "--self-test":
            self_test(sys.argv[2])
        else:
            launch()
    except Exception:
        details = traceback.format_exc()
        (LOG_DIR / "error.log").write_text(details, encoding="utf-8")
        if len(sys.argv) == 1:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, f"No se pudo iniciar Eaton EDS.\nConsulta: {LOG_DIR / 'error.log'}", "Eaton EDS", 16)
        sys.exit(1)
