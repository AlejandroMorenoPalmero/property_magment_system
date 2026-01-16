#!/bin/bash
# Script para iniciar el backend en py12env

echo "🚀 Iniciando backend de Property Management System..."
echo ""

# Verificar que estamos en py12env
if [[ "$CONDA_DEFAULT_ENV" != "py12env" ]]; then
    echo "⚠️  No estás en el entorno py12env"
    echo "Por favor ejecuta primero: conda activate py12env"
    exit 1
fi

# Cambiar al directorio del proyecto
cd "/home/alejandro/Enterprise Projects/property_magment_system"

echo "✅ Entorno: $CONDA_DEFAULT_ENV"
echo "📂 Directorio: $(pwd)"
echo ""

# Iniciar servidor FastAPI
echo "🔥 Iniciando servidor FastAPI en http://localhost:8000"
echo "📚 Documentación disponible en http://localhost:8000/docs"
echo ""

python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
