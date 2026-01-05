# main.py
import base64
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

load_dotenv()  # Charger les variables d'environnement depuis le fichier .env

# 1. Définition du format de sortie (Schéma)
class ProductInfo(BaseModel):
    name: str = Field(description="Nom court de l'objet")
    category: str = Field(description="Catégorie (ex: Électronique, Outils, Vêtements)")
    condition: str = Field(description="État visible (Neuf, Usagé, Pour pièces)")
    estimated_price: float = Field(description="Estimation du prix en CAD")
    description: str = Field(description="Courte description technique")

# 2. Configuration du modèle (GPT-4o est recommandé pour la vision)
llm = ChatOpenAI(model="gpt-4o", temperature=0)
structured_llm = llm.with_structured_output(ProductInfo)

def analyze_image_with_agent(image_path):
    """
    Prend le chemin d'une image, l'analyse et retourne un dictionnaire de données.
    """
    # Encodage en base64 pour l'envoi à l'API
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    message = HumanMessage(
        content=[
            {"type": "text", "text": "Analyse cet objet pour l'ajouter à un inventaire de revente. Sois précis sur le prix et l'état."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
        ]
    )

    try:
        # L'IA analyse l'image
        result = structured_llm.invoke([message])
        # On retourne le résultat sous forme de dictionnaire (plus facile pour le CSV)
        return result.dict()
    except Exception as e:
        print(f"Erreur lors de l'analyse : {e}")
        return None