from osbrain import run_nameserver, run_agent
from operator_code import Operator
from merchant_code import Merchant
import time

def main():
    # Configuración inicial
    num_merchants = int(input("Number of Merchants: "))
    num_fishes = int(input("Number of Fishes: "))
    preference_type =""

    while preference_type not in ["R", "NR"]:
        preference_type = input("Preference type Algorithm (R or NR): ")
        if preference_type not in ["R", "NR"]:
            print("Invalid preference type, please enter R or NR")

    # Inicializar servidor de nombres
    ns = run_nameserver()

    # Crear y configurar el operador
    operator = run_agent('Operator', base=Operator)
    operator.setup_products(num_fishes)

    # Crear y configurar comerciantes
    for i in range(1, num_merchants + 1):
        merchant_name = f'Merchant-{i}'
        merchant = run_agent(merchant_name, base=Merchant)
        merchant.setup_preferences(preference_type, probabilities=[0.5, 0.3, 0.2])
        merchant.connect(operator.addr('publish_channel'), handler='on_new_product')

    # Simulación de la subasta
    while operator.get_products() or operator.get_current_product():
        if not operator.get_current_product():
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
