# Modelado de Datos - AgroControl Pro

**Proyecto:** ERP Agropecuario  
**Empresa:** Mas Finca Produccion SAS  
**Semana 4 - Diagrama Entidad-Relacion (MER)**  
**Motor de base de datos:** MySQL  

---

## Relaciones entre tablas

```
T_NOMINA (1) ----------- (N) T_USUARIOS
T_USUARIOS (1) ----------- (N) T_OPERACIONES
T_INVENTARIO (1) ----------- (N) T_OPERACIONES
T_OPERACIONES (1) ----------- (N) T_GANADO
```

---

## Tablas

### T_NOMINA

| Campo | Tipo | Clave |
|-------|------|-------|
| id_nomina | int | PK |
| nombre_empleado | varchar(150) | |
| cargo | varchar(100) | |
| salario_base | decimal(12,2) | |
| fecha_ingreso | date | |
| estado | varchar(20) | |

---

### T_USUARIOS

| Campo | Tipo | Clave |
|-------|------|-------|
| id_usuario | int | PK |
| nombre_usuario | varchar(100) | |
| email | varchar(150) | UNIQUE |
| contrasena | varchar(255) | |
| rol | varchar(50) | |
| id_nomina | int | FK |
| fecha_registro | date | |
| estado | varchar(20) | |

---

### T_INVENTARIO

| Campo | Tipo | Clave |
|-------|------|-------|
| id_inventario | int | PK |
| nombre_item | varchar(150) | |
| categoria | varchar(100) | |
| unidad_medida | varchar(50) | |
| cantidad | decimal(12,2) | |
| costo_unitario | decimal(12,2) | |
| ubicacion | varchar(150) | |
| fecha_registro | date | |
| estado | varchar(20) | |

---

### T_OPERACIONES

| Campo | Tipo | Clave |
|-------|------|-------|
| id_operacion | int | PK |
| fecha_operacion | date | |
| tipo_operacion | varchar(100) | |
| descripcion | varchar(255) | |
| id_inventario | int | FK |
| id_usuario | int | FK |
| costo_total | decimal(12,2) | |
| estado | varchar(20) | |

---

### T_GANADO

| Campo | Tipo | Clave |
|-------|------|-------|
| id_ganado | int | PK |
| identificacion | varchar(50) | UNIQUE |
| tipo | varchar(100) | |
| raza | varchar(100) | |
| fecha_nacimiento | date | |
| sexo | varchar(10) | |
| peso | decimal(10,2) | |
| id_operacion | int | FK |
| estado | varchar(20) | |

---

### T_CLIMA

| Campo | Tipo | Clave |
|-------|------|-------|
| id_clima | int | PK |
| fecha | date | |
| temperatura | decimal(5,2) | |
| humedad | decimal(5,2) | |
| precipitacion | decimal(6,2) | |
| viento | decimal(5,2) | |
| descripcion | varchar(255) | |
| ubicacion | varchar(150) | |

---

## Script SQL

```sql
CREATE DATABASE IF NOT EXISTS agrocontrol_pro;
USE agrocontrol_pro;

CREATE TABLE T_NOMINA (
  id_nomina       INT PRIMARY KEY AUTO_INCREMENT,
  nombre_empleado VARCHAR(150),
  cargo           VARCHAR(100),
  salario_base    DECIMAL(12,2),
  fecha_ingreso   DATE,
  estado          VARCHAR(20) DEFAULT 'Activo'
);

CREATE TABLE T_USUARIOS (
  id_usuario     INT PRIMARY KEY AUTO_INCREMENT,
  nombre_usuario VARCHAR(100),
  email          VARCHAR(150) UNIQUE,
  contrasena     VARCHAR(255),
  rol            VARCHAR(50),
  id_nomina      INT,
  fecha_registro DATE,
  estado         VARCHAR(20) DEFAULT 'Activo',
  FOREIGN KEY (id_nomina) REFERENCES T_NOMINA(id_nomina)
);

CREATE TABLE T_INVENTARIO (
  id_inventario  INT PRIMARY KEY AUTO_INCREMENT,
  nombre_item    VARCHAR(150),
  categoria      VARCHAR(100),
  unidad_medida  VARCHAR(50),
  cantidad       DECIMAL(12,2),
  costo_unitario DECIMAL(12,2),
  ubicacion      VARCHAR(150),
  fecha_registro DATE,
  estado         VARCHAR(20) DEFAULT 'Activo'
);

CREATE TABLE T_OPERACIONES (
  id_operacion    INT PRIMARY KEY AUTO_INCREMENT,
  fecha_operacion DATE,
  tipo_operacion  VARCHAR(100),
  descripcion     VARCHAR(255),
  id_inventario   INT,
  id_usuario      INT,
  costo_total     DECIMAL(12,2),
  estado          VARCHAR(20) DEFAULT 'Completado',
  FOREIGN KEY (id_inventario) REFERENCES T_INVENTARIO(id_inventario),
  FOREIGN KEY (id_usuario)    REFERENCES T_USUARIOS(id_usuario)
);

CREATE TABLE T_GANADO (
  id_ganado        INT PRIMARY KEY AUTO_INCREMENT,
  identificacion   VARCHAR(50) UNIQUE,
  tipo             VARCHAR(100),
  raza             VARCHAR(100),
  fecha_nacimiento DATE,
  sexo             VARCHAR(10),
  peso             DECIMAL(10,2),
  id_operacion     INT,
  estado           VARCHAR(20) DEFAULT 'Activo',
  FOREIGN KEY (id_operacion) REFERENCES T_OPERACIONES(id_operacion)
);

CREATE TABLE T_CLIMA (
  id_clima      INT PRIMARY KEY AUTO_INCREMENT,
  fecha         DATE,
  temperatura   DECIMAL(5,2),
  humedad       DECIMAL(5,2),
  precipitacion DECIMAL(6,2),
  viento        DECIMAL(5,2),
  descripcion   VARCHAR(255),
  ubicacion     VARCHAR(150)
);
```
