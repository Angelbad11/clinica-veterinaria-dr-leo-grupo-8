class EstrategiaPago:
    def obtener_observacion(self):
        return "Pago registrado"


class PagoEfectivo(EstrategiaPago):
    def obtener_observacion(self):
        return "Pago recibido en caja"


class PagoYape(EstrategiaPago):
    def obtener_observacion(self):
        return "Pago digital por Yape"


class PagoPlin(EstrategiaPago):
    def obtener_observacion(self):
        return "Pago digital por Plin"


class PagoPOS(EstrategiaPago):
    def obtener_observacion(self):
        return "Pago con tarjeta mediante POS"


class PagoTransferencia(EstrategiaPago):
    def obtener_observacion(self):
        return "Pago mediante transferencia bancaria"