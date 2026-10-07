import base64
import csv
import hashlib
import json
import os
import sqlite3
from functools import reduce

from models.entidades import Atencion, Cita, Mascota, Pago, Propietario


class CifradorDatos:
    """Protege datos personales sin agregar dependencias externas."""

    CLAVE = hashlib.sha256(b"DrLeo-Grupo8-Datos-2026").digest()

    @classmethod
    def cifrar(cls, valor):
        texto = str(valor or "")
        if texto == "":
            return ""
        datos = texto.encode("utf-8")
        protegidos = bytes(
            dato ^ cls.CLAVE[indice % len(cls.CLAVE)]
            for indice, dato in enumerate(datos)
        )
        return "enc:" + base64.urlsafe_b64encode(protegidos).decode("ascii")

    @classmethod
    def descifrar(cls, valor):
        texto = str(valor or "")
        if not texto.startswith("enc:"):
            return texto
        try:
            protegidos = base64.urlsafe_b64decode(texto[4:].encode("ascii"))
            datos = bytes(
                dato ^ cls.CLAVE[indice % len(cls.CLAVE)]
                for indice, dato in enumerate(protegidos)
            )
            return datos.decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            return ""


class ClinicaService:
    def __init__(self, ruta_datos=None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.ruta_datos = ruta_datos or os.path.join(
            base_dir,
            "data",
            "datos_clinica.json",
        )
        self.ruta_bd = os.path.join(
            os.path.dirname(self.ruta_datos),
            "clinica.db",
        )
        self.propietarios = []
        self.mascotas = []
        self.citas = []
        self.pagos = []
        self.atenciones = []
        self.cargar_datos()

    def _coleccion_por_prefijo(self, prefijo):
        return {
            "P": self.propietarios,
            "M": self.mascotas,
            "C": self.citas,
            "G": self.pagos,
            "A": self.atenciones,
        }.get(prefijo, [])

    def _nuevo_id(self, prefijo):
        existentes = {
            getattr(item, "id_ponkis", "")
            for item in self._coleccion_por_prefijo(prefijo)
        }
        numero = len(existentes) + 1
        identificador = f"{prefijo}-{numero:04d}"
        while identificador in existentes:
            numero += 1
            identificador = f"{prefijo}-{numero:04d}"
        return identificador

    @staticmethod
    def _texto(valor):
        return str(valor or "").strip()

    @staticmethod
    def _normalizar_fecha(fecha):
        fecha = str(fecha or "").strip()
        for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                from datetime import datetime

                return datetime.strptime(fecha, formato)
            except ValueError:
                continue
        return None

    def registrar_propietario(self, nombre, dni, telefono):
        nombre = self._texto(nombre)
        dni = self._texto(dni)
        telefono = self._texto(telefono)
        self.validar_propietario(nombre, dni, telefono)
        if any(propietario.dni == dni for propietario in self.propietarios):
            raise ValueError("Ya existe un propietario registrado con ese DNI.")

        propietario = Propietario(nombre, dni, telefono, self._nuevo_id("P"))
        self.propietarios.append(propietario)
        self.guardar_datos()
        return propietario

    def listar_propietarios(self):
        return self.propietarios

    def buscar_propietarios(self, termino=""):
        termino = self._texto(termino).lower()
        return list(
            filter(
                lambda propietario: termino in propietario.nombre.lower()
                or termino in propietario.dni
                or termino in propietario.telefono,
                self.propietarios,
            )
        )

    def actualizar_propietario(self, indice_propietario, nombre, dni, telefono):
        nombre = self._texto(nombre)
        dni = self._texto(dni)
        telefono = self._texto(telefono)
        if indice_propietario < 0 or indice_propietario >= len(self.propietarios):
            raise ValueError("Selecciona un propietario válido para editar.")
        self.validar_propietario(nombre, dni, telefono)
        for indice, propietario in enumerate(self.propietarios):
            if indice != indice_propietario and propietario.dni == dni:
                raise ValueError("Ya existe otro propietario registrado con ese DNI.")
        propietario = self.propietarios[indice_propietario]
        propietario.actualizar(nombre, dni, telefono)
        self.guardar_datos()
        return propietario

    def eliminar_propietario(self, indice_propietario):
        if indice_propietario < 0 or indice_propietario >= len(self.propietarios):
            raise ValueError("Selecciona un propietario válido.")
        propietario = self.propietarios[indice_propietario]
        if any(mascota.propietario is propietario for mascota in self.mascotas):
            raise ValueError(
                "No se puede eliminar: el propietario todavía tiene mascotas vinculadas."
            )
        self.propietarios.pop(indice_propietario)
        self.guardar_datos()

    def validar_propietario(self, nombre, dni, telefono):
        if nombre == "" or dni == "" or telefono == "":
            raise ValueError("Completa nombre, DNI y teléfono.")
        if not dni.isdigit() or len(dni) != 8:
            raise ValueError("El DNI debe tener 8 números.")

    @staticmethod
    def _normalizar_opcion(valor, opciones, campo):
        texto = str(valor or "").strip()
        if texto == "":
            return "No especificado"
        for opcion in opciones:
            if texto.casefold() == opcion.casefold():
                return opcion
        raise ValueError(f"{campo} no válido.")

    def _validar_datos_mascota(self, nombre, especie, edad, sexo, esterilizado):
        if nombre == "" or especie == "" or edad == "":
            raise ValueError("Completa nombre, especie y edad.")
        sexo = self._normalizar_opcion(
            sexo,
            ("No especificado", "Macho", "Hembra"),
            "Sexo",
        )
        esterilizado = self._normalizar_opcion(
            esterilizado,
            ("No especificado", "Sí", "No"),
            "Esterilizado",
        )
        return sexo, esterilizado

    def registrar_mascota(
        self,
        nombre,
        especie,
        edad,
        propietario,
        sexo="No especificado",
        esterilizado="No especificado",
    ):
        nombre = self._texto(nombre)
        especie = self._texto(especie)
        edad = self._texto(edad)
        sexo, esterilizado = self._validar_datos_mascota(
            nombre,
            especie,
            edad,
            sexo,
            esterilizado,
        )
        if any(
            mascota.nombre.lower() == nombre.lower()
            and mascota.propietario is propietario
            for mascota in self.mascotas
        ):
            raise ValueError("Ese propietario ya tiene una mascota con ese nombre.")

        mascota = Mascota(
            nombre,
            especie,
            edad,
            propietario,
            self._nuevo_id("M"),
            sexo,
            esterilizado,
        )
        self.mascotas.append(mascota)
        self.guardar_datos()
        return mascota

    def listar_mascotas(self):
        return self.mascotas

    def buscar_mascotas(self, termino=""):
        termino = self._texto(termino).lower()
        return list(
            filter(
                lambda mascota: termino in mascota.nombre.lower()
                or termino in mascota.especie.lower()
                or termino in mascota.sexo.lower()
                or termino in mascota.esterilizado.lower()
                or termino in mascota.propietario.nombre.lower(),
                self.mascotas,
            )
        )

    def actualizar_mascota(
        self,
        indice_mascota,
        nombre,
        especie,
        edad,
        propietario,
        sexo="No especificado",
        esterilizado="No especificado",
    ):
        if indice_mascota < 0 or indice_mascota >= len(self.mascotas):
            raise ValueError("Selecciona una mascota válida para editar.")
        nombre = self._texto(nombre)
        especie = self._texto(especie)
        edad = self._texto(edad)
        sexo, esterilizado = self._validar_datos_mascota(
            nombre,
            especie,
            edad,
            sexo,
            esterilizado,
        )
        self.mascotas[indice_mascota].actualizar(
            nombre,
            especie,
            edad,
            propietario,
            sexo,
            esterilizado,
        )
        self.guardar_datos()
        return self.mascotas[indice_mascota]

    def eliminar_mascota(self, indice_mascota):
        if indice_mascota < 0 or indice_mascota >= len(self.mascotas):
            raise ValueError("Selecciona una mascota válida.")
        mascota = self.mascotas.pop(indice_mascota)
        self.citas = [cita for cita in self.citas if cita.mascota is not mascota]
        self.atenciones = [
            atencion for atencion in self.atenciones if atencion.mascota is not mascota
        ]
        self.guardar_datos()

    def registrar_cita(self, mascota, fecha, hora, motivo, estado="Pendiente"):
        fecha = self._texto(fecha)
        hora = self._texto(hora)
        motivo = self._texto(motivo)
        if fecha == "" or hora == "" or motivo == "":
            raise ValueError("Completa fecha, hora y motivo.")
        cita = Cita(mascota, fecha, hora, motivo, estado, self._nuevo_id("C"))
        self.citas.append(cita)
        self.guardar_datos()
        return cita

    def listar_citas(self):
        return self.citas

    def actualizar_cita(self, indice_cita, mascota, fecha, hora, motivo, estado):
        if indice_cita < 0 or indice_cita >= len(self.citas):
            raise ValueError("Selecciona una cita válida para editar.")
        fecha = self._texto(fecha)
        hora = self._texto(hora)
        motivo = self._texto(motivo)
        if fecha == "" or hora == "" or motivo == "" or estado == "":
            raise ValueError("Completa todos los datos de la cita.")
        self.citas[indice_cita].actualizar(mascota, fecha, hora, motivo, estado)
        self.guardar_datos()
        return self.citas[indice_cita]

    def cambiar_estado_cita(self, indice_cita, estado):
        if indice_cita < 0 or indice_cita >= len(self.citas):
            raise ValueError("Selecciona una cita válida.")
        if estado not in ("Pendiente", "Atendida", "Cancelada"):
            raise ValueError("Estado de cita inválido.")
        self.citas[indice_cita].estado = estado
        self.guardar_datos()

    def eliminar_cita(self, indice_cita):
        if indice_cita < 0 or indice_cita >= len(self.citas):
            raise ValueError("Selecciona una cita válida.")
        self.citas.pop(indice_cita)
        self.guardar_datos()

    def filtrar_citas(self, estado="", fecha=""):
        estado = self._texto(estado)
        fecha = self._texto(fecha)
        return list(
            filter(
                lambda cita: (estado == "" or cita.estado == estado)
                and (fecha == "" or fecha in cita.fecha),
                self.citas,
            )
        )

    def registrar_pago(self, concepto, monto, metodo, estado):
        concepto = self._texto(concepto)
        metodo = self._texto(metodo)
        estado = self._texto(estado)
        try:
            monto = float(monto)
        except (TypeError, ValueError):
            raise ValueError("El monto debe ser un número válido.")
        if concepto == "" or metodo == "" or estado == "":
            raise ValueError("Completa todos los datos del pago.")
        if monto <= 0:
            raise ValueError("El monto debe ser mayor que cero.")
        pago = Pago(concepto, monto, metodo, estado, self._nuevo_id("G"))
        self.pagos.append(pago)
        self.guardar_datos()
        return pago

    def listar_pagos(self):
        return self.pagos

    def filtrar_pagos(self, metodo="", estado=""):
        metodo = self._texto(metodo)
        estado = self._texto(estado)
        return list(
            filter(
                lambda pago: (metodo == "" or pago.metodo == metodo)
                and (estado == "" or pago.estado == estado),
                self.pagos,
            )
        )

    def actualizar_pago(self, indice_pago, concepto, monto, metodo, estado):
        if indice_pago < 0 or indice_pago >= len(self.pagos):
            raise ValueError("Selecciona un pago válido para editar.")
        try:
            monto = float(monto)
        except (TypeError, ValueError):
            raise ValueError("El monto debe ser un número válido.")
        if self._texto(concepto) == "" or monto <= 0 or metodo == "" or estado == "":
            raise ValueError("Completa correctamente todos los datos del pago.")
        self.pagos[indice_pago].actualizar(concepto, monto, metodo, estado)
        self.guardar_datos()
        return self.pagos[indice_pago]

    def eliminar_pago(self, indice_pago):
        if indice_pago < 0 or indice_pago >= len(self.pagos):
            raise ValueError("Selecciona un pago válido.")
        self.pagos.pop(indice_pago)
        self.guardar_datos()

    def calcular_total_confirmado(self):
        confirmados = filter(lambda pago: pago.estado == "Confirmado", self.pagos)
        return reduce(lambda total, pago: total + pago.monto, confirmados, 0.0)

    def resumen_pagos_por_metodo(self):
        resumen = {}
        for pago in filter(lambda item: item.estado == "Confirmado", self.pagos):
            resumen[pago.metodo] = resumen.get(pago.metodo, 0.0) + pago.monto
        return resumen

    def registrar_atencion(self, mascota, fecha, diagnostico, tratamiento, vacuna):
        valores = [fecha, diagnostico, tratamiento, vacuna]
        if any(self._texto(valor) == "" for valor in valores):
            raise ValueError("Completa todos los datos de la consulta.")
        atencion = Atencion(
            mascota,
            self._texto(fecha),
            self._texto(diagnostico),
            self._texto(tratamiento),
            self._texto(vacuna),
            self._nuevo_id("A"),
        )
        self.atenciones.append(atencion)
        self.guardar_datos()
        return atencion

    def listar_atenciones(self):
        return self.atenciones

    def actualizar_atencion(
        self,
        indice_atencion,
        mascota,
        fecha,
        diagnostico,
        tratamiento,
        vacuna,
    ):
        if indice_atencion < 0 or indice_atencion >= len(self.atenciones):
            raise ValueError("Selecciona una consulta válida para editar.")
        valores = [fecha, diagnostico, tratamiento, vacuna]
        if any(self._texto(valor) == "" for valor in valores):
            raise ValueError("Completa todos los datos de la consulta.")
        self.atenciones[indice_atencion].actualizar(
            mascota,
            self._texto(fecha),
            self._texto(diagnostico),
            self._texto(tratamiento),
            self._texto(vacuna),
        )
        self.guardar_datos()
        return self.atenciones[indice_atencion]

    def eliminar_atencion(self, indice_atencion):
        if indice_atencion < 0 or indice_atencion >= len(self.atenciones):
            raise ValueError("Selecciona una consulta válida.")
        self.atenciones.pop(indice_atencion)
        self.guardar_datos()

    def filtrar_atenciones(
        self,
        nombre_mascota="",
        vacuna="",
        fecha_desde="",
        fecha_hasta="",
    ):
        nombre_mascota = self._texto(nombre_mascota).lower()
        vacuna = self._texto(vacuna).lower()
        fecha_desde_obj = self._normalizar_fecha(fecha_desde)
        fecha_hasta_obj = self._normalizar_fecha(fecha_hasta)

        def coincide(atencion):
            fecha_atencion = self._normalizar_fecha(atencion.fecha)
            return (
                (nombre_mascota == "" or nombre_mascota in atencion.mascota.nombre.lower())
                and (vacuna == "" or vacuna in atencion.vacuna.lower())
                and (
                    fecha_desde_obj is None
                    or fecha_atencion is None
                    or fecha_atencion >= fecha_desde_obj
                )
                and (
                    fecha_hasta_obj is None
                    or fecha_atencion is None
                    or fecha_atencion <= fecha_hasta_obj
                )
            )

        return list(filter(coincide, self.atenciones))

    def generar_reporte_diario(self):
        total = self.calcular_total_confirmado()
        resumen_metodos = self.resumen_pagos_por_metodo()
        lineas = [
            "REPORTE DIARIO - CLÍNICA VETERINARIA DR. LEO",
            "",
            f"Propietarios registrados: {len(self.propietarios)}",
            f"Mascotas registradas: {len(self.mascotas)}",
            f"Citas registradas: {len(self.citas)}",
            f"Consultas registradas: {len(self.atenciones)}",
            f"Pagos registrados: {len(self.pagos)}",
            f"Total confirmado: S/ {total:.2f}",
            "",
            "INGRESOS POR MÉTODO",
        ]
        if not resumen_metodos:
            lineas.append("No hay pagos confirmados.")
        else:
            for metodo, monto in sorted(resumen_metodos.items()):
                lineas.append(f"{metodo}: S/ {monto:.2f}")
        lineas.extend(["", "CITAS"])
        if not self.citas:
            lineas.append("No hay citas registradas.")
        else:
            lineas.extend(str(cita) for cita in self.citas)
        lineas.extend(["", "PAGOS"])
        if not self.pagos:
            lineas.append("No hay pagos registrados.")
        else:
            lineas.extend(str(pago) for pago in self.pagos)
        return "\n".join(lineas)

    def exportar_reporte_diario(self):
        carpeta_data = os.path.dirname(self.ruta_datos)
        os.makedirs(carpeta_data, exist_ok=True)
        ruta_reporte = os.path.join(carpeta_data, "reporte_diario.txt")
        with open(ruta_reporte, "w", encoding="utf-8") as archivo:
            archivo.write(self.generar_reporte_diario())
        return ruta_reporte

    def exportar_datos_csv(self):
        carpeta_data = os.path.dirname(self.ruta_datos)
        carpeta_csv = os.path.join(carpeta_data, "exportacion_csv")
        os.makedirs(carpeta_csv, exist_ok=True)
        archivos = {
            "propietarios.csv": (
                [
                    "id_ponkis",
                    "nombre",
                    "dni_cifrado",
                    "dni_protegido",
                    "telefono_cifrado",
                    "telefono_protegido",
                ],
                [
                    [
                        propietario.id_ponkis,
                        propietario.nombre,
                        CifradorDatos.cifrar(propietario.dni),
                        propietario.obtener_dni_protegido(),
                        CifradorDatos.cifrar(propietario.telefono),
                        self._proteger_telefono(propietario.telefono),
                    ]
                    for propietario in self.propietarios
                ],
            ),
            "mascotas.csv": (
                [
                    "id_ponkis",
                    "nombre",
                    "especie",
                    "edad",
                    "sexo",
                    "esterilizado",
                    "propietario_id",
                ],
                [
                    [
                        mascota.id_ponkis,
                        mascota.nombre,
                        mascota.especie,
                        mascota.edad,
                        mascota.sexo,
                        mascota.esterilizado,
                        mascota.propietario.id_ponkis,
                    ]
                    for mascota in self.mascotas
                ],
            ),
            "citas.csv": (
                ["id_ponkis", "mascota_id", "fecha", "hora", "motivo", "estado"],
                [
                    [
                        cita.id_ponkis,
                        cita.mascota.id_ponkis,
                        cita.fecha,
                        cita.hora,
                        cita.motivo,
                        cita.estado,
                    ]
                    for cita in self.citas
                ],
            ),
            "pagos.csv": (
                ["id_ponkis", "concepto", "monto", "metodo", "estado"],
                [
                    [
                        pago.id_ponkis,
                        pago.concepto,
                        f"{pago.monto:.2f}",
                        pago.metodo,
                        pago.estado,
                    ]
                    for pago in self.pagos
                ],
            ),
            "consultas.csv": (
                ["id_ponkis", "mascota_id", "fecha", "diagnostico", "tratamiento", "vacuna"],
                [
                    [
                        atencion.id_ponkis,
                        atencion.mascota.id_ponkis,
                        atencion.fecha,
                        atencion.diagnostico,
                        atencion.tratamiento,
                        atencion.vacuna,
                    ]
                    for atencion in self.atenciones
                ],
            ),
        }
        rutas = []
        for nombre, (cabeceras, filas) in archivos.items():
            ruta = os.path.join(carpeta_csv, nombre)
            with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(cabeceras)
                escritor.writerows(filas)
            rutas.append(ruta)
        return carpeta_csv, rutas

    def importar_propietarios_csv(self, ruta_csv):
        agregados = 0
        with open(ruta_csv, "r", newline="", encoding="utf-8-sig") as archivo:
            lector = csv.DictReader(archivo)
            campos = set(lector.fieldnames or [])
            if "nombre" not in campos or not ({"dni", "dni_cifrado"} & campos):
                raise ValueError("El CSV debe incluir nombre y dni o dni_cifrado.")
            for fila in lector:
                nombre = self._texto(fila.get("nombre"))
                dni = CifradorDatos.descifrar(fila.get("dni_cifrado", ""))
                dni = dni or self._texto(fila.get("dni"))
                telefono = CifradorDatos.descifrar(fila.get("telefono_cifrado", ""))
                telefono = telefono or self._texto(fila.get("telefono")) or "000000000"
                if nombre == "" or dni == "":
                    continue
                if any(propietario.dni == dni for propietario in self.propietarios):
                    continue
                self.validar_propietario(nombre, dni, telefono)
                self.propietarios.append(
                    Propietario(nombre, dni, telefono, self._nuevo_id("P"))
                )
                agregados += 1
        if agregados:
            self.guardar_datos()
        return agregados

    @staticmethod
    def _proteger_telefono(telefono):
        telefono = str(telefono or "")
        if len(telefono) <= 2:
            return "*" * len(telefono)
        return "*" * (len(telefono) - 2) + telefono[-2:]

    def preparar_recordatorio_cita(self, indice_cita):
        cita = self.citas[indice_cita]
        return (
            f"Hola {cita.mascota.propietario.nombre}, le recordamos que "
            f"{cita.mascota.nombre} tiene una cita programada para el "
            f"{cita.fecha} a las {cita.hora}. Motivo: {cita.motivo}.\n\n"
            "Atentamente,\nClínica veterinaria Dr. Leo"
        )

    def generar_historial_mascota(self, indice_mascota):
        mascota = self.mascotas[indice_mascota]
        lineas = [
            "HISTORIAL CLÍNICO",
            "",
            f"Mascota: {mascota.nombre}",
            f"Especie: {mascota.especie}",
            f"Edad: {mascota.edad}",
            f"Sexo: {mascota.sexo}",
            f"Esterilizado: {mascota.esterilizado}",
            f"Propietario: {mascota.propietario.nombre}",
            f"DNI propietario: {mascota.propietario.obtener_dni_protegido()}",
            "",
            "ATENCIONES Y VACUNAS",
        ]
        historial = list(
            filter(
                lambda atencion: atencion.mascota.id_ponkis == mascota.id_ponkis,
                self.atenciones,
            )
        )
        if not historial:
            lineas.append("No hay consultas registradas para esta mascota.")
        else:
            for atencion in historial:
                lineas.extend(
                    [
                        "",
                        f"Fecha: {atencion.fecha}",
                        f"Diagnóstico: {atencion.diagnostico}",
                        f"Tratamiento: {atencion.tratamiento}",
                        f"Vacuna: {atencion.vacuna}",
                    ]
                )
        return "\n".join(lineas)

    def guardar_datos(self):
        carpeta_data = os.path.dirname(self.ruta_datos)
        os.makedirs(carpeta_data, exist_ok=True)
        datos = {
            "version": 2,
            "datos_personales_protegidos": True,
            "propietarios": [
                {
                    "id_ponkis": propietario.id_ponkis,
                    "nombre": CifradorDatos.cifrar(propietario.nombre),
                    "dni": CifradorDatos.cifrar(propietario.dni),
                    "telefono": CifradorDatos.cifrar(propietario.telefono),
                }
                for propietario in self.propietarios
            ],
            "mascotas": [
                {
                    "id_ponkis": mascota.id_ponkis,
                    "nombre": mascota.nombre,
                    "especie": mascota.especie,
                    "edad": mascota.edad,
                    "sexo": mascota.sexo,
                    "esterilizado": mascota.esterilizado,
                    "propietario_id": mascota.propietario.id_ponkis,
                    "propietario": CifradorDatos.cifrar(mascota.propietario.nombre),
                    "propietario_dni": CifradorDatos.cifrar(mascota.propietario.dni),
                }
                for mascota in self.mascotas
            ],
            "citas": [
                {
                    "id_ponkis": cita.id_ponkis,
                    "mascota_id": cita.mascota.id_ponkis,
                    "mascota": cita.mascota.nombre,
                    "propietario_id": cita.mascota.propietario.id_ponkis,
                    "propietario_dni": CifradorDatos.cifrar(cita.mascota.propietario.dni),
                    "fecha": cita.fecha,
                    "hora": cita.hora,
                    "motivo": cita.motivo,
                    "estado": cita.estado,
                }
                for cita in self.citas
            ],
            "pagos": [
                {
                    "id_ponkis": pago.id_ponkis,
                    "concepto": pago.concepto,
                    "monto": pago.monto,
                    "metodo": pago.metodo,
                    "estado": pago.estado,
                }
                for pago in self.pagos
            ],
            "atenciones": [
                {
                    "id_ponkis": atencion.id_ponkis,
                    "mascota_id": atencion.mascota.id_ponkis,
                    "mascota": atencion.mascota.nombre,
                    "propietario_dni": CifradorDatos.cifrar(atencion.mascota.propietario.dni),
                    "fecha": atencion.fecha,
                    "diagnostico": atencion.diagnostico,
                    "tratamiento": atencion.tratamiento,
                    "vacuna": atencion.vacuna,
                }
                for atencion in self.atenciones
            ],
        }
        with open(self.ruta_datos, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

        self._guardar_en_sqlite()

    def cargar_datos(self):
        if os.path.exists(self.ruta_bd) and self._base_sqlite_tiene_datos():
            self._cargar_desde_sqlite()
            return

        self._cargar_desde_json()
        if self.propietarios or self.mascotas or self.citas or self.pagos or self.atenciones:
            self._guardar_en_sqlite()

    def _base_sqlite_tiene_datos(self):
        try:
            with sqlite3.connect(self.ruta_bd) as conexion:
                tabla = conexion.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='propietarios'"
                ).fetchone()
                if tabla is None:
                    return False
                cantidad = conexion.execute("SELECT COUNT(*) FROM propietarios").fetchone()[0]
                otras = sum(
                    conexion.execute(f"SELECT COUNT(*) FROM {tabla_nombre}").fetchone()[0]
                    for tabla_nombre in ("mascotas", "citas", "pagos", "atenciones")
                )
                return cantidad + otras > 0
        except sqlite3.Error:
            return False

    def _asegurar_columnas_mascotas(self, conexion):
        columnas = {
            fila[1]
            for fila in conexion.execute("PRAGMA table_info(mascotas)").fetchall()
        }
        if "sexo" not in columnas:
            conexion.execute(
                "ALTER TABLE mascotas ADD COLUMN sexo TEXT NOT NULL DEFAULT 'No especificado'"
            )
        if "esterilizado" not in columnas:
            conexion.execute(
                "ALTER TABLE mascotas ADD COLUMN esterilizado TEXT NOT NULL DEFAULT 'No especificado'"
            )

    def _guardar_en_sqlite(self):
        carpeta_data = os.path.dirname(self.ruta_bd)
        os.makedirs(carpeta_data, exist_ok=True)
        with sqlite3.connect(self.ruta_bd) as conexion:
            conexion.executescript(
                """
                CREATE TABLE IF NOT EXISTS propietarios (
                    id_ponkis TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    dni TEXT NOT NULL,
                    telefono TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS mascotas (
                    id_ponkis TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    especie TEXT NOT NULL,
                    edad TEXT NOT NULL,
                    sexo TEXT NOT NULL DEFAULT 'No especificado',
                    esterilizado TEXT NOT NULL DEFAULT 'No especificado',
                    propietario_id TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS citas (
                    id_ponkis TEXT PRIMARY KEY,
                    mascota_id TEXT NOT NULL,
                    fecha TEXT NOT NULL,
                    hora TEXT NOT NULL,
                    motivo TEXT NOT NULL,
                    estado TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS pagos (
                    id_ponkis TEXT PRIMARY KEY,
                    concepto TEXT NOT NULL,
                    monto REAL NOT NULL,
                    metodo TEXT NOT NULL,
                    estado TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS atenciones (
                    id_ponkis TEXT PRIMARY KEY,
                    mascota_id TEXT NOT NULL,
                    fecha TEXT NOT NULL,
                    diagnostico TEXT NOT NULL,
                    tratamiento TEXT NOT NULL,
                    vacuna TEXT NOT NULL
                );
                """
            )
            self._asegurar_columnas_mascotas(conexion)
            for tabla in ("atenciones", "citas", "pagos", "mascotas", "propietarios"):
                conexion.execute(f"DELETE FROM {tabla}")

            conexion.executemany(
                "INSERT INTO propietarios VALUES (?, ?, ?, ?)",
                [
                    (
                        propietario.id_ponkis,
                        CifradorDatos.cifrar(propietario.nombre),
                        CifradorDatos.cifrar(propietario.dni),
                        CifradorDatos.cifrar(propietario.telefono),
                    )
                    for propietario in self.propietarios
                ],
            )
            conexion.executemany(
                """
                INSERT INTO mascotas
                (id_ponkis, nombre, especie, edad, sexo, esterilizado, propietario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        mascota.id_ponkis,
                        mascota.nombre,
                        mascota.especie,
                        mascota.edad,
                        mascota.sexo,
                        mascota.esterilizado,
                        mascota.propietario.id_ponkis,
                    )
                    for mascota in self.mascotas
                ],
            )
            conexion.executemany(
                "INSERT INTO citas VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (
                        cita.id_ponkis,
                        cita.mascota.id_ponkis,
                        cita.fecha,
                        cita.hora,
                        cita.motivo,
                        cita.estado,
                    )
                    for cita in self.citas
                ],
            )
            conexion.executemany(
                "INSERT INTO pagos VALUES (?, ?, ?, ?, ?)",
                [
                    (
                        pago.id_ponkis,
                        pago.concepto,
                        pago.monto,
                        pago.metodo,
                        pago.estado,
                    )
                    for pago in self.pagos
                ],
            )
            conexion.executemany(
                "INSERT INTO atenciones VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (
                        atencion.id_ponkis,
                        atencion.mascota.id_ponkis,
                        atencion.fecha,
                        atencion.diagnostico,
                        atencion.tratamiento,
                        atencion.vacuna,
                    )
                    for atencion in self.atenciones
                ],
            )

    def _cargar_desde_sqlite(self):
        with sqlite3.connect(self.ruta_bd) as conexion:
            self._asegurar_columnas_mascotas(conexion)
            propietarios = conexion.execute(
                "SELECT id_ponkis, nombre, dni, telefono FROM propietarios"
            ).fetchall()
            mascotas = conexion.execute(
                """
                SELECT id_ponkis, nombre, especie, edad, propietario_id, sexo, esterilizado
                FROM mascotas
                """
            ).fetchall()
            citas = conexion.execute(
                "SELECT id_ponkis, mascota_id, fecha, hora, motivo, estado FROM citas"
            ).fetchall()
            pagos = conexion.execute(
                "SELECT id_ponkis, concepto, monto, metodo, estado FROM pagos"
            ).fetchall()
            atenciones = conexion.execute(
                "SELECT id_ponkis, mascota_id, fecha, diagnostico, tratamiento, vacuna FROM atenciones"
            ).fetchall()

        self.propietarios = [
            Propietario(
                CifradorDatos.descifrar(nombre),
                CifradorDatos.descifrar(dni),
                CifradorDatos.descifrar(telefono),
                id_ponkis,
            )
            for id_ponkis, nombre, dni, telefono in propietarios
        ]
        self.mascotas = []
        for id_ponkis, nombre, especie, edad, propietario_id, sexo, esterilizado in mascotas:
            propietario = self.buscar_propietario_por_id(propietario_id)
            if propietario is not None:
                self.mascotas.append(
                    Mascota(nombre, especie, edad, propietario, id_ponkis, sexo, esterilizado)
                )

        self.citas = []
        for id_ponkis, mascota_id, fecha, hora, motivo, estado in citas:
            mascota = self.buscar_mascota_por_id(mascota_id)
            if mascota is not None:
                self.citas.append(
                    Cita(mascota, fecha, hora, motivo, estado, id_ponkis)
                )

        self.pagos = [
            Pago(concepto, monto, metodo, estado, id_ponkis)
            for id_ponkis, concepto, monto, metodo, estado in pagos
        ]
        self.atenciones = []
        for id_ponkis, mascota_id, fecha, diagnostico, tratamiento, vacuna in atenciones:
            mascota = self.buscar_mascota_por_id(mascota_id)
            if mascota is not None:
                self.atenciones.append(
                    Atencion(
                        mascota,
                        fecha,
                        diagnostico,
                        tratamiento,
                        vacuna,
                        id_ponkis,
                    )
                )

    def _cargar_desde_json(self):
        if not os.path.exists(self.ruta_datos):
            return
        try:
            with open(self.ruta_datos, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except (OSError, json.JSONDecodeError):
            return

        self.propietarios = []
        for propietario in datos.get("propietarios", []):
            if not isinstance(propietario, dict):
                continue
            self.propietarios.append(
                Propietario(
                    CifradorDatos.descifrar(propietario.get("nombre", "")),
                    CifradorDatos.descifrar(propietario.get("dni", "")),
                    CifradorDatos.descifrar(propietario.get("telefono", "")),
                    propietario.get("id_ponkis") or self._nuevo_id("P"),
                )
            )

        self.mascotas = []
        for datos_mascota in datos.get("mascotas", []):
            if not isinstance(datos_mascota, dict):
                continue
            propietario = self.buscar_propietario_por_id(
                datos_mascota.get("propietario_id", "")
            )
            if propietario is None:
                propietario = self.buscar_propietario_para_carga(
                    datos_mascota.get("propietario_dni", ""),
                    datos_mascota.get("propietario", ""),
                )
            if propietario is None:
                propietario = self.crear_propietario_temporal_para_carga(datos_mascota)
            self.mascotas.append(
                Mascota(
                    datos_mascota.get("nombre", ""),
                    datos_mascota.get("especie", ""),
                    datos_mascota.get("edad", ""),
                    propietario,
                    datos_mascota.get("id_ponkis") or self._nuevo_id("M"),
                    datos_mascota.get("sexo", "No especificado"),
                    datos_mascota.get("esterilizado", "No especificado"),
                )
            )

        self.citas = []
        for datos_cita in datos.get("citas", []):
            if not isinstance(datos_cita, dict):
                continue
            mascota = self.buscar_mascota_por_id(datos_cita.get("mascota_id", ""))
            if mascota is None:
                mascota = self.buscar_mascota_para_carga(
                    datos_cita.get("mascota", ""),
                    datos_cita.get("propietario_dni", ""),
                    datos_cita.get("propietario", ""),
                )
            if mascota is None:
                continue
            self.citas.append(
                Cita(
                    mascota,
                    datos_cita.get("fecha", ""),
                    datos_cita.get("hora", ""),
                    datos_cita.get("motivo", ""),
                    datos_cita.get("estado", "Pendiente"),
                    datos_cita.get("id_ponkis") or self._nuevo_id("C"),
                )
            )

        self.pagos = []
        for datos_pago in datos.get("pagos", []):
            if not isinstance(datos_pago, dict):
                continue

            id_pago = datos_pago.get("id_ponkis", "")
            ids_existentes = {pago.id_ponkis for pago in self.pagos}
            if not id_pago or id_pago in ids_existentes:
                id_pago = self._nuevo_id("G")

            self.pagos.append(
                Pago(
                    datos_pago.get("concepto", ""),
                    datos_pago.get("monto", 0),
                    datos_pago.get("metodo", ""),
                    datos_pago.get("estado", ""),
                    id_pago,
                )
            )

        self.atenciones = []
        for datos_atencion in datos.get("atenciones", []):
            if not isinstance(datos_atencion, dict):
                continue
            mascota = self.buscar_mascota_por_id(datos_atencion.get("mascota_id", ""))
            if mascota is None:
                mascota = self.buscar_mascota_para_carga(
                    datos_atencion.get("mascota", ""),
                    datos_atencion.get("propietario_dni", ""),
                    datos_atencion.get("propietario", ""),
                )
            if mascota is None:
                continue
            self.atenciones.append(
                Atencion(
                    mascota,
                    datos_atencion.get("fecha", ""),
                    datos_atencion.get("diagnostico", ""),
                    datos_atencion.get("tratamiento", ""),
                    datos_atencion.get("vacuna", ""),
                    datos_atencion.get("id_ponkis") or self._nuevo_id("A"),
                )
            )

    def buscar_propietario_por_id(self, id_ponkis):
        return next(
            (
                propietario
                for propietario in self.propietarios
                if id_ponkis and propietario.id_ponkis == id_ponkis
            ),
            None,
        )

    def buscar_mascota_por_id(self, id_ponkis):
        return next(
            (
                mascota
                for mascota in self.mascotas
                if id_ponkis and mascota.id_ponkis == id_ponkis
            ),
            None,
        )

    def buscar_propietario_para_carga(self, dni, nombre):
        if isinstance(nombre, dict):
            dni = dni or nombre.get("dni", "")
            nombre = nombre.get("nombre", "")
        dni = CifradorDatos.descifrar(dni)
        nombre = CifradorDatos.descifrar(nombre)
        for propietario in self.propietarios:
            if dni != "" and propietario.dni == dni:
                return propietario
        for propietario in self.propietarios:
            if propietario.nombre == nombre:
                return propietario
        return None

    def buscar_mascota_para_carga(
        self,
        nombre_mascota,
        dni_propietario,
        nombre_propietario="",
    ):
        dni_propietario = CifradorDatos.descifrar(dni_propietario)
        nombre_propietario = CifradorDatos.descifrar(nombre_propietario)
        for mascota in self.mascotas:
            mismo_nombre = mascota.nombre == nombre_mascota
            mismo_dni = dni_propietario == "" or mascota.propietario.dni == dni_propietario
            mismo_propietario = (
                nombre_propietario == ""
                or mascota.propietario.nombre == nombre_propietario
            )
            if mismo_nombre and mismo_dni and mismo_propietario:
                return mascota
        return None

    def crear_propietario_temporal_para_carga(self, mascota):
        nombre_propietario = mascota.get("propietario", "")
        if isinstance(nombre_propietario, dict):
            nombre = nombre_propietario.get("nombre", "Propietario sin datos")
            dni = nombre_propietario.get("dni", "")
            telefono = nombre_propietario.get("telefono", "")
        else:
            nombre = nombre_propietario or "Propietario sin datos"
            dni = mascota.get("propietario_dni", "")
            telefono = ""
        propietario = Propietario(
            CifradorDatos.descifrar(nombre),
            CifradorDatos.descifrar(dni),
            CifradorDatos.descifrar(telefono),
            mascota.get("propietario_id") or self._nuevo_id("P"),
        )
        self.propietarios.append(propietario)
        return propietario
