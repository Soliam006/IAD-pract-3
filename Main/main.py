from osbrain import run_nameserver, run_agent
from operator import Operator
from merchant import Merchant
import time

def main():
    # Configuración inicial
    num_merchants = 3  # Número de comerciantes
    num_fishes = 5     # Número de productos
    preference_type = 'R'  # Preferencias de los comerciantes ('R' o 'NR')

    # Inicializar servidor de nombres
    ns = run_nameserver()

    # Crear y configurar el operador
    operator = run_agent('Operator', base=Operator)
    operator.setup_products(num_fishes)

    # Crear y configurar comerciantes
    merchants = []
    for i in range(1, num_merchants + 1):
        merchant = run_agent(f'Merchant-{i}', base=Merchant)
        merchant.setup_preferences(preference_type, probabilities=[0.5, 0.3, 0.2])
        merchant.connect(operator.addr('publish_channel'), handler='on_new_product')
        merchant.bind('PUSH', alias='response_channel')
        merchants.append(merchant)

    # Simulación de la subasta
    while operator.products or operator.current_product:
        if not operator.current_product:
            operator.send_new_product()
        else:
            time.sleep(1)  # Simular tiempo entre reducciones de precio
            operator.reduce_price()

    # Guardar logs
    operator.save_logs()

    # Finalizar servidor de nombres
    ns.shutdown()

if __name__ == '__main__':
    main()
