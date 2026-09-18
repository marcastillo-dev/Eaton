# Eaton EDS Orders

Aplicación Streamlit para configurar órdenes EDS.

## Estructura

```text
app.py                  # Punto de entrada de Streamlit
assets/                 # Imágenes usadas por la interfaz
data/                   # Catálogo de productos
docs/                   # Documentación y listas de precios
src/eaton/config/       # Configuración de la aplicación
src/eaton/services/     # Lógica de negocio y acceso a datos
src/eaton/ui/           # Componentes de la interfaz
```

## Ejecución local

Instala las dependencias y ejecuta la aplicación desde la raíz del proyecto:

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```