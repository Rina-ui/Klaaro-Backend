import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import io

# Chemins des modèles
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
        print("Chargement des modèles ML...")
        try:
            if Path(ISOLATION_FOREST_PATH).exists() and Path(LABEL_ENCODER_PATH).exists():
                self.isolation_forest = joblib.load(ISOLATION_FOREST_PATH)
                self.label_encoder = joblib.load(LABEL_ENCODER_PATH)
                print("Isolation Forest et Label Encoder chargés !")

            if Path(XGBOOST_PATH).exists():
                self.xgboost = joblib.load(XGBOOST_PATH)
                print("XGBoost chargé !")
        except Exception as e:
            print(f"Erreur lors du chargement des modèles : {e}")

    def validate_document_structure(self, df: pd.DataFrame) -> dict:
        if df is None or df.empty:
            return {"valid": False, "reason": "Le fichier téléchargé est vide."}

        columns = [str(col).lower().strip() for col in df.columns]

        # 1. Vérification si le document extrait est du texte brut (ex: extraction PDF non structurée)
        if "texte_brut_pdf" in columns:
            text_sample = " ".join(df["texte_brut_pdf"].iloc[:30].astype(str).tolist()).lower()
            cv_keywords = ['curriculum', 'cv', 'soutenance', 'lettre de motivation', 'competences']

            if any(word in text_sample for word in cv_keywords):
                return {
                    "valid": False,
                    "reason": "Ce document semble être un CV ou un texte rédigé. Klaaro analyse les données structurées sous forme de tableau."
                }

        # 2. Conformité standard (2 colonnes ou plus)
        if len(df.columns) >= 2:
            return {"valid": True, "reason": "Fichier conforme pour l'analyse."}

        # 3. Validation si une seule colonne est présente
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            try:
                # Essai de conversion pour vérifier si la colonne unique contient des valeurs chiffrées
                cleaned = df.iloc[:, 0].astype(str).str.replace(',', '').str.replace(' ', '')
                pd.to_numeric(cleaned)
            except Exception:
                return {
                    "valid": False,
                    "reason": "Le fichier ne contient qu'une seule colonne non numérique et ne peut pas être analysé comme un tableau."
                }

        return {"valid": True, "reason": "Fichier conforme pour l'analyse."}

    def preprocess_data(self, df: pd.DataFrame) -> dict:
        validation = self.validate_document_structure(df)
        if not validation["valid"]:
            return {"status": "rejected", "message": validation["reason"]}

        rapport = {
            "lignes_avant": len(df),
            "colonnes_avant": list(df.columns),
            "actions": []
        }

        df_clean = df.copy()

        # Standardisation des noms de colonnes (sans accents, minuscules, underscores)
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

        # Suppression des doublons stricts
        nb_doublons = df_clean.duplicated().sum()
        if nb_doublons > 0:
            df_clean = df_clean.drop_duplicates()
            rapport["actions"].append(f"{nb_doublons} lignes identiques supprimées")

        # Conversion intelligente des colonnes numériques
        for col in df_clean.columns:
            if df_clean[col].dtype == 'object':
                try:
                    cleaned_col = (
                        df_clean[col]
                        .astype(str)
                        .str.replace(',', '')
                        .str.replace(' ', '')
                        .str.strip()
                    )
                    converted = pd.to_numeric(cleaned_col, errors='coerce')

                    # Seuil de tolérance : au moins 70% de valeurs convertibles pour valider le type numérique
                    if converted.notnull().sum() / len(df_clean) > 0.7:
                        df_clean[col] = converted
                        rapport["actions"].append(f"Colonne '{col}' convertie en numérique")
                except Exception:
                    pass

        # Traitement et filtrage des dates
        for col in df_clean.columns:
            if any(k in col.lower() for k in ['date', 'mois', 'annee', 'created', 'updated']):
                try:
                    converted_dates = pd.to_datetime(df_clean[col], errors='coerce')
                    if converted_dates.notnull().sum() > 0:
                        df_clean[col] = converted_dates
                        # Exclusion des années aberrantes
                        df_clean = df_clean[
                            (df_clean[col].isnull()) |
                            ((df_clean[col].dt.year >= 1980) & (df_clean[col].dt.year <= 2100))
                            ]
                        rapport["actions"].append(f"Colonne '{col}' convertie en date avec filtrage des valeurs aberrantes")
                except Exception:
                    pass

        # Imputation des valeurs manquantes
        nb_nulls_avant = df_clean.isnull().sum().sum()
        if nb_nulls_avant > 0:
            for col in df_clean.columns:
                if df_clean[col].isnull().sum() > 0:
                    if df_clean[col].dtype in ['float64', 'int64']:
                        df_clean[col] = df_clean[col].fillna(df_clean[col].median())
                    elif isinstance(df_clean[col].dtype, pd.DatetimeTZDtype) or df_clean[col].dtype == 'datetime64[ns]':
                        df_clean[col] = df_clean[col].bfill().ffill()
                    else:
                        mode_values = df_clean[col].mode()
                        fill_val = mode_values.iloc[0] if not mode_values.empty else "Inconnu"
                        df_clean[col] = df_clean[col].fillna(fill_val)
            rapport["actions"].append(f"{nb_nulls_avant} valeurs manquantes imputées")

        # Construction des visualisations graphiques
        charts = []
        num_cols = df_clean.select_dtypes(include=['float64', 'int64']).columns.tolist()
        cat_cols = df_clean.select_dtypes(include=['object', 'string']).columns.tolist()
        date_cols = df_clean.select_dtypes(include=['datetime64[ns]']).columns.tolist()

        # Graphique 1 : Évolution Temporelle
        if len(date_cols) > 0 and len(num_cols) > 0:
            date_target = date_cols[0]
            num_target = num_cols[0]
            df_grouped = df_clean.groupby(df_clean[date_target].dt.strftime('%Y-%m-%d'))[num_target].sum().reset_index().tail(15)

            chart_data = [
                {"name": str(row[date_target]), "valeur": float(row[num_target])}
                for _, row in df_grouped.iterrows()
            ]

            if not df_grouped.empty:
                val_max = df_grouped[num_target].max()
                date_max = df_grouped.loc[df_grouped[num_target].idxmax(), date_target]
                moyenne = df_grouped[num_target].mean()
                val_min = df_grouped[num_target].min()
                volatilite = float(df_grouped[num_target].std() / moyenne * 100) if moyenne > 0 else 0

                charts.append({
                    "type": "line",
                    "title": f"Évolution de {num_target} au fil du temps",
                    "colonne_choisie": f"La colonne temporelle '{date_target}' a été sélectionnée pour structurer l'historique et croiser l'indicateur '{num_target}'.",
                    "explanation": (
                        f"L'analyse montre une valeur moyenne de {moyenne:,.2f}. "
                        f"Un pic est atteint le {date_max} avec {val_max:,.2f} unités, "
                        f"tandis que la valeur minimale descend à {val_min:,.2f}. "
                        f"La volatilité observée est de {volatilite:.1f}%."
                    ),
                    "data": chart_data
                })

        # Graphique 2 : Segmentation Catégorielle
        if len(cat_cols) > 0:
            target_col = cat_cols[0]
            counts_all = df_clean[target_col].value_counts()
            counts = counts_all.head(6)
            chart_data = [{"name": str(k), "valeur": int(v)} for k, v in counts.items()]

            total_rows = len(df_clean)
            unique_count = len(counts_all)
            top_1_name = counts.index[0] if len(counts) > 0 else "N/A"
            top_1_val = counts.iloc[0] if len(counts) > 0 else 0
            top_1_pct = (top_1_val / total_rows * 100) if total_rows > 0 else 0

            explication_col = f"La colonne '{target_col}' présente {unique_count} catégories distinctes sur {total_rows} entrées."

            if len(counts) <= 4:
                charts.append({
                    "type": "pie",
                    "title": f"Répartition de la colonne '{target_col}'",
                    "colonne_choisie": explication_col,
                    "explanation": (
                        f"La catégorie principale '{top_1_name}' représente {top_1_pct:.1f}% de la distribution totale ({top_1_val} occurrences)."
                    ),
                    "data": chart_data
                })
            else:
                top_3_pct = (counts.head(3).sum() / total_rows * 100) if total_rows > 0 else 0
                charts.append({
                    "type": "bar",
                    "title": f"Distribution de la colonne '{target_col}'",
                    "colonne_choisie": explication_col,
                    "explanation": (
                        f"Dominance du segment '{top_1_name}' ({top_1_pct:.1f}% du volume). "
                        f"Le Top 3 des catégories rassemble {top_3_pct:.1f}% des occurrences totales."
                    ),
                    "data": chart_data
                })

        # Graphique 3 : Corrélation
        if len(num_cols) >= 2:
            x_target = num_cols[0]
            y_target = num_cols[1]
            df_sampled = df_clean.head(30)
            chart_data = [
                {"name": float(row[x_target]), "valeur": float(row[y_target])}
                for _, row in df_sampled.iterrows()
            ]

            charts.append({
                "type": "scatter",
                "title": f"Corrélation entre {x_target} et {y_target}",
                "colonne_choisie": f"Analyse croisée des variables numériques '{x_target}' et '{y_target}'.",
                "explanation": (
                    f"Évaluation de l'interaction entre '{x_target}' et '{y_target}'. "
                    f"Une disposition alignée indique une relation directe, tandis qu'une dispersion traduit une indépendance des variables."
                ),
                "data": chart_data
            })

        # Préparation de l'aperçu JSON
        df_preview = df_clean.head(5).copy()
        for col in df_preview.columns:
            if df_preview[col].dtype == 'datetime64[ns]':
                df_preview[col] = df_preview[col].dt.strftime('%Y-%m-%d')
        df_preview = df_preview.replace({np.nan: None})

        rapport["colonnes_apres"] = list(df_clean.columns)
        rapport["lignes_apres"] = len(df_clean)

        return {
            "status": "success",
            "format_origine": "csv",
            "charts": charts,
            "rapport": rapport,
            "apercu_donnees": df_preview.to_dict(orient="records"),
            "data": df_clean
        }

    def detect_anomalies(self, df: pd.DataFrame) -> dict:
        if self.isolation_forest is None:
            return {"status": "fallback", "anomalies_detectees": 0, "details": []}

        try:
            num_cols = df.select_dtypes(include=['number']).columns
            if len(num_cols) == 0:
                return {"status": "success", "anomalies_detectees": 0, "details": []}

            preds = self.isolation_forest.predict(df[num_cols].fillna(0))
            anomalies_count = int((preds == -1).sum())

            return {
                "status": "success",
                "anomalies_detectees": anomalies_count,
                "details": f"{anomalies_count} lignes isolées statistiquement comme atypiques."
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def predict(self, df: pd.DataFrame, target_col: str, n_days: int) -> dict:
        try:
            if target_col not in df.columns:
                available_cols = list(df.select_dtypes(include=['number']).columns)
                if not available_cols:
                    return {"status": "error", "message": "Aucune colonne numérique exploitable."}
                target_col = available_cols[0]

            df[target_col] = pd.to_numeric(df[target_col], errors='coerce')
            df_filtered = df.dropna(subset=[target_col]).copy()

            if df_filtered.empty:
                return {"status": "error", "message": "Aucune valeur exploitable après nettoyage."}

            date_cols = df_filtered.select_dtypes(include=['datetime64[ns]']).columns.tolist()

            if len(date_cols) > 0:
                date_col = date_cols[0]
                df_sorted = df_filtered.sort_values(by=date_col)

                historique = [
                    {"date": row[date_col].strftime('%Y-%m-%d'), "valeur": float(row[target_col])}
                    for _, row in df_sorted.iterrows()
                ]

                dernieres_valeurs = df_sorted[target_col].tail(7).tolist()
                base_pred = np.mean(dernieres_valeurs) if dernieres_valeurs else 0.0
                tendance = np.mean(np.diff(dernieres_valeurs)) if len(dernieres_valeurs) > 1 else 0.0

                predictions_futures = []
                derniere_date = df_sorted[date_col].max()

                for i in range(1, n_days + 1):
                    nouvelle_date = derniere_date + pd.Timedelta(days=i)
                    valeur_predite = max(0.0, base_pred + (tendance * i) + np.random.normal(0, max(1.0, base_pred * 0.02)))
                    predictions_futures.append({
                        "date": nouvelle_date.strftime('%Y-%m-%d'),
                        "valeur": round(float(valeur_predite), 2)
                    })
            else:
                historique = [
                    {"date": f"Index {idx}", "valeur": float(val)}
                    for idx, val in enumerate(df_filtered[target_col])
                ]

                dernieres_valeurs = df_filtered[target_col].tail(7).tolist()
                base_pred = np.mean(dernieres_valeurs) if dernieres_valeurs else 0.0

                predictions_futures = []
                for i in range(1, n_days + 1):
                    valeur_predite = max(0.0, base_pred + np.random.normal(0, max(1.0, base_pred * 0.03)))
                    predictions_futures.append({
                        "date": f"Futur +{i}j",
                        "valeur": round(float(valeur_predite), 2)
                    })

            return {
                "status": "success",
                "target_column": target_col,
                "horizon_jours": n_days,
                "historique": historique[-30:],
                "predictions": predictions_futures
            }

        except Exception as e:
            return {"status": "error", "message": f"Erreur lors du calcul des prévisions : {str(e)}"}

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
            recommandations.append("Changez vos mots de passe régulièrement (tous les 3 mois)")

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
            recommandations.append("Chiffrez vos données sensibles et bases clients")
        score += points_chiffrement
        details.append({"critere": "Chiffrement", "score": points_chiffrement, "max": 20})

        # Contrôle des accès
        points_acces = 20 if reponses.get('acces_controles', False) else 0
        if points_acces == 0:
            recommandations.append("Limitez les accès selon les rôles utilisateurs")
        score += points_acces
        details.append({"critere": "Contrôle des accès", "score": points_acces, "max": 20})

        # Sauvegardes
        points_sauvegarde = 20 if reponses.get('sauvegarde_quotidienne', False) else 0
        if points_sauvegarde == 0:
            recommandations.append("Mettez en place des sauvegardes quotidiennes automatiques")
        score += points_sauvegarde
        details.append({"critere": "Sauvegarde", "score": points_sauvegarde, "max": 20})

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

    def export_processed_file(self, df: pd.DataFrame, file_format: str = "csv") -> tuple[bytes, str, str]:
        """
        Exporte le DataFrame nettoyé sous forme de buffer binaire prêt au téléchargement.
        Retourne : (buffer_bytes, media_type, file_extension)
        """
        buffer = io.BytesIO()
        file_format = file_format.lower().strip()

        if file_format in ["xlsx", "excel"]:
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Data_Cleaned")
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ext = "xlsx"

        elif file_format == "json":
            # Pour JSON, export propre avec dates au format ISO string
            json_str = df.to_json(orient="records", date_format="iso")
            buffer.write(json_str.encode("utf-8"))
            media_type = "application/json"
            ext = "json"

        else:  # Format CSV par défaut
            # Export CSV encodé en UTF-8 avec BOM pour une ouverture directe sans bug d'accents dans Excel
            csv_str = df.to_csv(index=False, encoding="utf-8-sig")
            buffer.write(csv_str.encode("utf-8-sig"))
            media_type = "text/csv"
            ext = "csv"

        buffer.seek(0)
        return buffer.getvalue(), media_type, ext


ml_service = KlaaroMLService()