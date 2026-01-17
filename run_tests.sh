#!/bin/bash
# Script para ejecutar tests del backend

echo "🧪 Ejecutando tests del backend..."
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

python backend/test_backend.py
