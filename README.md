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

## Ejecutable portable para Windows

El archivo que se comparte es **`dist/EatonEDS.exe`**. Incluye Python, las
dependencias, el catálogo de `data/` y las imágenes de `assets/`. Usa
`assets/eaton_logo.ico` como icono del ejecutable y de la ventana de inicio.
No necesita instalar Python, Excel ni ejecutar comandos en la computadora del usuario.
Está dirigido a Windows 10/11 de 64 bits con un navegador instalado.

1. Copia `EatonEDS.exe` a la computadora de destino y haz doble clic.
2. Espera el inicio: el archivo extrae sus dependencias a una carpeta temporal.
3. La aplicación se abre automáticamente en el navegador predeterminado.
4. Conserva abierta la ventana **Eaton · EDS Orders**. Puedes usar **Abrir aplicación**
   para regresar a la interfaz y **Cerrar aplicación** para detener el servidor local.

La interfaz funciona localmente en `127.0.0.1`, sin necesitar internet para cargar
el catálogo. Cerrar solamente la pestaña del navegador no detiene el programa.
Las órdenes siguen almacenándose en la sesión, como en la aplicación original:
empaquetar el proyecto no agrega almacenamiento permanente.

### Generar nuevamente el EXE (solo en la computadora de desarrollo)

Se utilizó Python 3.14 de 64 bits. Desde PowerShell, en la raíz del proyecto:

```powershell
python build.py
```

El script crea `.venv-build`, instala las versiones de `requirements-build.txt`
y ejecuta PyInstaller con `EatonEDS.spec`. Después comprueba el catálogo, las
capacidades y la exportación Excel dentro del ejecutable. Necesita internet al instalar dependencias.
El usuario final únicamente recibe el EXE. Si cambias el catálogo, las imágenes o
el código, vuelve a compilar y distribuye el nuevo ejecutable.

Los archivos de `docs/` son material de referencia y no se usan en la interfaz;
no se incluyen en el ejecutable.

### Diagnóstico

Los registros se guardan en `%LOCALAPPDATA%\EatonEDS`.
Para ejecutar la comprobación integrada del catálogo, las capacidades y la
exportación Excel desde PowerShell:

```powershell
Start-Process .\dist\EatonEDS.exe -ArgumentList '--self-test', "$env:TEMP\eaton-test.json" -Wait
Get-Content "$env:TEMP\eaton-test.json"
```

El empaquetado utiliza la [configuración de PyInstaller](https://pyinstaller.org/en/stable/spec-files.html)
para incluir los recursos y las importaciones dinámicas de Streamlit.
