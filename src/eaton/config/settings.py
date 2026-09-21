from pathlib import Path

PAGE_TITLE = "CPDI Orders"

PRIMARY_COLOR = "#005EB8"
SECONDARY_COLOR = "#0A2342"

BASE_DIR = Path(__file__).resolve().parents[3]
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"

LOGO = ASSETS_DIR / "eaton_logo.png"
LOGO_ICON = ASSETS_DIR / "eaton_icon.png"
CATALOGO = DATA_DIR / "catalogo_productos.xlsx"