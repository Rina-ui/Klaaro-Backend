import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

class KlaaroAIService:
    def __init__(self, base_model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0", adapter_path: str = "ml/models/klaaro-tinyllama-v2"):
        print("Chargement du Tokenizer et du modèle TinyLlama...")
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)

        # Détection automatique de l'appareil (GPU ou CPU)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        print(f"Modèle chargé sur : {self.device.upper()} avec la précision : {dtype}")

        # Chargement propre du modèle de base
        if self.device == "cuda":
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                torch_dtype=dtype,
                device_map="auto"
            )
        else:
            print("Mode CPU détecté : Chargement direct en RAM.")
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                torch_dtype=dtype,
                device_map=None
            ).to(self.device)

        # Chargement de ton adaptateur LoRA
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
        Inférence calquée sur le format d'entraînement LoRA (instruction -> response).
        """
        # 1. On crée une instruction qui ressemble à 100% à celles de ton dataset
        # Exemple d'instruction dans ton dataset : "Analyse : chiffre_affaires=2500000 FCFA, ..."
        instruction = f"Analyse : {query_content}. Contexte et données : {report_content}"

        # 2. Structure brute sans Chat Template (pour éviter que TinyLlama Chat ne reprenne le dessus avec ses tirets)
        prompt = f"instruction: {instruction}\nresponse: "

        # On encode l'invite
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.3, # Bas pour rester fidèle au dataset
                do_sample=True,
                repetition_penalty=1.15
            )

        # On extrait la génération de l'IA
        decoded_output = self.tokenizer.decode(outputs[0][len(inputs["input_ids"][0]):], skip_special_tokens=True)

        # On nettoie les résidus de formatage s'il y en a
        clean_response = decoded_output.split("instruction:")[0].split("response:")[0].strip()

        print("--- SORTIE DE TON MODÈLE FINE-TUNÉ ---")
        print(clean_response)
        print("---------------------------------------")

        # Extraction d'une action pour l'interface utilisateur
        action_suggeree = "Appliquer les recommandations"
        description_action = "Suivre les conseils générés par l'analyse ci-dessus."

        phrases = [p.strip() for p in clean_response.replace("!", ".").split(".") if p.strip()]
        if phrases:
            derniere_phrase = phrases[-1]
            if len(derniere_phrase) < 120 and any(v in derniere_phrase.lower() for v in ["vérifiez", "analysez", "anticipez", "passez", "identifiez", "adaptez", "assurez-vous", "optimisez", "négociez", "bloquez"]):
                action_suggeree = "Action recommandée"
                description_action = derniere_phrase

        return {
            "explication": clean_response,
            "decisions": [
                {
                    "content": action_suggeree,
                    "description": description_action
                }
            ]
        }