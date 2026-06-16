import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# Chemins des modèles
BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
LORA_PATH = "ml/models/klaaro-tinyllama-v2"
ISOLATION_FOREST_PATH = "ml/models/isolation_forest.pkl"
XGBOOST_PATH = "ml/models/XGBoost/xgboost_generic.pkl"
LABEL_ENCODER_PATH = "ml/models/label_encoder.pkl"

class KlaaroMLService:
    def __init__(self):
        self.llm = None
        self.tokenizer = None
        self.isolation_forest = None
        self.xgboost = None
        self.label_encoder = None
        self._load_models()

    def _load_models(self):
        print("Chargement des modèles ML...")

        # Charger Isolation Forest
        self.isolation_forest = joblib.load(ISOLATION_FOREST_PATH)
        self.label_encoder = joblib.load(LABEL_ENCODER_PATH)
        print("Isolation Forest chargé !")

        # Charger XGBoost
        self.xgboost = joblib.load(XGBOOST_PATH)
        print("XGBoost chargé !")

        # Charger TinyLlama + LoRA
        self.tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            dtype=torch.float32,
            device_map="cpu",
            low_cpu_mem_usage=True
        )
        self.llm = PeftModel.from_pretrained(base_model, LORA_PATH)
        self.llm.eval()
        print("TinyLlama fine-tuné chargé !")

    def generate_explanation(self, instruction: str) -> str:
        prompt = f"<|system|>Tu es Klaaro, un assistant intelligent qui analyse les données business et explique les résultats en français simple.</s><|user|>{instruction}</s><|assistant|>"

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.llm.device)

        with torch.no_grad():
            outputs = self.llm.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.3,
                do_sample=True,
                repetition_penalty=1.3,
                pad_token_id=self.tokenizer.eos_token_id
            )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.split("<|assistant|>")[-1].strip()

    def detect_anomalies(self, df: pd.DataFrame) -> dict:
        df_encoded = df.copy()
        if 'type_transaction' in df_encoded.columns:
            df_encoded['type_transaction_encoded'] = self.label_encoder.transform(
                df_encoded['type_transaction']
            )

        features = ['montant', 'quantite', 'heure', 'type_transaction_encoded']
        X = df_encoded[features]

        predictions = self.isolation_forest.predict(X)
        anomalies = df[predictions == -1]

        return {
            "nb_anomalies": len(anomalies),
            "anomalies": anomalies.to_dict('records'),
            "is_anomalie": (predictions == -1).tolist()
        }

    def predict(self, df: pd.DataFrame, target_col: str, n_days: int = 30) -> dict:
        features = ['jour_semaine', 'mois', 'jour_mois', 'trimestre',
                    'annee', 'semaine', 'lag_1', 'lag_7', 'lag_30',
                    'moyenne_7j', 'moyenne_30j']

        last_values = df[target_col].values.tolist()
        last_date = pd.to_datetime(df['date'].iloc[-1])
        predictions = []

        for i in range(n_days):
            next_date = last_date + pd.Timedelta(days=i+1)
            features_dict = {
                'jour_semaine': next_date.dayofweek,
                'mois': next_date.month,
                'jour_mois': next_date.day,
                'trimestre': next_date.quarter,
                'annee': next_date.year,
                'semaine': next_date.isocalendar()[1],
                'lag_1': last_values[-1],
                'lag_7': last_values[-7] if len(last_values) >= 7 else last_values[0],
                'lag_30': last_values[-30] if len(last_values) >= 30 else last_values[0],
                'moyenne_7j': np.mean(last_values[-7:]),
                'moyenne_30j': np.mean(last_values[-30:])
            }
            X_pred = pd.DataFrame([features_dict])
            pred = float(self.xgboost.predict(X_pred)[0])
            predictions.append({'date': str(next_date.date()), target_col: pred})
            last_values.append(pred)

        return {"predictions": predictions}

# pretraitement
def preprocess_data(self, df: pd.DataFrame) -> dict:
    rapport = {
        "lignes_avant": len(df),
        "colonnes_avant": list(df.columns),
        "actions": []
    }

    df_clean = df.copy()

    # Standardiser les noms de colonnes
    df_clean.columns = (
        df_clean.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_')
        .str.normalize('NFKD')
        .str.encode('ascii', errors='ignore')
        .str.decode('utf-8')
    )
    rapport["actions"].append("Noms de colonnes standardisés")

    # Supprimer les doublons
    nb_doublons = df_clean.duplicated().sum()
    if nb_doublons > 0:
        df_clean = df_clean.drop_duplicates()
        rapport["actions"].append(f"{nb_doublons} doublons supprimés")

    # Détecter et convertir les colonnes de dates
    for col in df_clean.columns:
        if 'date' in col.lower():
            try:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                rapport["actions"].append(f"Colonne '{col}' convertie en date")
            except:
                pass

    # Gérer les valeurs manquantes
    nb_nulls_avant = df_clean.isnull().sum().sum()
    if nb_nulls_avant > 0:
        for col in df_clean.columns:
            if df_clean[col].dtype in ['float64', 'int64']:
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
            else:
                df_clean[col] = df_clean[col].fillna(df_clean[col].mode()[0] if not df_clean[col].mode().empty else "Inconnu")
        rapport["actions"].append(f"{nb_nulls_avant} valeurs manquantes corrigées")

    # Détecter automatiquement les colonnes numériques mal typées
    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':
            try:
                df_clean[col] = pd.to_numeric(df_clean[col].str.replace(',', '').str.replace(' ', ''))
                rapport["actions"].append(f"Colonne '{col}' convertie en numérique")
            except:
                pass

    rapport["lignes_apres"] = len(df_clean)
    rapport["colonnes_apres"] = list(df_clean.columns)

    return {
        "rapport": rapport,
        "data": df_clean
    }
# Instance singleton
ml_service = KlaaroMLService()