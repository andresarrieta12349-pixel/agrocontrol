# 🌾 AgroControl Pro - Frontend

## Descripción General

Frontend profesional y moderno para **AgroControl Pro**, sistema integral de gestión agrícola. Desarrollado con HTML5, CSS3 y JavaScript vanilla, sin dependencias externas.

## 📁 Estructura del Proyecto

```
agrocontrol/
├── index.html                          # Pantalla de inicio de sesión
├── frontend/
│   ├── pages/
│   │   ├── dashboard.html             # Panel principal
│   │   ├── inputs.html                # Gestión de insumos
│   │   ├── livestock.html             # Gestión de ganado
│   │   └── machinery.html             # Gestión de maquinaria
│   │
│   ├── css/
│   │   ├── main.css                   # Estilos globales y variables CSS
│   │   ├── login.css                  # Estilos de pantalla de login
│   │   ├── dashboard.css              # Estilos del dashboard y sidebar
│   │   └── modules.css                # Estilos de módulos (tablas, formularios)
│   │
│   ├── js/
│   │   ├── auth.js                    # Gestión de autenticación
│   │   ├── sidebar.js                 # Control del sidebar navegable
│   │   ├── dashboard.js               # Lógica del dashboard
│   │   ├── inputs.js                  # CRUD de insumos
│   │   ├── livestock.js               # CRUD de ganado
│   │   └── machinery.js               # CRUD de maquinaria
│   │
│   └── utils/
│       ├── api.js                     # Cliente HTTP para API
│       ├── validation.js              # Validadores de datos
│       └── utilities.js               # Funciones de utilidad general
└── README.md                           # Este archivo
```

## 🎨 Paleta de Colores

### Colores Institucionales
- **Verde Oscuro (Primario)**: `#1b5e20`
- **Verde Claro (Secundario)**: `#2e7d32`
- **Naranja (Acentos)**: `#f57c00`
- **Azul (Información)**: `#0288d1`

### Colores de Estado
- **Éxito**: `#2e7d32` (Verde)
- **Error**: `#c62828` (Rojo)
- **Advertencia**: `#f57c00` (Naranja)
- **Información**: `#0288d1` (Azul)

## 📱 Diseño Responsivo

El sistema está optimizado para **escritorios (1280px+)** pero mantiene compatibilidad con pantallas más pequeñas.

### Breakpoints
- **Desktop**: 1024px+
- **Tablet**: 768px - 1023px
- **Mobile**: < 768px

## 🔐 Autenticación

### Flujo de Login
1. Usuario ingresa credenciales en `index.html`
2. `auth.js` valida y envía al backend
3. Backend devuelve token JWT
4. Token se almacena en localStorage o sessionStorage
5. Usuario redirigido a dashboard

### Almacenamiento de Token
```javascript
// Con "Recuérdame" activado
localStorage.setItem('authToken', token);

// Sin "Recuérdame"
sessionStorage.setItem('authToken', token);
```

## 📊 Módulos Principales

### 1. Dashboard (`dashboard.html`)
- **Propósito**: Visualizar estadísticas principales
- **Características**:
  - Cards con conteos en tiempo real
  - Acciones rápidas
  - Actividad reciente
  - Navegación a módulos

### 2. Insumos (`inputs.html`)
- **Propósito**: Gestionar insumos agrícolas
- **CRUD Completo**:
  - ✅ Crear nuevos insumos
  - ✅ Ver tabla de insumos
  - ✅ Buscar/Filtrar
  - ✅ Editar (placeholder)
  - ✅ Eliminar con confirmación

**Campos**:
- Nombre del insumo
- Tipo (fertilizante, pesticida, fungicida, etc.)
- Cantidad
- Unidad de medida
- Precio unitario
- Fecha de ingreso
- Proveedor
- Número de lote

### 3. Ganado (`livestock.html`)
- **Propósito**: Gestionar inventario de animales
- **CRUD Completo**:
  - ✅ Registrar nuevos animales
  - ✅ Visualizar en tabla
  - ✅ Buscar por ID, nombre, raza
  - ✅ Eliminar con confirmación

**Campos**:
- ID del animal
- Nombre
- Tipo (bovino, porcino, ovino, etc.)
- Raza
- Sexo
- Edad (meses)
- Peso (kg)
- Fecha de nacimiento
- Estado de salud
- Valor del animal

### 4. Maquinaria (`machinery.html`)
- **Propósito**: Administrar equipos agrícolas
- **CRUD Completo**:
  - ✅ Registrar equipos
  - ✅ Visualizar tabla de maquinaria
  - ✅ Buscar por código, marca, modelo
  - ✅ Eliminar con confirmación

**Campos**:
- Código del equipo
- Nombre
- Tipo (tractor, cosechadora, etc.)
- Marca
- Modelo
- Año de fabricación
- Número de serie
- Estado (excelente, bueno, regular, etc.)
- Horas de trabajo
- Valor de adquisición
- Fecha de adquisición
- Próxima revisión

## 🛠️ Características Técnicas

### JavaScript Vanilla (Sin Frameworks)
- ✅ Clases ES6+
- ✅ Async/Await
- ✅ DOM API moderna
- ✅ Fetch API
- ✅ localStorage y sessionStorage

