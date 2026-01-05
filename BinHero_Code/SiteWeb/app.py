# app.py
import os
import csv
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from main import analyze_image_with_agent # On importe notre fonction IA

app = Flask(__name__)
# On sauvegarde directement dans le dossier static pour que le HTML puisse lire les images
UPLOAD_FOLDER = 'static/uploads' 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DB_FILE = 'products.csv'

# Fonction pour lire le CSV et récupérer les produits
def get_products():
    products = []
    if os.path.isfile(DB_FILE):
        with open(DB_FILE, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                products.append(row)
    # On inverse la liste pour voir les derniers ajouts en premier
    return products[::-1] 

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'photo' not in request.files:
            return 'Aucun fichier'
        file = request.files['photo']
        if file.filename == '':
            return 'Aucun fichier'

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Analyse IA
            product_data = analyze_image_with_agent(filepath)

            if product_data:
                # IMPORTANT : On ajoute le nom du fichier image aux données
                product_data['image_filename'] = filename 
                
                # Sauvegarde CSV
                save_to_csv(product_data)
                
    # GET request : On affiche la page avec les produits
    products_list = get_products()
    return render_template('index.html', products=products_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') # host='0.0.0.0' permet l'accès depuis ton téléphone sur le même wifi