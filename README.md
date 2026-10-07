# Clinica Veterinaria Dr Leo - Grupo 8

Sistema academico desarrollado en Python para la gestion de una clinica veterinaria.  
Permite registrar propietarios mascotas citas consultas pagos historial clinico recordatorios y reportes.

## Funciones principales

- Registro y edicion de propietarios
- Proteccion de DNI y celular
- Registro de mascotas con sexo y esterilizado
- Gestion de citas veterinarias
- Registro de consultas con diagnostico tratamiento y vacuna
- Registro de pagos con concepto monto metodo y estado
- Historial clinico por mascota
- Recordatorios de citas
- Reportes diarios
- Exportacion CSV
- Persistencia en JSON y SQLite

## Estructura del proyecto

- main.py: punto de entrada de la aplicacion
- gui/app.py: interfaz grafica en Tkinter
- models/entidades.py: entidades principales del sistema
- services/clinica_service.py: reglas de negocio persistencia y exportacion
- 	ests/test_clinica_service.py: pruebas automatizadas
- ssets/fondo.png: fondo visual de la aplicacion

## Ejecucion

En Visual Studio Code o PowerShell ejecutar:

`ash
python main.py
Flujo recomendado de uso
1. Registrar propietarios
2. Registrar mascotas
3. Gestionar citas
4. Registrar consultas
5. Registrar pagos
6. Revisar historial clinico
7. Generar recordatorios
8. Generar reportes
Tecnologias utilizadas
- Python
- Tkinter
- SQLite
- JSON
- CSV
- Pytest
- Git y GitHub
Buenas practicas aplicadas
- Separacion por carpetas
- Uso de clases
- Manejo de errores
- Pruebas automatizadas
- Proteccion de datos personales
- Commits descriptivos en español
Autor
Grupo 8
Proyecto academico del curso Lenguajes de Programacion
