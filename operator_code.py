import csv
from datetime import datetime
from osbrain import Agent
import random
from product import Product

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
        self.min_price = 4  # Precio mínimo para vender un producto
        self.log = []       # Registro de ventas

    def get_products(self):
        return self.products
    
    def get_current_product(self):
        return self.current_product
    
    def setup_products(self, num_products):
        # Product List with random prices within (20, 50)
        product_types = ['H', 'S', 'T']  # Hake, Sole, Tuna
        for i in range(1, num_products + 1):
            product = Product(i, random.choice(product_types), random.randint(20, 50), self.min_price)
            self.products.append(product)
        
    def send_new_product(self):
        # Send a new product to the merchants subscribed
        if self.products:
            self.current_product = self.products.pop(0)
            self.log_info(f"New product: {self.current_product}")
            # Enviamos un mensaje de New Product y el producto actual
            self.send('publish_channel', {"msg": "New Product", "product": self.current_product, "merchant_id": None})
        else:
            self.log_info("No more products available.")
            self.current_product = None

    def reduce_price(self):
        # If the product is not sold, reduce the price by 5 (for now, we'll change this later)
        if self.current_product:
            product_functional = self.current_product.reduce_price()
            if product_functional:
                self.log_info(f"Reducing price: {self.current_product}")
                self.send('publish_channel', {"msg": "Price Reduced", "product": self.current_product, "merchant_id": None})
            else:
                self.log_info(f"Product {self.current_product.product_number} reached minimum price and is unsold.")
                self.current_product = None

    def handle_sale(self, message):
        msg = message.get("msg")
        product = message.get("product")
        merchant_id = message.get("merchant_id")

        if msg == "Yes":
            # Si el operador recibe una confirmación de venta, registra la venta
            self.log.append({"product number": product.product_number, "product type": product.product_type, "sell price": product.price, "merchant": merchant_id})

            self.log_info(f"Product sold: {product.product_number} to Merchant {merchant_id}")
            
            # Enviar mensaje a los comerciantes para que dejen de ofertar
            self.send(f'publish_channel', {"msg": "Product Sold", "product": product, "merchant_id": merchant_id})
            
            # Limpiar el producto actual
            self.current_product = None


    def save_logs(self):
        # Save the setup and log files when the auction is over
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"setup_{date_str}.csv", "w", newline="") as setup_file:
            writer = csv.DictWriter(setup_file, fieldnames=["product number", "product type", "price", "min_price"])
            writer.writeheader()
            writer.writerows(self.products)
        
        with open(f"log_{date_str}.csv", "w", newline="") as log_file:
            writer = csv.DictWriter(log_file, fieldnames=["product number", "product type", "sell price", "merchant"])
            writer.writeheader()
            writer.writerows(self.log)