# Property Management System - Migrated Architecture

## 🏗️ Nueva Arquitectura en Capas

Este proyecto ha sido refactorizado siguiendo una arquitectura en capas (Layered Architecture) que separa claramente frontend y backend.

## 📁 Estructura del Proyecto

```
property_management_system/
├── backend/                    # API Backend (FastAPI)
│   ├── database/              # Configuración de base de datos
│   │   └── connection.py      # Gestión de conexiones MySQL
│   ├── models/                # Modelos de datos (Pydantic)
│   │   └── booking.py         # Modelos de Booking
│   ├── repositories/          # Acceso a datos
│   │   └── booking_repository.py  # CRUD de bookings
│   ├── services/              # Lógica de negocio
│   │   └── booking_service.py     # Casos de uso de bookings
│   ├── routers/               # Endpoints API
│   │   └── bookings.py        # Rutas de bookings
│   ├── main.py                # FastAPI app principal
│   ├── config.py              # Configuración
│   └── requirements.txt       # Dependencias backend
│
├── frontend/                  # Frontend (Streamlit)
│   ├── components/            # Componentes UI (TODO)
│   ├── services/              # Comunicación con backend
│   │   └── api_client.py      # Cliente HTTP para API
│   ├── utils/                 # Utilidades
│   ├── app.py                 # App Streamlit (original, a migrar)
│   └── requirements.txt       # Dependencias frontend
│
├── shared/                    # Código compartido
│   └── constants.py           # Constantes globales
│
├── .env                       # Variables de entorno
├── docker-compose.new.yml     # Nueva configuración Docker
├── Dockerfile.backend         # Dockerfile para backend
├── Dockerfile.frontend        # Dockerfile para frontend
└── README.md                  # Este archivo
```

## 🚀 Cómo Ejecutar

### Opción 1: Con Docker (Recomendado)

```bash
# Usar la nueva configuración de docker-compose
docker-compose -f docker-compose.new.yml up --build

# Acceder a:
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Frontend: http://localhost:8501
```

### Opción 2: Desarrollo Local

#### Backend (FastAPI)
```bash
# Instalar dependencias
pip install -r backend/requirements.txt

# Ejecutar servidor
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Acceder a docs: http://localhost:8000/docs
```

#### Frontend (Streamlit)
```bash
# Instalar dependencias
pip install -r frontend/requirements.txt

# Configurar URL del backend
export API_BASE_URL=http://localhost:8000/api/v1

# Ejecutar app
streamlit run frontend/app.py
```

## 📡 API Endpoints

### Bookings

- `GET /api/v1/bookings/` - Listar todos los bookings
- `GET /api/v1/bookings/{id}` - Obtener booking específico
- `GET /api/v1/bookings/active` - Bookings activos
- `GET /api/v1/bookings/upcoming-checkins` - Próximos check-ins
- `GET /api/v1/bookings/upcoming-checkouts` - Próximos check-outs
- `GET /api/v1/bookings/calendar-events` - Eventos para calendario
- `POST /api/v1/bookings/` - Crear booking
- `PUT /api/v1/bookings/{id}` - Actualizar booking
- `DELETE /api/v1/bookings/{id}` - Eliminar booking

Ver documentación completa en: `http://localhost:8000/docs`

## 🔄 Estado de la Migración

### ✅ Completado

- [x] Estructura de carpetas backend
- [x] Modelos de datos con Pydantic
- [x] Repositorio de base de datos
- [x] Servicio de negocio
- [x] API REST con FastAPI
- [x] Cliente API para frontend
- [x] Dockerfiles separados
- [x] Docker Compose actualizado

### 🚧 Pendiente

- [ ] Refactorizar frontend/app.py en componentes
- [ ] Migrar lógica de calendario a componentes
- [ ] Migrar tabla de bookings a componentes
- [ ] Migrar modal de detalles a componentes
- [ ] Actualizar frontend para usar API client
- [ ] Escribir tests unitarios
- [ ] Escribir tests de integración

## 🔧 Configuración

Asegúrate de tener un archivo `.env` con las siguientes variables:

```env
# Database
DB_HOST=your_db_host
DB_USER=your_db_user
DB_PASS=your_db_password
DB_NAME=your_db_name
DB_PORT=3306

# Electric allowance bookings (comma-separated)
ELECTRIC=BK-001,BK-002

# Backend API URL (para frontend)
API_BASE_URL=http://localhost:8000/api/v1
```

## 📝 Notas de Migración

### Retrocompatibilidad

Los archivos antiguos en `services/` se mantienen temporalmente para compatibilidad con `app.py`. 
Una vez migrado el frontend, estos archivos pueden eliminarse.

### Uso del API Client

Ejemplo de uso en el frontend:

```python
from frontend.services.api_client import api_client

# Obtener bookings
bookings = api_client.get_bookings(days=14)

# Obtener eventos de calendario
events = api_client.get_calendar_events(days=90)

# Crear booking
new_booking = api_client.create_booking({
    "booking_id": "BK-2026-001",
    "guest_name": "John Doe",
    "check_in": "2026-01-20",
    "check_out": "2026-01-25",
    # ... más campos
})
```

## 🎯 Próximos Pasos

1. **Migrar componentes del frontend** - Extraer lógica de `app.py`
2. **Conectar frontend con backend** - Usar API client en lugar de acceso directo a DB
3. **Añadir tests** - Cobertura de código
4. **Mejorar documentación** - Swagger/OpenAPI
5. **Añadir autenticación** - JWT o similar

## 📚 Tecnologías

- **Backend**: FastAPI, Pydantic, MySQL Connector
- **Frontend**: Streamlit, Pandas
- **Database**: MySQL
- **Deployment**: Docker, Docker Compose
