# Python 3.11 slim
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar código
COPY arc_manager/ ./arc_manager/

# Crear directorios
RUN mkdir -p /app/arc_manager/staticfiles \
    && mkdir -p /app/arc_manager/media \
    && mkdir -p /app/arc_manager/logs

# Directorio Django
WORKDIR /app/arc_manager

# Crear script de inicio
RUN echo '#!/bin/bash\n\
echo "🔍 Creando base de datos si no existe..."\n\
python manage.py create_database || echo "⚠️ Error creando DB - puede que ya exista"\n\
echo "🔄 Configurando aplicación completa..."\n\
python manage.py setup_database --force || echo "⚠️ Error configurando DB - continuando"\n\
echo "✅ Proceso de inicialización completado"\n\
echo "🚀 Iniciando servidor..."\n\
exec gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 core.wsgi:application' > /app/start.sh && chmod +x /app/start.sh

# Puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Ejecutar script de inicio
CMD ["/app/start.sh"] 