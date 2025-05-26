@echo off
REM ========================================
REM COMANDOS RAPIDOS PARA GESTION DE DATOS
REM ========================================

echo.
echo ========================================
echo 🚀 COMANDOS RAPIDOS DE GESTION DE DATOS
echo ========================================
echo.
echo Selecciona una opcion:
echo.
echo 1. 📊 Ver resumen del sistema
echo 2. 🏗️  Crear datos de ejemplo (3 orgs, 5 usuarios c/u)
echo 3. 🏗️  Crear datos de ejemplo (RESET + 3 orgs, 5 usuarios c/u)
echo 4. 🏢 Crear organizacion basica
echo 5. 👤 Crear usuario basico
echo 6. 📋 Listar organizaciones
echo 7. 🎮 Script interactivo completo
echo 8. ❌ Salir
echo.

set /p opcion="Ingresa tu opcion (1-8): "

if "%opcion%"=="1" goto resumen
if "%opcion%"=="2" goto datos_ejemplo
if "%opcion%"=="3" goto datos_ejemplo_reset
if "%opcion%"=="4" goto crear_org
if "%opcion%"=="5" goto crear_usuario
if "%opcion%"=="6" goto listar_orgs
if "%opcion%"=="7" goto script_interactivo
if "%opcion%"=="8" goto salir

echo ❌ Opcion invalida
pause
goto inicio

:resumen
echo.
echo 📊 MOSTRANDO RESUMEN DEL SISTEMA...
python manage.py list_orgs
pause
goto inicio

:datos_ejemplo
echo.
echo 🏗️ CREANDO DATOS DE EJEMPLO...
python manage.py setup_demo_data
pause
goto inicio

:datos_ejemplo_reset
echo.
echo 🏗️ CREANDO DATOS DE EJEMPLO (CON RESET)...
python manage.py setup_demo_data --reset
pause
goto inicio

:crear_org
echo.
set /p nombre="Nombre de la organizacion: "
if "%nombre%"=="" (
    echo ❌ El nombre es obligatorio
    pause
    goto inicio
)
echo 🏢 CREANDO ORGANIZACION...
python manage.py create_organization "%nombre%"
pause
goto inicio

:crear_usuario
echo.
set /p email="Email del usuario: "
if "%email%"=="" (
    echo ❌ El email es obligatorio
    pause
    goto inicio
)
echo 👤 CREANDO USUARIO...
python manage.py create_user "%email%"
pause
goto inicio

:listar_orgs
echo.
echo 📋 LISTANDO ORGANIZACIONES...
python manage.py list_orgs --detailed
pause
goto inicio

:script_interactivo
echo.
echo 🎮 INICIANDO SCRIPT INTERACTIVO...
python scripts_demo.py
pause
goto inicio

:salir
echo.
echo 👋 ¡Hasta luego!
exit

:inicio
cls
goto :eof 