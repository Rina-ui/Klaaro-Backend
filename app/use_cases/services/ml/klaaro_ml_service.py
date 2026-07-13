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
        Vérifie si le document est un tableau de données valide ou un texte hors-sujet (CV, mémoire).
        Accepte tout type de données tabulaires.
        """
        if df.empty:
            return {
                "valid": False,
                "reason": "Le fichier téléchargé est vide."
            }

        columns = [str(col).lower().strip() for col in df.columns]

        # 1. Protection contre les documents textuels (CV, Mémoires, Lettres)
        # Si c'est un PDF converti en texte brut ou un tableau suspect à colonne unique textuelle
        if "texte_brut_pdf" in columns or len(df.columns) == 1:
            target_col = "texte_brut_pdf" if "texte_brut_pdf" in columns else df.columns[0]
            text_sample = " ".join(df[target_col].iloc[:30].astype(str).tolist()).lower()

            cv_keywords = ['curriculum', 'cv', 'stage', 'competences', 'formation', 'memoire', 'these', 'introduction', 'soutenance']
            if any(word in text_sample for word in cv_keywords):
                return {
                    "valid": False,
                    "reason": "Ce document ressemble à un CV, un rapport ou un mémoire. Klaaro n'analyse que les données sous forme de tableau."
                }

        # 2. Validation de la structure tabulaire
        # Si le fichier a au moins 2 colonnes, c'est un tableau de données (RH, Logistique, Inventaire, etc.), on valide !
        if len(df.columns) >= 2:
            return {"valid": True, "reason": "Fichier conforme pour l'analyse."}

        # 3. Sécurité pour les fichiers à colonne unique qui ne sont pas des CV mais qui n'ont rien d'exploitable
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            return {
                "valid": False,
                "reason": "Le fichier ne contient qu'une seule colonne de texte brut et ne peut pas être analysé comme un tableau."
            }

        return {"valid": True, "reason": "Fichier conforme pour l'analyse."}

    def preprocess_data(self, df: pd.DataFrame) -> dict:
        """ Nettoie le dataset et choisit le type de graphique adapté selon la nature des données """
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
            if 'date' in col.lower() or 'mois' in col.lower() or 'annee' in col.lower():
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
                    # Enlever les espaces et les virgules pour forcer la conversion
                    cleaned_col = df_clean[col].astype(str).str.replace(',', '').str.replace(' ', '')
                    df_clean[col] = pd.to_numeric(cleaned_col)
                    rapport["actions"].append(f"Colonne '{col}' convertie en numérique")
                except:
                    pass

        rapport["lignes_apres"] = len(df_clean)
        rapport["colonnes_apres"] = list(df_clean.columns)

        # SÉLECTION DYNAMIQUE ET ADAPTATIVE DU GRAPHISME
        chart_data = []
        chart_type = "bar" # Type par défaut

        num_cols = df_clean.select_dtypes(include=['float64', 'int64']).columns.tolist()
        cat_cols = df_clean.select_dtypes(include=['object', 'string']).columns.tolist()
        date_cols = df_clean.select_dtypes(include=['datetime64[ns]']).columns.tolist()

        # Scénario 1 : Série Temporelle / Évolution -> LINE CHART
        if len(date_cols) > 0 and len(num_cols) > 0:
            chart_type = "line"
            date_target = date_cols[0]
            num_target = num_cols[0]

            # Agrégation par jour ou par mois pour éviter la surcharge visuelle
            df_grouped = df_clean.groupby(df_clean[date_target].dt.date)[num_target].sum().reset_index().tail(15)
            chart_data = [
                {"name": str(row[date_target]), "valeur": float(row[num_target])}
                for _, row in df_grouped.iterrows()
            ]

        # Scénario 2 : Deux variables numériques / Corrélations -> SCATTER CHART
        elif len(num_cols) >= 2:
            chart_type = "scatter"
            x_target = num_cols[0]
            y_target = num_cols[1]

            # Échantillonnage à 30 points max pour la clarté du nuage
            df_sampled = df_clean.head(30)
            chart_data = [
                {"name": str(row[x_target]), "valeur": float(row[y_target])}
                for _, row in df_sampled.iterrows()
            ]

        # Scénario 3 : Répartition de parts / Faible cardinalité -> PIE CHART
        elif len(cat_cols) > 0 and df_clean[cat_cols[0]].nunique() <= 4:
            chart_type = "pie"
            target_col = cat_cols[0]
            counts = df_clean[target_col].value_counts()
            chart_data = [{"name": str(k), "valeur": int(v)} for k, v in counts.items()]

        # Scénario 4 : Comptage par défaut / Cardinalités moyennes -> BAR CHART
        elif len(cat_cols) > 0:
            chart_type = "bar"
            target_col = cat_cols[0]
            counts = df_clean[target_col].value_counts().head(6)
            chart_data = [{"name": str(k), "valeur": int(v)} for k, v in counts.items()]

        # Secours : Si tout est numérique sans axe temporel, faire un histogramme en barres
        elif len(num_cols) > 0:
            chart_type = "bar"
            target_col = num_cols[0]
            counts = df_clean[target_col].value_counts().head(6)
            chart_data = [{"name": f"Val: {k}", "valeur": int(v)} for k, v in counts.items()]

        return {
            "status": "success",
            "format_origine": "csv",
            "chart_type": chart_type,
            "chart_data": chart_data,
            "rapport": rapport,
            "apercu_donnees": df_clean.head(5).to_dict(orient="records")
        }

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