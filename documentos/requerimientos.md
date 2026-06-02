# Requerimientos - AgroControl Pro

**Proyecto:** ERP Agropecuario  
**Empresa:** Mas Finca Produccion SAS  
**Formacion:** Programacion de Software - SENA  
**Instructor:** Edgardo Paul Almanza  

---

## Semana 1: Requerimientos Funcionales

### Descripcion del sistema
AgroControl Pro es un sistema de gestion integral para digitalizar la administracion de Mas Finca Produccion SAS. Permite controlar inventarios, ganado, nomina, operaciones y condiciones climaticas desde una sola plataforma.

### Modulos del sistema
- Control de inventario (venenos, gasolina, pesticidas, alimentos)
- Gestion y pesaje de ganado
- Nomina de empleados
- Control de consumo de combustible
- Registro de condiciones climaticas (lluvias)
- Seguridad y acceso de usuarios

---

### RF-01: Gestion de Usuarios y Seguridad
El sistema debe permitir el registro e inicio de sesion de usuarios con roles definidos.

- El sistema debe permitir login con correo y contrasena.
- El sistema debe manejar dos roles: Administrador y Secretario.
- El sistema debe proteger las paginas segun el rol del usuario.

---

### RF-02: Control de Inventario
El sistema debe permitir registrar, consultar, actualizar y eliminar items del inventario.

- El sistema debe clasificar los items por categoria: Alimentos, Medicamentos, Herramientas, Fertilizantes, Combustible, Otros.
- El sistema debe mostrar la cantidad disponible en stock.
- El sistema debe registrar entradas y salidas de inventario.

---

### RF-03: Control de Ganado y Pesaje
El sistema debe permitir registrar cada animal con su identificacion, raza, peso y estado.

- El sistema debe registrar el peso de cada animal.
- El sistema debe mostrar el historial de pesajes por animal.
- El sistema debe identificar cada animal con un codigo unico.

---

### RF-04: Gestion de Nomina
El sistema debe permitir registrar los empleados con su cargo y salario base.

- El sistema debe calcular el pago mensual.
- El sistema debe mostrar el listado de empleados activos.
- El sistema debe registrar la fecha de ingreso de cada empleado.

---

### RF-05: Control de Combustible
El sistema debe registrar el consumo de gasolina de la finca.

- El sistema debe registrar la cantidad de combustible consumido.
- El sistema debe calcular el costo total del consumo.
- El sistema debe mostrar el consumo por semana.

---

### RF-06: Registro de Condiciones Climaticas
El sistema debe permitir registrar temperatura, humedad, precipitacion y viento diariamente.

- El sistema debe guardar el registro climatico por fecha.
- El sistema debe mostrar el historial climatico de la finca.

---

## Requerimientos No Funcionales

| ID | Requerimiento | Descripcion |
|----|--------------|-------------|
| RNF-01 | Rendimiento | Las paginas deben cargar rapido. |
| RNF-02 | Seguridad | Las contrasenas deben almacenarse cifradas. |
| RNF-03 | Usabilidad | La interfaz debe ser facil de usar. |
| RNF-04 | Compatibilidad | Debe funcionar en Chrome, Firefox y Edge. |

---

## Equipo de Desarrollo

| Integrante | Rol | Responsabilidades |
|-----------|-----|------------------|
| Integrante 1 | Frontend y Diseno | HTML, CSS, JS, interfaces |
| Integrante 2 | Backend y Datos | Node.js, MySQL, seguridad |
