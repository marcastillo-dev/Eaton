# services/carrito_service.py

class CarritoService:

    @staticmethod
    def agregar(carrito, producto):

        codigo = producto["Catalogo"]

        for item in carrito:

            if item["Catalogo"] == codigo:

                item["Cantidad"] += 1
                return

        carrito.append({
            "Catalogo": producto["Catalogo"],
            "Descripcion": producto["Descripcion"],
            "Precio": producto["Precio"],
            "Cantidad": 1
        })

    @staticmethod
    def eliminar(carrito, posicion):

        item = carrito[posicion]

        if item["Cantidad"] > 1:
            item["Cantidad"] -= 1
        else:
            carrito.pop(posicion)