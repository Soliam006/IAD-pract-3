from osbrain import run_agent, run_nameserver, Agent
import random
import time

# Configuramos los mensajes en formato JSON
import osbrain
osbrain.config['SERIALIZER'] = 'json'

# Clase del operador
class Operator(Agent):
    def on_init(self):
        # Crear un canal de publicación
        self.bind('PUB', alias='publish_channel')
        # Estado de la subasta
        self.current_product = None
        self.min_price = 10

    def send_new_product(self):
        # Generar un nuevo producto aleatorio
        product_types = ['H', 'S', 'T']  # Hake, Sole, Tuna
        product_type = random.choice(product_types)
        self.current_product = {
            "product number": random.randint(1, 100),
            "product type": product_type,
            "price": random.randint(20, 50)
        }
        self.log_info(f"New product created: {self.current_product}")
        self.send('publish_channel', self.current_product)

    def reduce_price(self):
        if self.current_product:
            # Reducir el precio si es posible
            self.current_product["price"] -= 5
            if self.current_product["price"] >= self.min_price:
                self.log_info(f"Reducing price: {self.current_product}")
                self.send('publish_channel', self.current_product)
            else:
                self.log_info(f"Product {self.current_product} unsold. Ending auction.")
                self.current_product = None

    def handle_response(self, response):
        # Procesar la respuesta de un comerciante
        if response.get('msg') == 'Yes':
            self.log_info(f"Product sold: {self.current_product}")
            self.current_product = None

if __name__ == '__main__':
    # Inicializar el servidor de nombres
    ns = run_nameserver()

    # Crear agentes
    operator = run_agent('Operator', base=Operator)

    # Simulación de la subasta
    operator.send_new_product()

    # Simulación básica para reducir el precio
    print("Reducing price...")
    for _ in range(5):
        time.sleep(1)
        if operator.current_product:
            operator.reduce_price()

    # Finalizar el servidor de nombres
    ns.shutdown()
