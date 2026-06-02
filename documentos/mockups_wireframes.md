# Mockups y Wireframes - AgroControl Pro

**Proyecto:** ERP Agropecuario  
**Empresa:** Mas Finca Produccion SAS  
**Semana 3 - Diseno de prototipos**  

---

## Sistema de Diseno

### Colores
- Fondo principal: #080d08 (negro oscuro)
- Verde principal: #22c55e
- Verde oscuro: #16a34a
- Texto: #f0fdf4
- Bordes: #1e3a1e

### Tipografia
- Fuente: Arial / Inter
- Titulos: Bold 24px
- Texto normal: 14px

---

## Vista 1 - Login

```
+------------------------------------------+
|                                          |
|         AgroControl Pro                  |
|       ERP Agropecuario                   |
|                                          |
|   [ correo electronico            ]      |
|   [ contrasena                    ]      |
|                                          |
|   [        INGRESAR               ]      |
|                                          |
+------------------------------------------+
```

**Elementos:**
- Logo y nombre centrado
- Campo de correo
- Campo de contrasena
- Boton de ingreso

---

## Vista 2 - Dashboard

```
+----------+----------------------------------+
| Logo     | Bienvenido, Administrador    [X] |
+----------+----------------------------------+
| Dashboard| [Prod] [Invent] [Ganado] [Emp]   |
| Inventario                                  |
| Ganado   | Actividad Reciente               |
| Nomina   | +---------------------------+    |
| Clima    | | Tipo | Descripcion | Valor|    |
|          | +---------------------------+    |
|          |                                  |
|          | Distribucion Inventario          |
|          | Alimentos     45.2%  44,450      |
|          | Medicamentos  20.1%  19,750      |
+----------+----------------------------------+
```

**Tarjetas de resumen:**
- Produccion Total (toneladas)
- Inventario Total (unidades)
- Ganado Total (cabezas)
- Empleados Activos
- Temperatura actual

---

## Vista 3 - Inventario

```
+----------+----------------------------------+
| Sidebar  | Inventario    [+ Nuevo Item]     |
|          +----------------------------------+
|          | Buscar: [__________] [Filtrar]   |
|          +----------------------------------+
|          | Nombre | Categoria | Cant | Est  |
|          | Herb.  | Medicam.  | 150  | Act  |
|          | Gasol. | Combustib.| 500L | Act  |
|          | Alim.  | Alimentos | 2000 | Act  |
|          +----------------------------------+
|          | [Editar] [Eliminar]              |
+----------+----------------------------------+
```

---

## Vista 4 - Ganado

```
+----------+----------------------------------+
| Sidebar  | Ganado        [+ Registrar]      |
|          +----------------------------------+
|          | Total: 2847 | Peso prom: 450kg   |
|          +----------------------------------+
|          | ID      | Raza  | Peso | Estado  |
|          | Toro4587| Brahm.| 520kg| Activo  |
|          | Vaca321 | Hols. | 380kg| Activo  |
|          +----------------------------------+
|          | [Ver detalle] [Editar]           |
+----------+----------------------------------+
```

---

## Vista 5 - Nomina

```
+----------+----------------------------------+
| Sidebar  | Nomina        [+ Empleado]       |
|          +----------------------------------+
|          | Periodo: Julio 2026              |
|          +----------------------------------+
|          | Empleado  | Cargo    | Salario   |
|          | Juan P.   | Operario | $1,500k   |
|          | Maria L.  | Secretar.| $2,000k   |
|          +----------------------------------+
|          | Total nomina: $8,750,000         |
+----------+----------------------------------+
```

---

## Vista 6 - Clima

```
+----------+----------------------------------+
| Sidebar  | Clima         [+ Registrar]      |
|          +----------------------------------+
|          | HOY: 24 C  Soleado  Humedad:65%  |
|          +----------------------------------+
|          | Fecha  | Temp | Humedad | Lluvia |
|          | Hoy    | 24C  |  65%    |  0mm   |
|          | Ayer   | 22C  |  80%    | 15mm   |
|          +----------------------------------+
+----------+----------------------------------+
```

---

## Formularios de Entrada de Datos

### Formulario - Inventario
- Nombre del item (texto obligatorio)
- Categoria (select)
- Unidad de medida (select)
- Cantidad (numero)
- Costo unitario (numero)
- Ubicacion (texto)
- Estado (select)

### Formulario - Ganado
- Identificacion (texto obligatorio)
- Tipo (select)
- Raza (texto)
- Sexo (select)
- Fecha de nacimiento (fecha)
- Peso en kg (numero)
- Estado (select)

### Formulario - Nomina
- Nombre completo (texto obligatorio)
- Cargo (select)
- Fecha de ingreso (fecha)
- Salario base (numero)
- Estado (select)

### Formulario - Clima
- Fecha (fecha)
- Temperatura en C (numero)
- Humedad % (numero)
- Precipitacion mm (numero)
- Viento km/h (numero)
- Condicion general (select)
- Ubicacion (texto)
