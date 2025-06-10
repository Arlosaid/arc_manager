#!/usr/bin/env python
"""
Script para debuggear los nombres de usuarios en la base de datos
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/c:/Users/Alonso/Desktop/arc_manager/arc_manager')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arc_manager.settings')
django.setup()

from apps.accounts.models import User

def check_user_names():
    print("=== DEBUG: Nombres de Usuarios ===")
    print()
    
    users = User.objects.all()
    print(f"Total de usuarios: {users.count()}")
    print()
    
    for user in users:
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"First Name: '{user.first_name}' (len: {len(user.first_name) if user.first_name else 0})")
        print(f"Last Name: '{user.last_name}' (len: {len(user.last_name) if user.last_name else 0})")
        print(f"Full Name: '{user.full_name}'")
        print(f"Avatar Initials: '{user.first_name[:1] if user.first_name else ''}{user.last_name[:1] if user.last_name else ''}'")
        print("-" * 50)

if __name__ == "__main__":
    check_user_names() 