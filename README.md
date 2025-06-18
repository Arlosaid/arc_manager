# 🏢 Arc Manager

Sistema de gestión organizacional con Django + PostgreSQL en Docker.

## 🚀 Despliegue en AWS Elastic Beanstalk

### 1. Configuración inicial
```bash
eb init
eb create --single-instance
```

### 2. Variables de entorno (EB Console)
```
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=*
```

### 3. Desplegar
```bash
./deploy.sh
```

## 🐳 Desarrollo Local
```bash
docker build -t arc-manager .
docker run -p 8000:8000 arc-manager
```

## 📋 Comandos útiles
- **Estado**: `eb status`
- **Logs**: `eb logs`
- **Abrir app**: `eb open`
- **SSH**: `eb ssh`

## 🔧 Estructura
- **Django App**: `/arc_manager/`
- **Docker**: `Dockerfile`
- **Deploy**: `deploy.sh`
- **Config EB**: `.ebextensions/`

Las migraciones y configuración se aplican automáticamente.

## 💰 Costo: $0 durante 12 meses
- EC2 t2.micro: Gratis (750 horas/mes)
- RDS db.t2.micro: Gratis (750 horas/mes)
- 20GB storage: Incluido

## 📁 Archivos esenciales
- `Dockerfile` - Imagen Docker
- `Dockerrun.aws.json` - Configuración EB
- `.ebextensions/02_django.config` - Configuración Django
- `deploy.sh` - Script de despliegue

## ⚡ Alternativa con SQLite (100% gratis)
Para evitar costos de RDS, puedes usar SQLite modificando `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
``` 