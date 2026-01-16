#!/bin/bash
# Script para iniciar el frontend en py12env

echo "🎨 Iniciando frontend de Property Management System..."
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

# Configurar URL del backend
export API_BASE_URL=http://localhost:8000/api/v1

# Iniciar Streamlit
echo "🔥 Iniciando Streamlit en http://localhost:8501"
echo ""

streamlit run app.py
