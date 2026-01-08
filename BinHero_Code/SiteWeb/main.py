# SiteWeb/main.py
import base64
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field # <-- Rappelle-toi, on a corrigé ça plus tôt

# Charge les clés
load_dotenv()

# --- Pas de "from main import..." ici ! ---

# 1. Définition du format de sortie
class ProductInfo(BaseModel):
    name: str = Field(description="Nom court de l'objet")
    category: str = Field(description="Catégorie (ex: Électronique, Outils, Vêtements)")
    condition: str = Field(description="État visible (Neuf, Usagé, Pour pièces)")
    estimated_price: float = Field(description="Estimation du prix en CAD")
    description: str = Field(description="Courte description technique")

# 2. Configuration du modèle
if not os.getenv("OPENAI_API_KEY"):
    print("ATTENTION: Pas de clé API trouvée dans .env")

llm = ChatOpenAI(model="gpt-4o", temperature=0)
structured_llm = llm.with_structured_output(ProductInfo)

def analyze_image_with_agent(image_path):
    print(f"Analyse de l'image : {image_path}") # Petit log pour t'aider
    
    # Encodage en base64
    try:
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print("Erreur: Image introuvable pour l'analyse")
        return None

    message = HumanMessage(
        content=[
            {"type": "text", "text": "Analyse cet objet pour l'ajouter à un inventaire de revente. Sois précis sur le prix et l'état."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
        ]
    )

    try:
        result = structured_llm.invoke([message])
        return result.dict()
    except Exception as e:
        print(f"Erreur IA : {e}")
        return None