### Validación de Datos
```javascript
// Validadores personalizados
InsumosValidator.validate(data)
LivestockValidator.validate(data)
MachineryValidator.validate(data)
```

### Cliente API Centralizado
```javascript
// Uso del cliente API
const response = await apiClient.get('/endpoint');
const data = await InsumosAPI.create(formData);
```

### Seguridad
- ✅ Escape de HTML para prevenir XSS
- ✅ Validación de entrada en cliente
- ✅ Token JWT en headers
- ✅ Confirmación antes de eliminar

## 🎯 Funcionalidades Implementadas

### Globales
- [x] Login con validación
- [x] Navegación lateral (Sidebar)
- [x] Cerrar sesión
- [x] Información de usuario
- [x] Protección de rutas

### Insumos
- [x] Crear insumo
- [x] Listar insumos
- [x] Buscar/Filtrar
- [x] Eliminar insumo
- [x] Validación de datos
- [x] Cálculo de totales

### Ganado
- [x] Registrar animal
- [x] Listar animales
- [x] Buscar por criterios
- [x] Eliminar animal
- [x] Validación de edad y fechas
- [x] Badges de estado

### Maquinaria
- [x] Registrar equipo
- [x] Listar maquinaria
- [x] Búsqueda avanzada
- [x] Eliminar equipo
- [x] Estado de revisión
- [x] Cálculo de depreciación

## 📋 Guía de Uso

### Instalación
1. Clonar/descargar el proyecto
2. No requiere instalación de dependencias
3. Usar un servidor web local (ej: Live Server en VS Code)

### Iniciar Sesión
1. Abrir `index.html` en el navegador
2. Ingresar email y contraseña
3. Opcionalmente marcar "Recuérdame"
4. Acceder al dashboard

### Gestionar Insumos
1. Ir a módulo "Insumos"
2. Completar formulario
3. Hacer clic en "Guardar Insumo"
4. Ver tabla actualizada automáticamente
5. Usar búsqueda para filtrar

### Gestionar Ganado
1. Ir a módulo "Ganado"
2. Llenar datos del animal
3. Validar formato de fechas
4. Guardar registro
5. Consultar tabla dinámica

### Gestionar Maquinaria
1. Ir a módulo "Maquinaria"
2. Ingresa datos del equipo
3. Especificar próxima revisión
4. Guardar maquinaria
5. Monitorear estado

## 🔌 Integración con API

### Configuración
```javascript
const apiClient = new APIClient('http://localhost:3000/api');
```

### Endpoints Esperados
```
POST   /api/auth/login
POST   /api/auth/logout

GET    /api/insumos
POST   /api/insumos
DELETE /api/insumos/:id

GET    /api/livestock
POST   /api/livestock
DELETE /api/livestock/:id

GET    /api/machinery
POST   /api/machinery
DELETE /api/machinery/:id
```

## 📦 Variables CSS Disponibles

```css
:root {
    --color-primary: #1b5e20;
    --color-secondary: #f57c00;
    --color-accent: #0288d1;
    --spacing-md: 1rem;
    --font-size-base: 1rem;
    --border-radius-md: 0.5rem;
    --transition-normal: 300ms ease-in-out;
}
```

## 🧪 Datos de Demostración

Si la API no está disponible, el sistema carga automáticamente datos de demostración:

```javascript
// Ejemplo de dato demo (Insumo)
{
    id: 1,
    nombre: 'Fertilizante NPK 15-15-15',
    tipo: 'fertilizante',
    cantidad: 500,
    unidad: 'kg',
    precio: 45.50,
    fecha: '2024-08-12',
    proveedor: 'Agrícola Express'
}
```

## 🐛 Troubleshooting

### El formulario no envía datos
1. Verificar que la API esté ejecutándose
2. Revisar consola del navegador (F12)
3. Validar que todos los campos obligatorios estén completos

### La tabla aparece vacía
- Si no hay conexión a API: Se cargan datos demo
- Verificar que la búsqueda no tenga filtro activo

### El sidebar no funciona
- Limpiar caché del navegador
- Verificar que sidebar.js esté cargado

### Problemas de estilos
- Forzar recarga: Ctrl+F5 (Windows) o Cmd+Shift+R (Mac)
- Verificar que los archivos CSS estén en las rutas correctas

## 📝 Notas de Desarrollo

### Convenciones de Código
- Usar camelCase para variables y funciones
- Usar kebab-case para clases CSS
- Comentar código complejo
- Usar validadores antes de enviar datos

### Añadir Nuevo Módulo
1. Crear `modulo.html` en `pages/`
2. Crear `modulo.css` en `css/` (si aplica)
3. Crear `modulo.js` en `js/`
4. Agregar navegación en sidebar
5. Implementar clase Manager

### Personalización
- Cambiar colores en `main.css` (:root variables)
- Modificar max-width en `--max-width` (actualmente 1280px)
- Ajustar espaciado en variables CSS

## 🚀 Performance

- **No usar** jQuery o frameworks pesados
- **Optimizar** queries del DOM
- **Debounce** en búsquedas
- **Lazy loading** si se implementan imágenes

## 📄 Licencia

Proyecto educativo - AgroControl Pro 2024

---

**Desarrollado con ❤️ para profesionales agrícolas**

Para soporte o sugerencias, contactar al equipo de desarrollo.
