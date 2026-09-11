# AgroControl Pro

Plataforma B2B de gestión agrícola integral: autenticación JWT, dashboard operativo,
inventario y bodegas (kardex), producción agrícola por ciclos y administración de
fincas, lotes, proveedores y usuarios.

## Arquitectura

```
agrocontrol-pro/
├── docker-compose.yml        # Orquesta backend + PostgreSQL + frontend (Nginx)
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini            # Migraciones
│   ├── alembic/
│   └── app/
│       ├── database.py        # Motor SQLAlchemy (Postgres o SQLite fallback)
│       ├── models.py          # Modelos ORM (Usuario, Finca, Lote, Potrero,
│       │                        Producto, MovimientoInventario, CicloProductivo,
│       │                        ActividadDiaria, Cosecha, Animal, Alerta, Proveedor)
│       ├── schemas.py         # Esquemas Pydantic v2
│       ├── auth.py            # JWT + bcrypt + bootstrap de usuario maestro
│       ├── repositories/      # Acceso a datos por agregado
│       ├── services/          # Reglas de negocio de autenticación e inventario
│       ├── main.py            # App FastAPI, CORS, startup
│       └── routers/
│           ├── auth_router.py     # /api/auth/*
│           ├── dashboard.py       # /api/dashboard/*
│           ├── inventory.py       # /api/inventario/*
│           ├── production.py      # /api/produccion/*
│           └── admin.py           # /api/admin/*
└── frontend/
    ├── index.html             # Shell de la SPA
    ├── css/variables.css      # Variables de tema claro/oscuro
    └── js/
        ├── views/             # Renderizado de vistas
        └── components/        # Componentes y acciones reutilizables
```

**Stack:** FastAPI (async) + SQLAlchemy + Alembic + PostgreSQL/SQLite + JWT + bcrypt.
El frontend es una SPA estática servida por Nginx, que consume la API vía `fetch`.

## Autenticación

- Endpoint: `POST /api/auth/register` (correo obligatorio, contraseña de mínimo 8 caracteres)
- Endpoint: `POST /api/auth/login`
- Acepta como `identificador`: correo, teléfono o nombre de usuario.
- **Credenciales maestras de prueba** (se crean automáticamente al arrancar el backend):
  - Identificador: `julian arrieta`
  - Contraseña: `arrieta`
- La contraseña se almacena únicamente como hash `bcrypt`; el login la valida con
  `passlib`. El token JWT resultante se firma con `JWT_SECRET_KEY` (variable de
  entorno) y expira según `ACCESS_TOKEN_EXPIRE_MINUTES` (por defecto 8 horas).

## Ejecución con Docker (recomendado)

```bash
# 1. Clona o descomprime el proyecto y entra a la carpeta raíz
cd agrocontrol-pro

# 2. Construye y levanta todos los servicios (backend + PostgreSQL + frontend)
docker compose up --build

# 3. Accede a:
#    - Frontend (Dashboard):  http://localhost:8080
#    - API + Swagger UI:      http://localhost:8000/docs
#    - Redoc:                 http://localhost:8000/redoc
```

Al arrancar, el backend crea las tablas automáticamente y siembra el usuario maestro
`julian arrieta / arrieta`. Ingresa con esas credenciales en `http://localhost:8080`.

Para detener los servicios:
```bash
docker compose down
```

Para reiniciar limpiando la base de datos (borra el volumen de Postgres):
```bash
docker compose down -v
docker compose up --build
```

## Migraciones con Alembic (opcional, para producción)

El backend crea las tablas automáticamente en el arranque (`Base.metadata.create_all`)
para poder probarse de inmediato. En un entorno productivo se recomienda gestionar el
esquema exclusivamente con Alembic:

```bash
docker compose exec backend alembic revision --autogenerate -m "estructura inicial"
docker compose exec backend alembic upgrade head
```

## Ejecución local sin Docker (desarrollo rápido)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # En Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Sin DATABASE_URL definido, se usa SQLite local automáticamente
export MASTER_USER_NAME="julian arrieta"
export MASTER_USER_PASSWORD="arrieta"
export JWT_SECRET_KEY="clave-de-desarrollo"

uvicorn app.main:app --reload --port 8000
```

Luego abre `frontend/index.html` directamente en el navegador (o sírvelo con
`python -m http.server 8080` desde la carpeta `frontend/`). Como no habrá Nginx,
verifica que `API_BASE` en `index.html` (`http://localhost:8000` por defecto)
coincida con la URL de tu backend.

## Módulos y endpoints principales

| Módulo | Endpoints |
|---|---|
| Autenticación | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me` |
| Dashboard | `GET /api/dashboard/resumen` |
| Inventario | `/api/inventario/bodegas`, `/api/inventario/productos`, `/api/inventario/movimientos` (CRUD) |
| Producción | `/api/produccion/ciclos`, `/api/produccion/actividades`, `/api/produccion/cosechas` (CRUD) |
| Administración | `/api/admin/fincas`, `/api/admin/lotes`, `/api/admin/potreros`, `/api/admin/animales`, `/api/admin/proveedores`, `/api/admin/usuarios` (CRUD, usuarios requiere rol admin) |

Toda la documentación interactiva (probar cada endpoint, ver esquemas Pydantic,
generar tokens) está disponible en **Swagger UI**: `http://localhost:8000/docs`.

## Notas de seguridad para producción

- Cambia `JWT_SECRET_KEY` y la contraseña de PostgreSQL antes de desplegar.
- Restringe `CORS_ORIGINS` al dominio real del frontend (no dejar `*`).
- Considera rotar o eliminar el usuario maestro de pruebas una vez creados los
  usuarios reales, o cambiar su contraseña desde `PUT /api/admin/usuarios/{id}`.
