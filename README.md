# Clinica Veterinaria Dr Leo - Grupo 8

Sistema academico desarrollado en Python para la gestion de una clinica veterinaria.  
El proyecto permite registrar propietarios, mascotas, citas, consultas, pagos, historial clinico, recordatorios y reportes.

## Funciones principales

- Registro y edicion de propietarios.
- Proteccion de DNI y numero de celular.
- Registro de mascotas con sexo y estado de esterilizacion.
- Gestion de citas veterinarias.
- Registro de consultas con diagnostico, tratamiento y vacuna.
- Registro de pagos con concepto, monto, metodo y estado.
- Generacion de historial clinico por mascota.
- Generacion de recordatorios de citas.
- Generacion de reportes diarios.
- Exportacion de datos en CSV.
- Persistencia de datos en JSON y SQLite.

## Estructura del proyecto

| Archivo o carpeta | Descripcion |
| --- | --- |
| `main.py` | Punto de entrada de la aplicacion |
| `gui/app.py` | Interfaz grafica desarrollada con Tkinter |
| `models/entidades.py` | Entidades principales del sistema |
| `services/clinica_service.py` | Reglas de negocio, persistencia y exportacion |
| `tests/test_clinica_service.py` | Pruebas automatizadas |
| `assets/fondo.png` | Recurso visual usado como fondo |

## Ejecucion

Desde Visual Studio Code o PowerShell ejecutar:

```bash
python main.py
```

## Flujo recomendado de uso

1. Registrar propietarios.
2. Registrar mascotas.
3. Gestionar citas.
4. Registrar consultas.
5. Registrar pagos.
6. Revisar historial clinico.
7. Generar recordatorios.
8. Generar reportes.

## Tecnologias utilizadas

- Python
- Tkinter
- SQLite
- JSON
- CSV
- Pytest
- Git y GitHub

## Buenas practicas aplicadas

- Separacion del proyecto por carpetas.
- Uso de clases para representar entidades.
- Manejo de errores y validaciones.
- Pruebas automatizadas.
- Proteccion de datos personales.
- Commits descriptivos en español.
- Interfaz grafica ordenada por flujo de trabajo.

## Proyecto academico

Proyecto desarrollado por el Grupo 8 para el curso Lenguajes de Programacion.
