#!/bin/bash

# ========================================
# COMANDOS RAPIDOS PARA GESTION DE DATOS
# ========================================

mostrar_menu() {
    clear
    echo "========================================"
    echo "🚀 COMANDOS RAPIDOS DE GESTION DE DATOS"
    echo "========================================"
    echo ""
    echo "Selecciona una opción:"
    echo ""
    echo "1. 📊 Ver resumen del sistema"
    echo "2. 🏗️  Crear datos de ejemplo (3 orgs, 5 usuarios c/u)"
    echo "3. 🏗️  Crear datos de ejemplo (RESET + 3 orgs, 5 usuarios c/u)"
    echo "4. 🏢 Crear organización básica"
    echo "5. 👤 Crear usuario básico"
    echo "6. 📋 Listar organizaciones"
    echo "7. 🎮 Script interactivo completo"
    echo "8. ❌ Salir"
    echo ""
}

resumen() {
    echo ""
    echo "📊 MOSTRANDO RESUMEN DEL SISTEMA..."
    python manage.py list_orgs
    echo ""
    read -p "Presiona Enter para continuar..."
}

datos_ejemplo() {
    echo ""
    echo "🏗️ CREANDO DATOS DE EJEMPLO..."
    python manage.py setup_demo_data
    echo ""
    read -p "Presiona Enter para continuar..."
}

datos_ejemplo_reset() {
    echo ""
    echo "🏗️ CREANDO DATOS DE EJEMPLO (CON RESET)..."
    python manage.py setup_demo_data --reset
    echo ""
    read -p "Presiona Enter para continuar..."
}

crear_org() {
    echo ""
    read -p "Nombre de la organización: " nombre
    if [ -z "$nombre" ]; then
        echo "❌ El nombre es obligatorio"
        read -p "Presiona Enter para continuar..."
        return
    fi
    echo "🏢 CREANDO ORGANIZACIÓN..."
    python manage.py create_organization "$nombre"
    echo ""
    read -p "Presiona Enter para continuar..."
}

crear_usuario() {
    echo ""
    read -p "Email del usuario: " email
    if [ -z "$email" ]; then
        echo "❌ El email es obligatorio"
        read -p "Presiona Enter para continuar..."
        return
    fi
    echo "👤 CREANDO USUARIO..."
    python manage.py create_user "$email"
    echo ""
    read -p "Presiona Enter para continuar..."
}

listar_orgs() {
    echo ""
    echo "📋 LISTANDO ORGANIZACIONES..."
    python manage.py list_orgs --detailed
    echo ""
    read -p "Presiona Enter para continuar..."
}

script_interactivo() {
    echo ""
    echo "🎮 INICIANDO SCRIPT INTERACTIVO..."
    python scripts_demo.py
    echo ""
    read -p "Presiona Enter para continuar..."
}

# Bucle principal
while true; do
    mostrar_menu
    read -p "Ingresa tu opción (1-8): " opcion
    
    case $opcion in
        1)
            resumen
            ;;
        2)
            datos_ejemplo
            ;;
        3)
            datos_ejemplo_reset
            ;;
        4)
            crear_org
            ;;
        5)
            crear_usuario
            ;;
        6)
            listar_orgs
            ;;
        7)
            script_interactivo
            ;;
        8)
            echo ""
            echo "👋 ¡Hasta luego!"
            exit 0
            ;;
        *)
            echo "❌ Opción inválida"
            read -p "Presiona Enter para continuar..."
            ;;
    esac
done 