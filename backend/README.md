# AgroControl Pro - Backend API

Backend profesional para AgroControl Pro, desarrollado con **FastAPI** y **SQLAlchemy**.

## 📋 Descripción

API REST completa para gestión agrícola integral con:
- ✅ Autenticación JWT
- ✅ CRUD completo para Insumos, Ganado y Maquinaria
- ✅ Base de datos MySQL
- ✅ Validación de datos con Pydantic
- ✅ CORS configurado para frontend
- ✅ Documentación interactiva (Swagger)

## 🚀 Inicio Rápido

### 1. Requisitos Previos
- Python 3.8+
- MySQL Server
- pip (gestor de paquetes Python)

### 2. Instalación

```bash
# Navegar a la carpeta backend
cd backend/

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración de Base de Datos

```bash
# Crear base de datos MySQL
mysql -u root -p
CREATE DATABASE agrocontrol_pro;
EXIT;
```

### 4. Configurar Variables de Entorno

```bash
# Copiar archivo .env.example a .env
cp .env.example .env

# Editar .env con credenciales reales:
# DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost:3306/agrocontrol_pro
# SECRET_KEY=tu-clave-secreta-muy-larga-minimo-32-caracteres
```

### 5. Ejecutar Servidor

```bash
python main.py
# O usar uvicorn directamente:
# uvicorn main:app --reload --host 0.0.0.0 --port 3000
```

El servidor iniciará en: `http://localhost:3000`

## 📚 Documentación de API

### Acceder a Documentación Interactiva

- **Swagger UI**: http://localhost:3000/api/docs
- **ReDoc**: http://localhost:3000/api/redoc
- **OpenAPI JSON**: http://localhost:3000/api/openapi.json

## 🔐 Autenticación

### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "usuario@example.com",
  "password": "contraseña123"
}

Respuesta:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id_usuario": 1,
    "nombre_usuario": "usuario",
    "email": "usuario@example.com",
    "rol": "secretary",
    "fecha_registro": "2024-08-12",
    "estado": "active"
  }
}
```

### Registrar Usuario
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "nuevo@example.com",
  "nombre_usuario": "nuevoUsuario",
  "password": "contraseña123"
}
```

### Verificar Token
```bash
GET /api/auth/verify
Authorization: Bearer <token>

Respuesta: Usuario autenticado
```

## 📦 Endpoints de Insumos

### Listar todos
```bash
GET /api/insumos
Authorization: Bearer <token>
```

### Obtener contador
```bash
GET /api/insumos/count
Authorization: Bearer <token>
```

### Obtener por ID
```bash
GET /api/insumos/{id}
Authorization: Bearer <token>
```

### Crear insumo
```bash
POST /api/insumos
Authorization: Bearer <token>
Content-Type: application/json

{
  "nombre": "Fertilizante NPK 15-15-15",
  "tipo": "fertilizante",
  "cantidad": 50,
  "unidad": "kg",
  "precio": 25000,
  "proveedor": "Agroquímica SAS",
  "lote": "LOT-2024-001",
  "fecha": "2024-08-12"
}
```

### Actualizar insumo
```bash
PUT /api/insumos/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "cantidad": 45,
  "precio": 26000
}
```

### Eliminar insumo
```bash
DELETE /api/insumos/{id}
Authorization: Bearer <token>
```

## 🐄 Endpoints de Ganado

### Listar todos
```bash
GET /api/livestock
Authorization: Bearer <token>
```

### Obtener contador
```bash
GET /api/livestock/count
Authorization: Bearer <token>
```

### Crear animal
```bash
POST /api/livestock
Authorization: Bearer <token>
Content-Type: application/json

{
  "id_animal_str": "BOV-001",
  "nombre_animal": "Bessie",
  "tipo_animal": "bovino",
  "raza": "Holstein",
  "sexo": "F",
  "edad": 36,
  "peso": 450.5,
  "fecha_nacimiento": "2021-08-12",
  "estado_salud": "good",
  "valor_animal": 3000000
}
```

### Agregar peso
```bash
POST /api/livestock/{animal_id}/pesajes
Authorization: Bearer <token>
Content-Type: application/json

{
  "peso": 451.2,
  "fecha_pesaje": "2024-08-12",
  "observaciones": "Peso después de alimentación"
}
```

### Obtener pesajes
```bash
GET /api/livestock/{animal_id}/pesajes
Authorization: Bearer <token>
```

## 🚜 Endpoints de Maquinaria

### Listar todos
```bash
GET /api/machinery
Authorization: Bearer <token>
```

### Obtener contador
```bash
GET /api/machinery/count
Authorization: Bearer <token>
```

