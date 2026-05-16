# 1. Crear el entorno virtual
python -m venv core/venv
# 2. Activar el entorno virtual
& core/venv/Scripts/Activate.ps1
# 3. Instalar dependencias
pip install -r core/requirements.txt

# 4. Instalar dependencias de React en /web
if (Test-Path "web/package.json") {
    Set-Location web
    npm install
    Set-Location ..
} else {
    Write-Host "No se encontro web/package.json, saltando instalacion de React."
}
