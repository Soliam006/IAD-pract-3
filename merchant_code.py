from osbrain import Agent
import random
from product import Product

class Merchant(Agent):
    def on_init(self):
        # Configuración inicial del comerciante
        self.budget = 100
        self.preference = None
        self.fishes_owned = {"H": 0, "S": 0, "T": 0}  # Pescados adquiridos por tipo

    def get_budget(self):
        return self.budget
    
    def get_preference(self):
        return self.preference

    def setup_preferences(self, preference_type, probabilities=None):
        # Set up the merchant's preferences
        if preference_type == 'R':
            self.preference = random.choice(["H", "S", "T"])
        elif preference_type == 'NR' and probabilities:
            self.preference = random.choices(["H", "S", "T"], probabilities)[0]
        else:
            self.preference = "H"  # Default preference
        
        self.log_info(f"Preference set to: {self.preference}")

    def on_new_product(self, message):
        # Extraer msg y product del diccionario
        msg = message.get("msg")
        prod_msg = message.get("product")
        product = Product(prod_msg.get("product_number"), prod_msg.get("product_type"),
                          prod_msg.get("price"), prod_msg.get("min_price"))
        merchan_id = message.get("merchant_id")

        if merchan_id != None and merchan_id == self.name.split("-")[1]:
            self.log_info(f"I bought this product: {product.product_number}")
            self.budget -= product.price
            self.fishes_owned[product.product_type] += 1
            return # No comprar el producto que ya se ha comprado
        
        if msg == "Product Sold":
            self.log_info(f"I can't buy this product: {product.product_number} - Merchant {merchan_id} bought it")
            return
        
        # When the merchant receives a new product, decide whether to buy it
        self.log_info(f"Received product: {product.product_number} - {product.product_type} - {product.price} - {product.min_price}")

        # Decidir si comprar
        if self.budget >= product.price:
            if product.product_type == self.preference or self.fishes_owned[product.product_type] == 0:
                self.buy_product(product)
            elif self.fishes_owned[product.product_type] == 0:  # Necesita al menos uno de cada tipo
                self.buy_product(product)
                

    def buy_product(self, product: Product):
        # Buy the product and send a confirmation to the operator
        self.log_info(f"I want buy this product: {product}")

        # Enviar mensaje de confirmación al operador
        # Para ello utilizo el nombre del Mercante y su numero de identificación
        merchant_id = self.name.split("-")[1]
        self.send(self.addr('response_channel_' + merchant_id), {"msg": "Yes", "product": {
            "product_number": product.product_number,
            "product_type": product.product_type,
            "price": product.price,
            "min_price": product.min_price
        }, "merchant_id": self.name.split("-")[1]})
