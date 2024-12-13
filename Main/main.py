from osbrain import run_nameserver, run_agent
from operator import Operator
# from merchant import Merchant
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
