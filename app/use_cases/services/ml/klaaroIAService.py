import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

class KlaaroAIService:
    def __init__(self, base_model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0", adapter_path: str = "ml/models/klaaro-tinyllama-v2"):
        print("Chargement du Tokenizer et du modèle TinyLlama...")

        # Chargement sécurisé du Tokenizer à partir du modèle de base
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)

        # Détection automatique de l'appareil (GPU CUDA ou CPU)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        print(f"Modèle chargé sur : {device.upper()} avec la précision : {dtype}")

        # Chargement du modèle de base
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=dtype,
            device_map="auto"
        )

        # Fusion/chargement de l'adaptateur LoRA entraîné
        print(f"Application de l'adaptateur LoRA depuis {adapter_path}...")
        try:
            self.model = PeftModel.from_pretrained(base_model, adapter_path)
            self.model.eval()
            print("Modèle Klaaro TinyLlama chargé avec succès et prêt pour l'inférence !")
        except Exception as e:
            print(f"Attention: Impossible de charger l'adaptateur LoRA ({e}). Utilisation du modèle de base.")
            self.model = base_model
            self.model.eval()

    def generate_decision_and_explanation(self, query_content: str, report_content: str) -> dict:
        """
        Prend le rapport et la requête utilisateur, puis demande à TinyLlama
        de retourner une explication vulgarisée et une liste de décisions structurées en JSON.
        """

        # Le prompt système force le modèle à cracher un JSON strict
        prompt_system = (
            "Tu es l'assistant d'aide à la décision Klaaro. Tu dois analyser le rapport fourni et répondre à l'utilisateur.\n"
            "Réponds TOUJOURS au format JSON strict et rien d'autre. Ne mets aucune phrase d'introduction ni de conclusion en dehors du JSON.\n"
            "Format de réponse requis :\n"
            "{\n"
            '  "explication": "Vulgarisation claire, pédagogique et détaillée de l\'analyse pour l\'utilisateur.",\n'
            '  "decisions": [\n'
            '    {"content": "Nom court de la décision", "description": "Explication de pourquoi et comment l\'appliquer"}\n'
            '  ]\n'
            "}"
        )

        user_message = f"Rapport de données : {report_content}\n\nQuestion de l'utilisateur : {query_content}"

        # Structuration avec le template de chat de TinyLlama
        messages = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": user_message}
        ]

        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=512,
                temperature=0.1,  # Encore plus bas pour forcer la structure JSON sans déviation
                do_sample=True
            )

        decoded_output = self.tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)

        # Nettoyage et parsing robuste du JSON
        try:
            # Recherche des délimiteurs de l'objet JSON
            start_idx = decoded_output.find("{")
            end_idx = decoded_output.rfind("}") + 1

            if start_idx == -1 or end_idx == -1:
                raise ValueError("Accolades JSON introuvables dans la réponse de l'IA.")

            json_str = decoded_output[start_idx:end_idx]

            # Suppression des retours à la ligne ou espaces parasites susceptibles de corrompre le parseur
            json_str = json_str.strip()

            return json.loads(json_str)

        except Exception as e:
            # Plan de secours robuste : si l'IA écrit du texte brut ou un JSON mal formé, on ne fait pas planter l'API
            print(f"Erreur lors du parsing du JSON généré par TinyLlama : {e}")
            print(f"Sortie brute de l'IA : {decoded_output}")
            return {
                "explication": decoded_output or "L'assistant n'a pas pu générer d'explication claire.",
                "decisions": [
                    {
                        "content": "Analyse manuelle requise",
                        "description": "Le format de la réponse de l'IA n'a pas pu être structuré automatiquement en actions directes. Veuillez lire l'explication générée.",
                    }
                ]
            }