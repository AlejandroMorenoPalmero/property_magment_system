# 🚀 Guía Rápida de Inicio - Property Management System

## ✅ Migración Completada

Se ha refactorizado exitosamente el proyecto a una **arquitectura en capas** con backend y frontend separados.

---

## 📦 Requisitos Previos

1. **Entorno virtual py12env activado**:
   ```bash
   conda activate py12env
   ```

2. **Dependencias instaladas**:
   - Backend: ✅ Instaladas (FastAPI, Pydantic, MySQL Connector, etc.)
   - Frontend: Instalar con `pip install -r frontend/requirements.txt`

---

## 🎯 Cómo Usar el Nuevo Sistema

### Opción 1: Usar Scripts Rápidos

#### 1️⃣ Ejecutar Tests del Backend
```bash
conda activate py12env
./run_tests.sh
```

#### 2️⃣ Iniciar Backend (FastAPI)
```bash
conda activate py12env
./start_backend.sh
```
- **Backend API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

#### 3️⃣ Iniciar Frontend (Streamlit) - En otra terminal
```bash
conda activate py12env
./start_frontend.sh
```
- **Frontend**: http://localhost:8501

---

### Opción 2: Comandos Manuales

#### Backend
```bash
conda activate py12env
cd "/home/alejandro/Enterprise Projects/property_magment_system"
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
conda activate py12env
cd "/home/alejandro/Enterprise Projects/property_magment_system"
export API_BASE_URL=http://localhost:8000/api/v1
streamlit run app.py
```

#### Tests
```bash
conda activate py12env
cd "/home/alejandro/Enterprise Projects/property_magment_system"
python backend/test_backend.py
```

---

## 🧪 Resultados de Tests

Todos los tests pasaron exitosamente:

```
==================================================
📊 TEST RESULTS
==================================================
Database Connection..................... ✅ PASSED
Pydantic Models......................... ✅ PASSED
Repository Layer........................ ✅ PASSED
Service Layer........................... ✅ PASSED
==================================================
🎉 All tests passed!
```

---

## 🔗 Endpoints API Disponibles

### Bookings
- `GET /api/v1/bookings/` - Listar bookings
- `GET /api/v1/bookings/{id}` - Obtener booking específico
- `GET /api/v1/bookings/active` - Bookings activos
- `GET /api/v1/bookings/upcoming-checkins` - Próximos check-ins
- `GET /api/v1/bookings/upcoming-checkouts` - Próximos check-outs
- `GET /api/v1/bookings/calendar-events` - Eventos para calendario
- `POST /api/v1/bookings/` - Crear booking
- `PUT /api/v1/bookings/{id}` - Actualizar booking
- `DELETE /api/v1/bookings/{id}` - Eliminar booking

**Ver documentación interactiva**: http://localhost:8000/docs

---

## 📁 Nueva Estructura

```
property_management_system/
├── backend/                    ✅ NUEVO - API REST
│   ├── database/              # Conexión a base de datos
│   ├── models/                # Modelos Pydantic
│   ├── repositories/          # Acceso a datos
│   ├── services/              # Lógica de negocio
│   ├── routers/               # Endpoints API
│   ├── main.py                # FastAPI app
│   └── test_backend.py        # Tests
│
├── frontend/                   ✅ REFACTORIZADO
│   ├── services/              # API client
│   ├── components/            # Componentes UI (TODO)
│   └── app.py                 # Streamlit app
│
├── shared/                     ✅ NUEVO - Código compartido
│   └── constants.py
│
├── services/                   ⚠️ DEPRECATED
│   ├── bbdd_conection.py      # Migrado a backend/database/
│   └── bbdd_query.py          # Migrado a backend/repositories/
│
├── start_backend.sh            ✅ Script rápido
├── start_frontend.sh           ✅ Script rápido
├── run_tests.sh                ✅ Script rápido
└── README.md                   ✅ Documentación completa
```

---

## 🎨 Probar la API

### Con curl:
```bash
# Obtener todos los bookings
curl http://localhost:8000/api/v1/bookings/

# Obtener bookings activos
curl http://localhost:8000/api/v1/bookings/active

# Obtener eventos de calendario
curl http://localhost:8000/api/v1/bookings/calendar-events
```

### Con el navegador:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🐳 Docker (Opcional)

Si prefieres usar Docker:

```bash
# Construir y ejecutar con docker-compose
docker-compose -f docker-compose.new.yml up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:8501
```

---

## ⚠️ Notas Importantes

1. **El frontend actual (app.py) sigue funcionando igual** - No se ha roto nada
2. **El backend está completamente funcional** - Todos los tests pasan
3. **Próximo paso**: Refactorizar frontend para usar el API client
4. **Carpeta services/ deprecated**: Se mantendrá hasta migrar completamente el frontend

---

## 🆘 Solución de Problemas

### Error: "No module named 'pydantic'"
```bash
conda activate py12env
pip install -r backend/requirements.txt
```

### Error: "Command 'uvicorn' not found"
```bash
# Usar el módulo de Python
python -m uvicorn backend.main:app --reload
```

### Error de conexión a base de datos
```bash
# Verificar archivo .env
cat .env | grep DB_

# Ejecutar test de conexión
python backend/test_backend.py
```

---

## 📞 Soporte

Para más información, revisa:
- `README.md` - Documentación completa
- `backend/test_backend.py` - Ejemplos de uso
- http://localhost:8000/docs - Documentación API interactiva