### Crear equipo
```bash
POST /api/machinery
Authorization: Bearer <token>
Content-Type: application/json

{
  "codigo_equipo": "TRAC-001",
  "nombre_equipo": "Tractor John Deere 5075E",
  "tipo_equipo": "tractor",
  "marca": "John Deere",
  "modelo": "5075E",
  "anno_fabricacion": 2020,
  "serie": "SN123456",
  "estado": "bueno",
  "horas_trabajo": 1250.5,
  "valor_adquisicion": 45000000,
  "fecha_adquisicion": "2020-01-15",
  "proxima_revision": "2024-12-01"
}
```

### Agregar mantenimiento
```bash
POST /api/machinery/{equipo_id}/mantenimientos
Authorization: Bearer <token>
Content-Type: application/json

{
  "tipo_mantenimiento": "preventivo",
  "descripcion": "Cambio de aceite y filtros",
  "costo": 150000,
  "fecha_mantenimiento": "2024-08-12"
}
```

## 🗄️ Modelos de Datos

### User
```python
id_usuario: int (PK)
nombre_usuario: str (unique)
email: str (unique)
password_hash: str
rol: enum (admin, secretary, worker)
fecha_registro: date
estado: str (active, inactive)
is_active: bool
```

### Insumo
```python
id_insumo: int (PK)
nombre: str
tipo: str (fertilizante, pesticida, fungicida, herbicida, semilla, otro)
cantidad: float
unidad: str (kg, lt, u, bolsa, caneca)
precio: float
proveedor: str
lote: str (optional)
total: float (cantidad * precio)
fecha: date
estado: str (active, inactive)
id_usuario: int (FK)
```

### Ganado
```python
id_animal: int (PK)
id_animal_str: str (unique)
nombre_animal: str
tipo_animal: str (bovino, porcino, ovino, caprino, equino, aviar)
raza: str
sexo: str (M, F)
edad: int (meses)
peso: float (kg)
fecha_nacimiento: date
estado_salud: str (excellent, good, regular, sick)
valor_animal: float
fecha_registro: date
estado: str (active, inactive)
id_usuario: int (FK)
```

### Maquinaria
```python
id_equipo: int (PK)
codigo_equipo: str (unique)
nombre_equipo: str
tipo_equipo: str (tractor, cosechadora, arado, sembradora, pulverizador, rastrillo, otro)
marca: str
modelo: str
anno_fabricacion: int
serie: str (optional)
estado: str (excelente, bueno, regular, mantenimiento, inoperativo)
horas_trabajo: float
valor_adquisicion: float
fecha_adquisicion: date
proxima_revision: date
id_usuario: int (FK)
```

## 📋 Estructura de Carpetas

```
backend/
├── main.py                 # Aplicación principal FastAPI
├── database.py             # Configuración de base de datos
├── models.py               # Modelos SQLAlchemy
├── schemas.py              # Esquemas Pydantic
├── crud.py                 # Operaciones CRUD
├── config.py               # Configuración de la app
├── requirements.txt        # Dependencias Python
├── .env.example            # Variables de entorno (ejemplo)
├── routers/
│   ├── __init__.py
│   ├── auth.py             # Rutas de autenticación
│   ├── inputs.py           # Rutas de insumos
│   ├── livestock.py        # Rutas de ganado
│   └── machinery.py        # Rutas de maquinaria
└── README.md               # Este archivo
```

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ JWT para autenticación
- ✅ CORS configurado
- ✅ Validación de entrada con Pydantic
- ✅ SQL Injection prevención (SQLAlchemy ORM)
- ✅ Autorización por usuario

## 🐛 Troubleshooting

### Error de conexión a MySQL
```
Solución: Verificar credenciales en .env y que MySQL esté corriendo
```

### ModuleNotFoundError: No module named 'fastapi'
```
Solución: Instalar dependencias: pip install -r requirements.txt
```

### Port 3000 already in use
```
Solución: Cambiar PORT en .env a otro puerto disponible
```

### CORS Error
```
Solución: Agregar origen en CORS_ORIGINS en config.py o .env
```

## 📦 Dependencias Principales

- **FastAPI 0.104.1** - Framework web moderno
- **SQLAlchemy 2.0.23** - ORM para bases de datos
- **Pydantic 2.5.0** - Validación de datos
- **python-jose 3.3.0** - Implementación JWT
- **passlib 1.7.4** - Hashing de contraseñas
- **PyMySQL 1.1.0** - Conector MySQL
- **python-dotenv 1.0.0** - Manejo de variables de entorno

## 🚀 Deployment

### Usando Gunicorn (Producción)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:3000 main:app
```

### Usando Docker
```bash
docker build -t agrocontrol-backend .
docker run -p 3000:3000 agrocontrol-backend
```

## 📞 Soporte

Para problemas o sugerencias, contactar al equipo de desarrollo.

## 📄 Licencia

Proyecto AgroControl Pro - 2024

---

**Desarrollado con ❤️ para Mas Finca Produccion SAS**

Ver también: [Frontend Documentation](../frontend/README.md)
