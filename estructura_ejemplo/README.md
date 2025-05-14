# Estructura Recomendada para Proyecto Django

```
TU_REPOSITORIO_GIT/  <-- Aquí está tu .git principal
├── arc_manager/  <-- Carpeta del proyecto Django (la que contiene manage.py)
│   ├── accounts/
│   ├── core/
│   ├── logs/
│   ├── static/
│   ├── templates/
│   ├── db.sqlite3
│   └── manage.py
├── .gitignore  <-- En la raíz
├── README.md  <-- En la raíz
└── requirements.txt <-- En la raíz
```

El entorno virtual (venv) **NO** debe incluirse en el repositorio Git. 
Debería estar en tu .gitignore y típicamente se coloca:

1. Fuera del repositorio por completo, o
2. En la raíz del repositorio (pero excluido de Git)

## Ventajas de esta estructura

1. Todos los archivos de configuración están en la raíz
2. El código del proyecto está organizado en su propio directorio
3. No hay anidamiento innecesario de directorios
4. Es compatible con las prácticas estándar de despliegue 