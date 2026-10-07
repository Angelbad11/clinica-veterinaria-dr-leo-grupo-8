from services.estrategias_pago import (
    PagoEfectivo,
    PagoYape,
    PagoPlin,
    PagoPOS,
    PagoTransferencia
)


class FabricaPago:
    @staticmethod
    def crear_estrategia(metodo):
        if metodo == "Efectivo":
            return PagoEfectivo()

        if metodo == "Yape":
            return PagoYape()

        if metodo == "Plin":
            return PagoPlin()

        if metodo == "POS":
            return PagoPOS()

        if metodo == "Transferencia":
            return PagoTransferencia()

        raise ValueError("Método de pago no válido")