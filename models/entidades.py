class Propietario:
    def __init__(self, nombre, dni="", telefono="", id_ponkis=""):
        self.nombre = nombre
        self.dni = dni
        self.telefono = telefono
        self.id_ponkis = id_ponkis

    def actualizar(self, nombre, dni, telefono):
        self.nombre = nombre
        self.dni = dni
        self.telefono = telefono

    def obtener_dni_protegido(self):
        if self.dni == "":
            return "No registrado"

        if len(self.dni) <= 2:
            return "*" * len(self.dni)

        return "*" * (len(self.dni) - 2) + self.dni[-2:]

    def __str__(self):
        return (
            f"{self.nombre} | DNI: {self.obtener_dni_protegido()} "
            f"| Teléfono: {self.telefono}"
        )


class Mascota:
    SEXOS = ("No especificado", "Macho", "Hembra")
    ESTERILIZADO = ("No especificado", "Sí", "No")

    def __init__(
        self,
        nombre,
        especie,
        edad,
        propietario,
        id_ponkis="",
        sexo="No especificado",
        esterilizado="No especificado",
    ):
        self.nombre = nombre
        self.especie = especie
        self.edad = edad
        self.propietario = propietario
        self.id_ponkis = id_ponkis
        self.sexo = self._normalizar_opcion(sexo, self.SEXOS)
        self.esterilizado = self._normalizar_opcion(esterilizado, self.ESTERILIZADO)

    @staticmethod
    def _normalizar_opcion(valor, opciones):
        texto = str(valor or "").strip()
        if texto == "":
            return "No especificado"
        for opcion in opciones:
            if texto.casefold() == opcion.casefold():
                return opcion
        return texto

    def actualizar(self, nombre, especie, edad, propietario, sexo, esterilizado):
        self.nombre = nombre
        self.especie = especie
        self.edad = edad
        self.propietario = propietario
        self.sexo = self._normalizar_opcion(sexo, self.SEXOS)
        self.esterilizado = self._normalizar_opcion(esterilizado, self.ESTERILIZADO)

    def __str__(self):
        return (
            f"{self.nombre} | Especie: {self.especie} | Edad: {self.edad} "
            f"| Sexo: {self.sexo} | Esterilizado: {self.esterilizado} "
            f"| Dueño: {self.propietario.nombre}"
        )


class Cita:
    def __init__(self, mascota, fecha, hora, motivo, estado="Pendiente", id_ponkis=""):
        self.mascota = mascota
        self.fecha = fecha
        self.hora = hora
        self.motivo = motivo
        self.estado = estado or "Pendiente"
        self.id_ponkis = id_ponkis

    def actualizar(self, mascota, fecha, hora, motivo, estado):
        self.mascota = mascota
        self.fecha = fecha
        self.hora = hora
        self.motivo = motivo
        self.estado = estado

    def __str__(self):
        return (
            f"{self.fecha} {self.hora} | Mascota: {self.mascota.nombre} "
            f"| Estado: {self.estado} | Motivo: {self.motivo}"
        )


class Pago:
    def __init__(self, concepto, monto, metodo, estado, id_ponkis=""):
        self.concepto = concepto
        self.monto = float(monto)
        self.metodo = metodo
        self.estado = estado
        self.id_ponkis = id_ponkis

    def actualizar(self, concepto, monto, metodo, estado):
        self.concepto = concepto
        self.monto = float(monto)
        self.metodo = metodo
        self.estado = estado

    def __str__(self):
        return (
            f"{self.concepto} | S/ {self.monto:.2f} "
            f"| Método: {self.metodo} | Estado: {self.estado}"
        )


class Atencion:
    def __init__(self, mascota, fecha, diagnostico, tratamiento, vacuna, id_ponkis=""):
        self.mascota = mascota
        self.fecha = fecha
        self.diagnostico = diagnostico
        self.tratamiento = tratamiento
        self.vacuna = vacuna
        self.id_ponkis = id_ponkis

    def actualizar(self, mascota, fecha, diagnostico, tratamiento, vacuna):
        self.mascota = mascota
        self.fecha = fecha
        self.diagnostico = diagnostico
        self.tratamiento = tratamiento
        self.vacuna = vacuna

    def __str__(self):
        return (
            f"{self.fecha} | Mascota: {self.mascota.nombre} "
            f"| Diagnóstico: {self.diagnostico} | Vacuna: {self.vacuna}"
        )
