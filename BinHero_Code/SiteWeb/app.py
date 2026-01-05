from flask import Flask, request, redirect, render_template
from main import load_products, add_product

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        add_product({
            "name": request.form["name"],
            "category": request.form["category"],
            "condition": request.form["condition"],
            "price_initial": request.form["price"],
            "stock_quantity": request.form["quantity"],
            "description": request.form["description"]
        })
        return redirect("/")

    products = load_products()
    return render_template("index.html", products=products)

app.run(host="0.0.0.0", port=5000)
