CLINICA VETERINARIA DR. LEO - VERSION FUNCIONAL

Estructura:
- main.py: punto de entrada de la aplicacion.
- gui/app.py: interfaz Tkinter.
- models/entidades.py: entidades del sistema.
- services/clinica_service.py: reglas, persistencia JSON/SQLite y CSV.
- tests/test_clinica_service.py: pruebas automatizadas.
- assets/fondo.png: fondo de la aplicacion.

Ejecucion en VS Code o PowerShell:
    python main.py

La aplicacion conserva datos anteriores en data/datos_clinica.json cuando se
copian estos archivos dentro del proyecto existente. Tambien crea data/clinica.db
como respaldo SQLite y data/exportacion_csv/ al exportar los registros.

Mascotas permite registrar y editar sexo y si esta esterilizada.

Orden recomendado de uso:
1. Propietarios.
2. Mascotas.
3. Citas.
4. Consultas.
5. Pagos.
6. Historial.
7. Recordatorios.
8. Reportes.

No se debe incluir la carpeta data con datos personales reales en GitHub.
