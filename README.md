# Clase `Operator`
> **Antes que nada, para ejecutar mi entorno, hay que crear dos carpetas `logs` y `setups`, para los resultados y el setup**

La clase `Operator` es un agente que simula un sistema de subasta automatizada para gestionar la venta de productos a comerciantes (merchants).

## Protocolo:
- Los comerciantes recibirán tres caso:
  - **CASO 1**: El Operator envía un producto nuevo:
    - 4. **Registrar una venta**
            ```python
            sale_message = {
                "msg": "New Product",
                "product": {
                    "product_number": 1,
                    "product_type": "H",
                    "price": 15,
                    "min_price": 4
                },
                "merchant_id": None
            }
            ```
            El Operator enviará `msg`, `product` y `merchant_id` al `publish_channel`, de esta forma, cada mercante puede saber si se trata de un nuevo producto.

  - **CASO 2**: El Operator vende un producto a un Merchant:
    - 4. **Registrar una venta**
            ```python
            sale_message = {
                "msg": "Yes",
                "product": {
                    "product_number": 1,
                    "product_type": "H",
                    "price": 15,
                    "min_price": 4
                },
                "merchant_id": "1"
            }
            ```
            Si el producto es comprado envía el producto por el `publish_channel`, pero con un merchant_id, así los demás mercantes pueden saber si ese **YES** es para ellos o no.
  - **CASO 3**: El Operator envía un producto con el precio reducido:
    - 4. **Registrar una venta**
            ```python
            sale_message = {
                "msg": "Reducing Price",
                "product": {
                    "product_number": 1,
                    "product_type": "H",
                    "price": 10,
                    "min_price": 4
                },
                "merchant_id": None
            }
            ```
            Mismo que el nuevo producto pero en el mensaje aclarará que es un producto reducido de precio.

## Funcionalidades principales

### Inicialización
- **Canal de publicación (`publish_channel`)**: Los comerciantes suscritos a este canal recibirán información sobre nuevos productos y cambios de precio.
- **Lista de productos**: El operador gestiona una lista de productos a subastar.
- **Timer para reducción de precios**: Si un producto no se vende, el operador reduce su precio periódicamente hasta alcanzar el precio mínimo.

### Métodos principales
#### - `setup_products(num_products)`
Inicializa una lista de productos con un número especificado (`num_products`), asignando tipos y precios aleatorios.
- Tipos de productos: `'H'` (HAke), `'S'` (Sole), `'T'` (Tuna).
- Precio inicial: Valores aleatorios entre 10 y 25.
- Precio mínimo: Fijado en `4` unidades.

#### - `send_new_product()`
Selecciona el próximo producto de la lista y lo publica a los comerciantes a través del canal `publish_channel`.

#### - `reduce_price()`
Si un producto no se vende, reduce su precio en 5 unidades y publica la actualización. Si el precio alcanza el mínimo, el producto queda marcado como no vendido.

#### - `handle_sale(message)`
Gestiona una venta tras recibir un mensaje de confirmación por parte de un comerciante. Registra la venta en un log e informa a los demás comerciantes que el producto ya fue vendido por el `publish_channel`.

#### - `save_logs()`
Guarda los registros de los productos y ventas en archivos CSV para análisis posterior. Pueden descargar la extensión CSV de **ReprEng**.

### Ejemplo de uso
1. **Configuración inicial**
```python
from osbrain import run_agent
operator = run_agent('operator', base=Operator)
operator.setup_products(num_products= N_products_seleccionados)
```

2. **Publicar un producto**
```python
operator.send_new_product()
```

3. **Simular reducción de precios**
```python
# Si nadie compra el producto actual, el precio se reducirá cada segundo automáticamente.
# Inicia el temporizador para reducir precios.
operator.start_timer() => {
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(1.0, self.reduce_price)
        self.timer.start()
}
```
            
## Notas
- Los comerciantes deben implementar su propia lógica para escuchar mensajes del canal `publish_channel` y decidir si compran o no el producto.
- La estructura de cada mensaje enviado al canal sigue el formato JSON.
- En el MAIN debereis crear un canal de respuesta para cada comerciante, en los cuales el Operator estará subscrito. Por ejemplo, en mi proyecto los mercantes envían su `YES` a `response_channel_{ID}` y el Operator se susbcribe a ellos.
```python
    merchant.bind('PUSH', alias='response_channel_' + str(i))
    operator.connect(merchant.addr('response_channel_' + str(i)), handler='handle_sale')
```
