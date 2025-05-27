#!/usr/bin/env python
"""
Script de utilidades para gestionar datos de demo
Ejecutar desde el directorio del proyecto: python scripts_demo.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from orgs.models import Organization

User = get_user_model()

def mostrar_menu():
    """Mostrar menú de opciones"""
    print("\n" + "="*50)
    print("🚀 SCRIPT DE GESTIÓN DE DATOS DE DEMO")
    print("="*50)
    print("1. 📊 Ver resumen del sistema")
    print("2. 🏗️  Crear datos de ejemplo completos")
    print("3. 🏢 Crear una organización")
    print("4. 👤 Crear un usuario")
    print("5. 📋 Listar organizaciones")
    print("6. 👥 Listar usuarios sin organización")
    print("7. 🗑️  Limpiar todos los datos (excepto superusuarios)")
    print("8. ❌ Salir")
    print("="*50)

def ver_resumen():
    """Mostrar resumen del sistema"""
    print("\n📊 RESUMEN DEL SISTEMA")
    print("-" * 30)
    
    total_orgs = Organization.objects.count()
    total_users = User.objects.count()
    superusers = User.objects.filter(is_superuser=True).count()
    users_with_org = User.objects.filter(organization__isnull=False).count()
    users_without_org = total_users - users_with_org
    
    print(f"🏢 Organizaciones: {total_orgs}")
    print(f"👥 Usuarios totales: {total_users}")
    print(f"⭐ Superusuarios: {superusers}")
    print(f"✅ Usuarios con organización: {users_with_org}")
    print(f"❌ Usuarios sin organización: {users_without_org}")
    
    if total_orgs > 0:
        print(f"\n🏢 ORGANIZACIONES:")
        for org in Organization.objects.all()[:5]:  # Mostrar solo las primeras 5
            status = "✅" if org.is_active else "❌"
            print(f"  {status} {org.name} ({org.get_user_count()}/{org.max_users} usuarios)")
        
        if total_orgs > 5:
            print(f"  ... y {total_orgs - 5} más")

def crear_datos_ejemplo():
    """Crear datos de ejemplo completos"""
    print("\n🏗️ CREANDO DATOS DE EJEMPLO")
    print("-" * 30)
    
    try:
        num_orgs = input("¿Cuántas organizaciones crear? (por defecto 3): ").strip()
        num_orgs = int(num_orgs) if num_orgs else 3
        
        users_per_org = input("¿Cuántos usuarios por organización? (por defecto 5): ").strip()
        users_per_org = int(users_per_org) if users_per_org else 5
        
        reset = input("¿Eliminar datos existentes primero? (s/N): ").strip().lower()
        reset_flag = reset in ['s', 'si', 'sí', 'y', 'yes']
        
        args = ['setup_demo_data', f'--orgs={num_orgs}', f'--users-per-org={users_per_org}']
        if reset_flag:
            args.append('--reset')
        
        call_command(*args)
        
    except ValueError:
        print("❌ Error: Ingresa números válidos")
    except Exception as e:
        print(f"❌ Error: {e}")

def crear_organizacion():
    """Crear una organización individual"""
    print("\n🏢 CREAR ORGANIZACIÓN")
    print("-" * 25)
    
    try:
        name = input("Nombre de la organización: ").strip()
        if not name:
            print("❌ El nombre es obligatorio")
            return
        
        description = input("Descripción (opcional): ").strip()
        max_users = input("Máximo de usuarios (por defecto 10): ").strip()
        max_users = int(max_users) if max_users else 10
        
        args = ['create_organization', name, f'--max-users={max_users}']
        if description:
            args.append(f'--description={description}')
        
        call_command(*args)
        
    except ValueError:
        print("❌ Error: Ingresa un número válido para máximo de usuarios")
    except Exception as e:
        print(f"❌ Error: {e}")

def crear_usuario():
    """Crear un usuario individual"""
    print("\n👤 CREAR USUARIO")
    print("-" * 20)
    
    try:
        email = input("Email del usuario: ").strip()
        if not email:
            print("❌ El email es obligatorio")
            return
        
        name = input("Nombre completo (opcional): ").strip()
        password = input("Contraseña (por defecto 'demo123'): ").strip()
        password = password if password else 'demo123'
        
        # Mostrar organizaciones disponibles
        orgs = Organization.objects.all()
        if orgs:
            print("\n🏢 Organizaciones disponibles:")
            for i, org in enumerate(orgs, 1):
                print(f"  {i}. {org.name} (slug: {org.slug}) - {org.get_user_count()}/{org.max_users} usuarios")
            
            org_choice = input("\nSelecciona organización (número o slug, opcional): ").strip()
            
            args = ['create_user', email, f'--password={password}']
            if name:
                args.append(f'--name={name}')
            
            if org_choice:
                if org_choice.isdigit():
                    org_index = int(org_choice) - 1
                    if 0 <= org_index < len(orgs):
                        args.append(f'--org-slug={orgs[org_index].slug}')
                    else:
                        print("❌ Número de organización inválido")
                        return
                else:
                    args.append(f'--org-slug={org_choice}')
            
            is_admin = input("¿Hacer administrador de la organización? (s/N): ").strip().lower()
            if is_admin in ['s', 'si', 'sí', 'y', 'yes']:
                args.append('--admin')
        else:
            print("⚠️ No hay organizaciones disponibles")
            args = ['create_user', email, f'--password={password}']
            if name:
                args.append(f'--name={name}')
        
        is_superuser = input("¿Crear como superusuario? (s/N): ").strip().lower()
        if is_superuser in ['s', 'si', 'sí', 'y', 'yes']:
            args.append('--superuser')
        
        call_command(*args)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def listar_organizaciones():
    """Listar organizaciones"""
    print("\n📋 LISTANDO ORGANIZACIONES")
    print("-" * 30)
    
    detailed = input("¿Mostrar información detallada? (s/N): ").strip().lower()
    detailed_flag = detailed in ['s', 'si', 'sí', 'y', 'yes']
    
    args = ['list_orgs']
    if detailed_flag:
        args.append('--detailed')
    
    call_command(*args)

def listar_usuarios_sin_org():
    """Listar usuarios sin organización"""
    print("\n👥 USUARIOS SIN ORGANIZACIÓN")
    print("-" * 30)
    
    detailed = input("¿Mostrar información detallada? (s/N): ").strip().lower()
    detailed_flag = detailed in ['s', 'si', 'sí', 'y', 'yes']
    
    args = ['list_orgs', '--users-only']
    if detailed_flag:
        args.append('--detailed')
    
    call_command(*args)

def limpiar_datos():
    """Limpiar todos los datos excepto superusuarios"""
    print("\n🗑️ LIMPIAR DATOS")
    print("-" * 20)
    
    confirm = input("⚠️ ¿Estás seguro de eliminar todos los datos? (escribe 'CONFIRMAR'): ").strip()
    if confirm == 'CONFIRMAR':
        try:
            User.objects.filter(is_superuser=False).delete()
            Organization.objects.all().delete()
            print("✅ Datos eliminados exitosamente (superusuarios conservados)")
        except Exception as e:
            print(f"❌ Error al eliminar datos: {e}")
    else:
        print("❌ Operación cancelada")

def main():
    """Función principal"""
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\nSelecciona una opción (1-8): ").strip()
            
            if opcion == '1':
                ver_resumen()
            elif opcion == '2':
                crear_datos_ejemplo()
            elif opcion == '3':
                crear_organizacion()
            elif opcion == '4':
                crear_usuario()
            elif opcion == '5':
                listar_organizaciones()
            elif opcion == '6':
                listar_usuarios_sin_org()
            elif opcion == '7':
                limpiar_datos()
            elif opcion == '8':
                print("\n👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida. Selecciona un número del 1 al 8.")
            
            input("\nPresiona Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            input("\nPresiona Enter para continuar...")

if __name__ == '__main__':
    main() 