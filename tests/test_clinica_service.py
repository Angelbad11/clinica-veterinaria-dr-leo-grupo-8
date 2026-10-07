import csv
from pathlib import Path

from services.clinica_service import ClinicaService


def test_propietario_muestra_dni_protegido(tmp_path):
    servicio = ClinicaService(tmp_path / "datos_clinica.json")

    propietario = servicio.registrar_propietario(
        "Ana Torres",
        "12345678",
        "999888777",
    )

    assert propietario.dni == "12345678"
    assert propietario.obtener_dni_protegido() == "******78"
    assert "12345678" not in str(propietario)
    assert "******78" in str(propietario)


def test_no_permite_dni_repetido(tmp_path):
    servicio = ClinicaService(tmp_path / "datos_clinica.json")
    servicio.registrar_propietario("Ana Torres", "12345678", "999888777")

    try:
        servicio.registrar_propietario("Luis Ramos", "12345678", "988777666")
        assert False
    except ValueError as error:
        assert "Ya existe" in str(error)


def test_persistencia_con_dni(tmp_path):
    ruta = tmp_path / "datos_clinica.json"

    servicio = ClinicaService(ruta)
    propietario = servicio.registrar_propietario("Ana Torres", "12345678", "999888777")
    servicio.registrar_mascota("Luna", "Perro", "3", propietario, "Hembra", "Sí")

    servicio_recargado = ClinicaService(ruta)

    assert len(servicio_recargado.listar_propietarios()) == 1
    assert servicio_recargado.listar_propietarios()[0].dni == "12345678"
    assert servicio_recargado.listar_mascotas()[0].propietario.dni == "12345678"
    assert servicio_recargado.listar_mascotas()[0].sexo == "Hembra"
    assert servicio_recargado.listar_mascotas()[0].esterilizado == "Sí"


def test_editar_propietario_mantiene_relacion_con_mascota(tmp_path):
    servicio = ClinicaService(tmp_path / "datos_clinica.json")
    propietario = servicio.registrar_propietario("Ana Torres", "12345678", "999888777")
    mascota = servicio.registrar_mascota("Luna", "Perro", "3", propietario)

    servicio.actualizar_propietario(0, "Ana María Torres", "87654321", "999000111")

    assert servicio.listar_propietarios()[0].nombre == "Ana María Torres"
    assert servicio.listar_propietarios()[0].obtener_dni_protegido() == "******21"
    assert mascota.propietario.nombre == "Ana María Torres"
    assert mascota.propietario.dni == "87654321"


def test_editar_propietario_no_permite_dni_de_otro(tmp_path):
    servicio = ClinicaService(tmp_path / "datos_clinica.json")
    servicio.registrar_propietario("Ana Torres", "12345678", "999888777")
    servicio.registrar_propietario("Luis Ramos", "87654321", "988777666")

    try:
        servicio.actualizar_propietario(1, "Luis Ramos", "12345678", "988777666")
        assert False
    except ValueError as error:
        assert "otro propietario" in str(error)


def test_compatibilidad_con_propietarios_sin_dni(tmp_path):
    ruta = tmp_path / "datos_clinica.json"
    ruta.write_text(
        """
        {
            "propietarios": [
                {"nombre": "Propietario antiguo", "telefono": "999111222"}
            ],
            "mascotas": [],
            "citas": [],
            "pagos": [],
            "atenciones": []
        }
        """,
        encoding="utf-8",
    )

    servicio = ClinicaService(ruta)
    propietario = servicio.listar_propietarios()[0]

    assert propietario.dni == ""
    assert propietario.obtener_dni_protegido() == "No registrado"


def test_filtros_csv_y_sqlite(tmp_path):
    ruta = tmp_path / "datos_clinica.json"
    servicio = ClinicaService(ruta)
    propietario = servicio.registrar_propietario("Ana Torres", "12345678", "999888777")
    mascota = servicio.registrar_mascota("Luna", "Perro", "3", propietario)
    servicio.registrar_atencion(mascota, "06/10/2026", "Gripe", "Jarabe", "Rabia")
    servicio.registrar_pago("Consulta", 50, "Yape", "Confirmado")

    assert len(servicio.filtrar_atenciones(vacuna="rabia")) == 1
    assert servicio.calcular_total_confirmado() == 50
    carpeta_csv, archivos = servicio.exportar_datos_csv()
    assert len(archivos) == 5
    with open(Path(carpeta_csv) / "mascotas.csv", newline="", encoding="utf-8-sig") as archivo:
        cabeceras = next(csv.reader(archivo))
    assert "sexo" in cabeceras
    assert "esterilizado" in cabeceras
    assert (tmp_path / "clinica.db").exists()


def test_historial_incluye_sexo_y_esterilizado(tmp_path):
    servicio = ClinicaService(tmp_path / "datos_clinica.json")
    propietario = servicio.registrar_propietario("Ana Torres", "12345678", "999888777")
    servicio.registrar_mascota("Luna", "Perro", "3", propietario, "Hembra", "Sí")

    historial = servicio.generar_historial_mascota(0)

    assert "Sexo: Hembra" in historial
    assert "Esterilizado: Sí" in historial


def test_repara_ids_duplicados_en_pagos_antiguos(tmp_path):
    ruta = tmp_path / "datos_clinica.json"
    ruta.write_text(
        """
        {
            "propietarios": [],
            "mascotas": [],
            "citas": [],
            "pagos": [
                {"concepto": "Consulta", "monto": 50, "metodo": "Yape", "estado": "Confirmado", "id_ponkis": "G-0001"},
                {"concepto": "Vacuna", "monto": 30, "metodo": "Efectivo", "estado": "Confirmado", "id_ponkis": "G-0001"}
            ],
            "atenciones": []
        }
        """,
        encoding="utf-8",
    )

    servicio = ClinicaService(ruta)
    ids = [pago.id_ponkis for pago in servicio.listar_pagos()]

    assert ids == ["G-0001", "G-0002"]
