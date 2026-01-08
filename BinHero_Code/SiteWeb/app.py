import os
import csv
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from main import analyze_image_with_agent

app = Flask(__name__)

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
DB_FILE = os.path.join(BASE_DIR, 'products.csv')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- FONCTIONS UTILITAIRES ---
def get_next_id():
    if not os.path.isfile(DB_FILE):
        return 1
    try:
        with open(DB_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None or 'id' not in reader.fieldnames:
                return 1
            ids = [int(row['id']) for row in reader if row.get('id') and row['id'].isdigit()]
            return max(ids) + 1 if ids else 1
    except:
        return 1

def save_to_csv(data_dict):
    """Sauvegarde finale dans le CSV"""
    fieldnames = ['id', 'name', 'category', 'condition', 'price_initial', 'stock_quantity', 'description', 'image_filename']
    file_exists = os.path.isfile(DB_FILE)
    
    with open(DB_FILE, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        
        # On force l'ajout des champs manquants si nécessaire
        data_dict.setdefault('stock_quantity', 1)
        
        # On filtre pour ne garder que les colonnes qu'on veut (sécurité)
        row_to_save = {key: data_dict.get(key) for key in fieldnames}
        writer.writerow(row_to_save)

def get_products():
    products = []
    if os.path.isfile(DB_FILE):
        with open(DB_FILE, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                products.append(row)
    return products[::-1]

# --- ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def index():
    # Cettte route gère maintenant L'UPLOAD seulement (pas la sauvegarde)
    if request.method == 'POST':
        if 'photo' not in request.files: return 'Aucun fichier'
        file = request.files['photo']
        if file.filename == '': return 'Pas de fichier'

        if file:
            # 1. Sauvegarde Image
            _, ext = os.path.splitext(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = uuid.uuid4().hex[:8]
            new_filename = f"img_{timestamp}_{unique_id}{ext}"
            
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            file.save(save_path)
            
            # 2. Analyse IA
            print(f"Analyse de {new_filename}...")
            product_data = analyze_image_with_agent(save_path)

            if product_data:
                # 3. AU LIEU DE SAUVEGARDER -> ON ENVOIE VERS LA PAGE DE VALIDATION
                # On passe les données de l'IA et le nom de l'image au template HTML
                return render_template('review.html', product=product_data, image_filename=new_filename)
            else:
                return "Erreur lors de l'analyse IA."

    products_list = get_products()
    return render_template('index.html', products=products_list)

@app.route('/confirm', methods=['POST'])
def confirm_add():
    # Cette nouvelle route reçoit le formulaire validé par l'utilisateur
    
    # 1. On récupère les données du formulaire sous forme de dictionnaire
    data = request.form.to_dict()
    
    # 2. On ajoute l'ID automatique
    data['id'] = get_next_id()
    
    # 3. On sauvegarde pour de vrai
    save_to_csv(data)
    
    print(f"Produit confirmé et ajouté : {data['name']}")
    
    # 4. Retour à l'accueil
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')