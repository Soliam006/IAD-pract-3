import random
import csv
from datetime import datetime
from osbrain import Agent

# Configuramos los mensajes en formato JSON
import osbrain
osbrain.config['SERIALIZER'] = 'json'

class Operator(Agent):
    def on_init(self):
        # Crear un canal de publicación
        self.bind('PUB', alias='publish_channel')
        
        # Parámetros de la subasta
        self.products = []
        self.current_product = None
        self.min_price = 10  # Precio mínimo para vender un producto
        self.log = []        # Registro de ventas

    def setup_products(self, num_products):
        """Configurar una lista de productos con precios iniciales y tipos."""
        product_types = ['H', 'S', 'T']  # Hake, Sole, Tuna
        for i in range(1, num_products + 1):
            product = {
                "product number": i,
                "product type": random.choice(product_types),
                "price": random.randint(20, 50),
                "min_price": self.min_price
            }
            self.products.append(product)
        
    def send_new_product(self):
        """Enviar un nuevo producto a los comerciantes."""
        if self.products:
            self.current_product = self.products.pop(0)
            self.log_info(f"New product: {self.current_product}")
            self.send('publish_channel', self.current_product)
        else:
            self.log_info("No more products available.")
            self.current_product = None

    def reduce_price(self):
        """Reducir el precio del producto actual si es posible."""
        if self.current_product:
            self.current_product["price"] -= 5
            if self.current_product["price"] >= self.current_product["min_price"]:
                self.log_info(f"Reducing price: {self.current_product}")
                self.send('publish_channel', self.current_product)
            else:
                self.log_info(f"Product {self.current_product} reached minimum price and is unsold.")
                self.current_product = None

    def handle_sale(self, product, merchant_id):
        """Registrar una venta en el log."""
        self.log.append({
            "product number": product["product number"],
            "product type": product["product type"],
            "sell price": product["price"],
            "merchant": merchant_id
        })
        self.log_info(f"Product sold: {product} to Merchant {merchant_id}")
        self.current_product = None

    def save_logs(self):
        """Guardar el registro y la configuración en archivos CSV."""
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"setup_{date_str}.csv", "w", newline="") as setup_file:
            writer = csv.DictWriter(setup_file, fieldnames=["product number", "product type", "price", "min_price"])
            writer.writeheader()
            writer.writerows(self.products)
        
        with open(f"log_{date_str}.csv", "w", newline="") as log_file:
            writer = csv.DictWriter(log_file, fieldnames=["product number", "product type", "sell price", "merchant"])
            writer.writeheader()
            writer.writerows(self.log)
