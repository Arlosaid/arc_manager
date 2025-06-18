#!/bin/bash

echo "🚀 Despliegue Docker para AWS Elastic Beanstalk"

# Verificar que estamos en el directorio correcto
if [ ! -f "Dockerfile" ]; then
    echo "❌ Error: No se encontró Dockerfile"
    exit 1
fi

# Verificar EB CLI
if ! command -v eb &> /dev/null; then
    echo "❌ Error: EB CLI no instalado. Instalar: pip install awsebcli"
    exit 1
fi

# Verificar configuración EB
if [ ! -f ".elasticbeanstalk/config.yml" ]; then
    echo "❌ Error: No configurado EB. Ejecutar: eb init"
    exit 1
fi

# Limpiar archivos temporales
echo "🧹 Limpiando archivos temporales..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
rm -f arc_manager/db.sqlite3

echo "⚠️  IMPORTANTE: Configurar variables en EB Console:"
echo "   DATABASE_URL=postgresql://user:pass@host:5432/db"
echo "   SECRET_KEY=tu-clave-secreta"
echo "   DEBUG=False"
echo ""

# Desplegar
echo "🚀 Desplegando..."
if eb deploy --verbose; then
    echo "✅ ¡Despliegue exitoso!"
    echo "🔍 Estado: eb status"
    echo "🌐 Abrir: eb open"
    echo "📋 Logs: eb logs"
else
    echo "❌ Falló el despliegue"
    echo "📋 Ver logs: eb logs"
    exit 1
fi 