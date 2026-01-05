import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "products.csv")

FIELDS = [
    "id", "name", "category", "condition",
    "price_initial", "day_in_stock",
    "stock_quantity", "description"
]

def load_products():
    """Charge tous les produits depuis le CSV"""
    products = []
    if not os.path.exists(CSV_PATH):
        # Crée le CSV si inexistant
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append(row)
    return products

def add_product(data):
    """Ajoute un produit au CSV"""
    products = load_products()
    new_id = len(products) + 1
    data["id"] = new_id
    if "day_in_stock" not in data:
        data["day_in_stock"] = 1

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writerow(data)
