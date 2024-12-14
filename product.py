# Product interface:
import random 

class Product:
    def __init__(self, product_number, product_type, price, min_price):
        self.product_number = product_number
        self.product_type = product_type
        self.price = price
        self.min_price = min_price

    def __str__(self):
        return f"Product {self.product_number}: {self.product_type} - Price: {self.price} - Min Price: {self.min_price}"

    def reduce_price(self):
        # If the product is not sold, reduce the price randomly (for now, we'll change this later)
        self.price = round(self.price - random.uniform(1, 4), 2)
        if self.price >= self.min_price:
            return self
        else:
            return None