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
    for name in ("eaton_logo.ico", "eaton_logo.png", "BZM.png", "PDG.png", "F.png", "J.png", "K.png", "L.png"):
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
    import tkinter as tk
    from tkinter import messagebox

    window = tk.Tk()
    window.title("Eaton · EDS Orders")
    window.geometry("460x210")
    window.resizable(False, False)
    window.iconbitmap(str(ROOT / "assets" / "eaton_logo.ico"))
    window.configure(bg="#f4f6f8")
    status = tk.StringVar(value="Iniciando la aplicación…")
    tk.Label(window, text="EATON  |  EDS Orders", font=("Segoe UI", 18, "bold"), fg="#005eb8", bg="#f4f6f8").pack(pady=(18, 8))
    tk.Label(window, textvariable=status, font=("Segoe UI", 10), bg="#f4f6f8").pack()
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

    def open_browser():
        if not webbrowser.open(url):
            messagebox.showinfo("Abrir aplicación", f"Abre esta dirección en tu navegador:\n{url}")

    def close():
        if child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
        log.close()
        window.destroy()

    button = tk.Button(window, text="Abrir aplicación", command=open_browser, state="disabled")
    button.pack(pady=10)
    tk.Button(window, text="Cerrar aplicación", command=close).pack()
    window.protocol("WM_DELETE_WINDOW", close)
    started = time.monotonic()
    ready = False
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def check():
        nonlocal ready
        if child.poll() is not None:
            status.set("La aplicación se ha detenido.")
            button.configure(state="disabled")
            messagebox.showerror("Eaton EDS", f"No se pudo mantener la aplicación abierta.\nDetalles: {log_path}")
            return
        if not ready:
            try:
                with opener.open(url + "/_stcore/health", timeout=0.3) as response:
                    ready = response.status == 200
            except OSError:
                pass
            if ready:
                status.set("Aplicación en ejecución. Conserva esta ventana abierta.")
                button.configure(state="normal")
                open_browser()
            elif time.monotonic() - started > 120:
                messagebox.showerror("Eaton EDS", f"Se agotó el tiempo de inicio.\nDetalles: {log_path}")
                close()
                return
        window.after(1000, check)

    window.after(300, check)
    try:
        window.mainloop()
    finally:
        if child.poll() is None:
            child.terminate()
            child.wait(timeout=5)
        log.close()


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
