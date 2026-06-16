import easyocr
import pandas as pd
import re

class OCRService:
    def __init__(self):
        print("Chargement du modèle OCR...")
        self.reader = easyocr.Reader(['fr', 'en'])
        print("OCR chargé !")

    def extract_text(self, image_path: str) -> list:
        """Extrait le texte brut depuis une image"""
        result = self.reader.readtext(image_path)
        texts = [detection[1] for detection in result]
        return texts

    def extract_structured_data(self, image_path: str) -> dict:
        """Extrait des données structurées (montants, dates) depuis une image"""
        texts = self.extract_text(image_path)
        full_text = " ".join(texts)

        # Détecter les montants (format FCFA)
        montants = re.findall(r'(\d[\d\s,\.]*\d)\s*(?:FCFA|F|CFA)', full_text)
        montants_clean = []
        for m in montants:
            try:
                montants_clean.append(float(m.replace(' ', '').replace(',', '')))
            except:
                pass

        # Détecter les dates (format JJ/MM/AAAA ou JJ-MM-AAAA)
        dates = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', full_text)

        return {
            "texte_brut": texts,
            "montants_detectes": montants_clean,
            "dates_detectees": dates,
            "texte_complet": full_text
        }

    def image_to_dataframe(self, image_path: str) -> pd.DataFrame:
        """Convertit les données extraites en DataFrame"""
        data = self.extract_structured_data(image_path)

        rows = []
        for i, montant in enumerate(data["montants_detectes"]):
            rows.append({
                "ligne": i + 1,
                "montant": montant,
                "date": data["dates_detectees"][i] if i < len(data["dates_detectees"]) else None,
                "source": "OCR"
            })

        return pd.DataFrame(rows)

ocr_service = OCRService()