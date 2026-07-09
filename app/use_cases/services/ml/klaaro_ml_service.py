import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# Chemins des modèles légers
ISOLATION_FOREST_PATH = "ml/models/isolation_forest.pkl"
XGBOOST_PATH = "ml/models/XGBoost/xgboost_generic.pkl"
LABEL_ENCODER_PATH = "ml/models/label_encoder.pkl"

class KlaaroMLService:
    def __init__(self):
        self.isolation_forest = None
        self.xgboost = None
        self.label_encoder = None
        self._load_models()

    def _load_models(self):
        print("Chargement des modèles ML légers...")
        try:
            # Charger Isolation Forest
            if Path(ISOLATION_FOREST_PATH).exists():
                self.isolation_forest = joblib.load(ISOLATION_FOREST_PATH)
                self.label_encoder = joblib.load(LABEL_ENCODER_PATH)
                print("Isolation Forest et Label Encoder chargés !")

            # Charger XGBoost
            if Path(XGBOOST_PATH).exists():
                self.xgboost = joblib.load(XGBOOST_PATH)
                print("XGBoost chargé !")
        except Exception as e:
            print(f"Erreur lors du chargement des modèles : {e}")

    def validate_document_structure(self, df: pd.DataFrame) -> dict:
        """
        Vrifie si le document est un fichier business ou un texte hors-sujet (CV, mmoire).
        """
        columns = [str(col).lower().strip() for col in df.columns]

        # Si c'est un PDF converti textuellement ou un tableau suspect à une seule colonne
        if "texte_brut_pdf" in columns or (len(df.columns) <= 2 and df.dtypes.iloc[0] == 'object'):
            target_col = "texte_brut_pdf" if "texte_brut_pdf" in columns else df.columns[0]
            text_sample = " ".join(df[target_col].iloc[:30].astype(str).tolist()).lower()

            cv_keywords = ['curriculum', 'cv', 'stage', 'competences', 'formation', 'memoire', 'these', 'introduction', 'soutenance']
            if any(word in text_sample for word in cv_keywords):
                return {
                    "valid": False,
                    "reason": "Ce document ressemble à un CV, un rapport ou un mémoire. Klaaro n'analyse que les données tabulaires d'entreprise (ventes, stocks, finances)."
                }

        # 2. On vérifie s'il y a au moins une colonne business essentielle
        business_keywords = ['date', 'montant', 'prix', 'quantite', 'total', 'vente', 'article', 'client', 'ca', 'revenue']
        has_business_col = any(any(key in col for key in business_keywords) for col in columns)

        # 3. On regarde s'il y a des colonnes numériques
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

        if len(numeric_cols) == 0 and not has_business_col:
            return {
                "valid": False,
                "reason": "Format non supporté. Le fichier ne contient aucune donnée financière ou quantitative exploitable."
            }

        return {"valid": True, "reason": "Fichier conforme pour l'analyse."}

    def preprocess_data(self, df: pd.DataFrame) -> dict:
        """ Nettoie le dataset et prépare les métriques pour les barplots du front """
        # D'abord, on valide le document !
        validation = self.validate_document_structure(df)
        if not validation["valid"]:
            return {
                "status": "rejected",
                "message": validation["reason"]
            }

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

        #  Extraction automatique des données pour les BARPLOTS du Frontend
        chart_data = []
        cat_cols = df_clean.select_dtypes(include=['object']).columns
        if len(cat_cols) > 0:
            # On prend la première colonne catégorielle textuelle (ex: type_transaction, region, article)
            target_col = cat_cols[0]
            counts = df_clean[target_col].value_counts().head(5)
            chart_data = [{"name": str(k), "valeur": int(v)} for k, v in counts.items()]

        return {
            "status": "success",
            "rapport": rapport,
            "chart_data": chart_data,  # Directement utilisable par Recharts / Chart.js
            "data": df_clean
        }

    def detect_anomalies(self, df: pd.DataFrame) -> dict:
        if self.isolation_forest is None:
            return {"nb_anomalies": 0, "anomalies": [], "message": "Modèle Isolation Forest non disponible."}

        df_encoded = df.copy()
        if 'type_transaction' in df_encoded.columns and self.label_encoder:
            df_encoded['type_transaction_encoded'] = self.label_encoder.transform(
                df_encoded['type_transaction']
            )

        features = ['montant', 'quantite', 'heure', 'type_transaction_encoded']
        # Sécurité : on garde uniquement les features disponibles dans le tableau actuel
        available_features = [f for f in features if f in df_encoded.columns]

        if len(available_features) < 2:
            return {"nb_anomalies": 0, "anomalies": [], "message": "Colonnes insuffisantes pour exécuter l'Isolation Forest."}

        X = df_encoded[available_features]
        predictions = self.isolation_forest.predict(X)
        anomalies = df[predictions == -1]

        return {
            "nb_anomalies": len(anomalies),
            "anomalies": anomalies.to_dict('records')[:10],  # On limite à 10 pour l'affichage front
            "is_anomalie": (predictions == -1).tolist()
        }

    def predict(self, df: pd.DataFrame, target_col: str, n_days: int = 30) -> dict:
        if self.xgboost is None:
            return {"predictions": [], "message": "Modèle XGBoost non disponible."}

        features = ['jour_semaine', 'mois', 'jour_mois', 'trimestre',
                    'annee', 'semaine', 'lag_1', 'lag_7', 'lag_30',
                    'moyenne_7j', 'moyenne_30j']

        if target_col not in df.columns or 'date' not in df.columns:
            return {"predictions": [], "message": f"La colonne cible '{target_col}' ou la colonne 'date' est manquante."}

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

    def calculate_security_score(self, reponses: dict) -> dict:
        score = 0
        details = []
        recommandations = []

        # Mots de passe
        points_mdp = 0
        if reponses.get('mot_de_passe_force', False):
            points_mdp += 10
        else:
            recommandations.append("Utilisez des mots de passe complexes d'au moins 12 caractères")
        if reponses.get('mot_de_passe_recent', False):
            points_mdp += 10
        else:
            recommandations.append("Changez vos mots de passe régulièrement, au moins tous les 3 mois")
        score += points_mdp
        details.append({"critere": "Mots de passe", "score": points_mdp, "max": 20})

        # Mises à jour
        points_maj = 20 if reponses.get('mises_a_jour_actives', False) else 0
        if points_maj == 0:
            recommandations.append("Activez les mises à jour automatiques sur tous vos systèmes")
        score += points_maj
        details.append({"critere": "Mises à jour", "score": points_maj, "max": 20})

        # Chiffrement
        points_chiffrement = 20 if reponses.get('donnees_chiffrees', False) else 0
        if points_chiffrement == 0:
            recommandations.append("Chiffrez vos données sensibles, notamment les informations clients")
        score += points_chiffrement
        details.append({"critere": "Chiffrement", "score": points_chiffrement, "max": 20})

        # Accès
        points_acces = 20 if reponses.get('acces_controles', False) else 0
        if points_acces == 0:
            recommandations.append("Limitez les accès selon les rôles, ne partagez jamais un compte entre plusieurs employés")
        score += points_acces
        details.append({"critere": "Contrôle des accès", "score": points_acces, "max": 20})

        # Sauvegarde
        points_sauvegarde = 20 if reponses.get('sauvegarde_quotidienne', False) else 0
        if points_sauvegarde == 0:
            recommandations.append("Mettez en place des sauvegardes quotidiennes automatiques de vos données")
        score += points_sauvegarde
        details.append({"critere": "Sauvegarde", "score": points_sauvegarde, "max": 20})

        # Niveau global
        if score >= 80:
            niveau = "Sécurisé"
        elif score >= 50:
            niveau = "Moyennement sécurisé"
        else:
            niveau = "Vulnérable"

        return {
            "score_total": score,
            "niveau": niveau,
            "details": details,
            "recommandations": recommandations
        }

# Instance singleton accessible partout
ml_service = KlaaroMLService()