@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Criando o ambiente virtual...
    py -m venv .venv
    if errorlevel 1 goto erro
)

echo Instalando ou atualizando as dependencias Panda3D...
".venv\Scripts\python.exe" -m pip install --pre --extra-index-url https://archive.panda3d.org/ -r requirements.txt
if errorlevel 1 goto erro

echo Iniciando o app: python main.py
".venv\Scripts\python.exe" main.py
if errorlevel 1 goto erro

pause
exit /b 0

:erro
echo.
echo Nao foi possivel preparar ou iniciar o projeto.
echo Confira se o Python esta instalado e disponivel pelo comando py.
pause
exit /b 1
