from osbrain import run_nameserver, run_agent
from operator_code import Operator
from merchant_code import Merchant
from datetime import datetime
import csv

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
    """
    for i in range(1, num_merchants + 1):
        merchant_name = f'Merchant-{i}'
        merchant = run_agent(merchant_name, base=Merchant)
        merchant.setup_preferences(preference_type, probabilities=[0.5, 0.3, 0.2])
        merchant.connect(operator.addr('publish_channel'), handler='on_new_product')
        merchant.bind('PUSH', alias='response_channel_' + str(i))
        operator.connect(merchant.addr('response_channel_' + str(i)), handler='handle_sale')"""

    # Save the setup and log files when the auction is over
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"setups/setup_{date_str}.csv", "w", newline="") as setup_file:
        writer = csv.DictWriter(setup_file, fieldnames=["Merchant", "Preference", "Budget"])
        writer.writeheader()

        for i in range(1, num_merchants + 1):
            merchant_name = f'Merchant-{i}'
            merchant = run_agent(merchant_name, base=Merchant)
            merchant.setup_preferences(preference_type, probabilities=[0.5, 0.3, 0.2])
            merchant.connect(operator.addr('publish_channel'), handler='on_new_product')
            merchant.bind('PUSH', alias='response_channel_' + str(i))
            operator.connect(merchant.addr('response_channel_' + str(i)), handler='handle_sale')
            
            preference = merchant.get_preference()
            budget = merchant.get_budget()
            writer.writerow({"Merchant": merchant_name, "Preference": preference, "Budget": budget})

    while operator.get_products() or operator.get_current_product():
        
        if not operator.get_current_product():
            operator.send_new_product()

    # Guardar logs
    operator.save_logs()

    # Finalizar servidor de nombres
    ns.shutdown()

if __name__ == '__main__':
    main()
