import csv
from datetime import datetime
from osbrain import Agent
import random
from product import Product
import threading

# Configuramos los mensajes en formato JSON
import osbrain
osbrain.config['SERIALIZER'] = 'json'
class Operator(Agent):
    def on_init(self):
        # Crear un canal de publicación
        # Aquí se enviarán los productos a los comerciantes que estén suscritos
        self.bind('PUB', alias='publish_channel')
        
        # Parámetros de la subasta
        self.products = []
        self.current_product = None
        self.min_price = 2  # Precio mínimo para vender un producto
        self.log = []       # Registro de ventas
        self.timer = None   # Timer para reducir el precio

    def start_timer(self):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(1.0, self.reduce_price)
        self.timer.start()

    def stop_timer(self, alias=None):
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def get_products(self):
        return self.products
    
    def get_current_product(self):
        return self.current_product
    
    def setup_products(self, num_products):
        # Product List with random prices within (20, 50)
        product_types = ['H', 'S', 'T']  # Hake, Sole, Tuna
        for i in range(1, num_products + 1):
            product = Product(i, random.choice(product_types), random.randint(10, 25), self.min_price)
            self.products.append(product)
        
    def send_new_product(self):
        
        # Send a new product to the merchants subscribed
        if self.products:
            new_product = self.products.pop(0)
            self.current_product = Product(new_product.product_number, new_product.product_type, 
                                           new_product.price, new_product.min_price)
            
            self.log_info(f"New product: {self.current_product}")
            # Enviamos un mensaje de New Product y el producto actual
            self.send('publish_channel', {"msg": "New Product", "product": {"product_number": self.current_product.product_number,
                                                                             "product_type": self.current_product.product_type,
                                                                             "price": self.current_product.price,
                                                                             "min_price": self.current_product.min_price}
                                          , "merchant_id": None})
            
            self.start_timer()
        else:
            self.log_info("No more products available.")
            self.current_product = None

    def reduce_price(self):
        self.stop_timer()
        # If the product is not sold, reduce the price by 5 (for now, we'll change this later)
        if self.current_product:
            product_functional = self.current_product.reduce_price()
            if product_functional:
                self.log_info(f"Reducing price: {self.current_product}")
                self.send('publish_channel', {"msg": "Reducing price", "product": {
                    "product_number": product_functional.product_number,
                    "product_type": product_functional.product_type,
                    "price": product_functional.price,
                    "min_price": product_functional.min_price
                }, "merchant_id": None})
                self.start_timer()
            else:
                self.log_info(f"Product {self.current_product.product_number} reached minimum price and is unsold.")
                self.current_product = None
                self.stop_timer()

    def handle_sale(self, message):
        if self.timer:
            self.stop_timer()

        if not self.current_product:
            self.log_info(f"There is no product to sell to Merchater {message.get('merchant_id')}")
            return

        msg = message.get("msg")
        product = Product(**message.get("product"))
        
        merchant_id = message.get("merchant_id")

        if msg == "Yes":
            # Si el operador recibe una confirmación de venta, registra la venta
            self.log.append({"product number": product.product_number, 
                             "product type": product.product_type, 
                             "sell price": product.price, 
                             "merchant": merchant_id})

            self.log_info(f"Product sold: {product.product_number} to Merchant {merchant_id}")
            
            # Enviar mensaje a los comerciantes para que dejen de ofertar
            self.send('publish_channel', {"msg": "Product Sold", "product": {
                "product_number": product.product_number,
                "product_type": product.product_type,
                "price": product.price,
                "min_price": product.min_price
            }, "merchant_id": merchant_id})
            
            # Limpiar el producto actual
            self.current_product = None


    def save_logs(self):
        # Save the setup and log files when the auction is over
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with open(f"logs/log_{date_str}.csv", "w", newline="") as log_file:
            writer = csv.DictWriter(log_file, fieldnames=["product number", "product type", "sell price", "merchant"])
            writer.writeheader()
            writer.writerows(self.log)
