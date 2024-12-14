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

    # I will keep the merchants
    merchants = []

    # Save the setup and log files when the auction is over
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"setups/setup_{date_str}.csv", "w", newline="") as setup_file:
        writer = csv.DictWriter(setup_file, fieldnames=["Merchant", "Preference", "Initial Budget", "Final Budget"])
        writer.writeheader()

        for i in range(1, num_merchants + 1):
            # Crear y configurar comerciantes
            merchant_name = f'Merchant-{i}'
            merchant = run_agent(merchant_name, base=Merchant)
            merchant.setup_preferences(preference_type, probabilities=[0.5, 0.3, 0.2])
            merchant.connect(operator.addr('publish_channel'), handler='on_new_product')
            merchant.bind('PUSH', alias='response_channel_' + str(i))
            merchants.append(merchant)

            operator.connect(merchant.addr('response_channel_' + str(i)), handler='handle_sale')
            
            preference = merchant.get_preference()
            budget = merchant.get_budget()
            writer.writerow({"Merchant": merchant_name, "Preference": preference, "Initial Budget": budget, "Final Budget": ""})

    while operator.get_products() or operator.get_current_product():

        if not operator.get_current_product():
            # First, we need to find if a Merchant have a budget
            operator.send_new_product()
        
        # Check if any merchant has a budget above the minimum price of the current product
        min_price = operator.get_min_price_product()
        active_merchants = [merchant for merchant in merchants if merchant.get_budget() >= min_price]

        if not active_merchants:
            operator.log_infos("All merchants have budgets below the minimum price of the products.")
            operator.send_new_product()

    # After the auction is over, update the final budgets
    with open(f"setups/setup_{date_str}.csv", "r") as setup_file:
        reader = list(csv.DictReader(setup_file))

    with open(f"setups/setup_{date_str}.csv", "w", newline="") as setup_file:
        writer = csv.DictWriter(setup_file, fieldnames=["Merchant", "Preference", "Initial Budget", "Final Budget"])
        writer.writeheader()

        for row in reader:
            merchant_name = row["Merchant"]
            merchant = next((m for m in merchants if m.get_name() == merchant_name), None)
            if merchant:
                row["Final Budget"] = merchant.get_budget()
            writer.writerow(row)
            
    # Guardar logs
    operator.save_logs()

    # Finalizar servidor de nombres
    ns.shutdown()

if __name__ == '__main__':
    main()
