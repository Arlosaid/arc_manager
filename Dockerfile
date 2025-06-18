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
echo "🔄 Aplicando migraciones..."\n\
python manage.py migrate --noinput\n\
echo "📦 Recopilando archivos estáticos..."\n\
python manage.py collectstatic --noinput\n\
echo "👤 Creando superusuario..."\n\
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser(\"admin\", \"admin@example.com\", \"admin123\") if not User.objects.filter(is_superuser=True).exists() else print(\"✅ Superuser exists\")" || echo "Superuser creation skipped"\n\
echo "📋 Configurando planes..."\n\
python manage.py setup_mvp_plans || echo "Plans setup skipped"\n\
echo "🚀 Iniciando servidor..."\n\
exec gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 core.wsgi:application' > /app/start.sh && chmod +x /app/start.sh

# Puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Ejecutar script de inicio
CMD ["/app/start.sh"] 