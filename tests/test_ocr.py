# test_ocr.py
from PIL import Image, ImageDraw, ImageFont

# Créer une fausse facture pour tester
img = Image.new('RGB', (600, 400), color='white')
draw = ImageDraw.Draw(img)

draw.text((50, 50), "FACTURE", fill='black')
draw.text((50, 100), "Date: 15/03/2024", fill='black')
draw.text((50, 150), "Produit: Riz parfume", fill='black')
draw.text((50, 200), "Quantite: 10 sacs", fill='black')
draw.text((50, 250), "Montant: 75000 FCFA", fill='black')
draw.text((50, 300), "Client: Boutique Adawlato", fill='black')

img.save('test_facture.png')
print("Image de test créée !")

# Tester l'OCR
from app.use_cases.services.ocr.ocr_service import ocr_service

result = ocr_service.extract_structured_data("test_facture.png")
print("\nTexte extrait :", result["texte_complet"])
print("Montants détectés :", result["montants_detectes"])
print("Dates détectées :", result["dates_detectees"])