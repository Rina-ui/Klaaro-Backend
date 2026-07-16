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
        Inférence cadrée pour éviter les hallucinations de TinyLlama.
        """
        # Cadrage strict du rôle et des consignes pour limiter les dérives de génération
        system_instruction = (
            "Tu es Klaaro, un assistant financier clair et pédagogue. "
            "Analyse le graphique de prévision de façon simple pour un utilisateur novice. "
            "Règles strictes : "
            "1. Décris uniquement la tendance visuelle (ex: forte hausse initiale suivie d'une stabilisation stable). "
            "2. N'invente jamais d'années, de pourcentages ou de termes économiques complexes. "
            "3. Reste cohérent (ne dis pas qu'il y a une baisse et une hausse en même temps). "
            "4. Utilise un français parfait et naturel. Pas de jargon."
        )

        instruction = f"{system_instruction}\nDonnées à analyser : {query_content}. Contexte additionnel : {report_content}"

        # Structure brute pour le modèle fine-tuné
        prompt = f"instruction: {instruction}\nresponse: "

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=180, # Réduit pour éviter qu'il ne se mette à boucler ou radoter
                temperature=0.2,    # Plus bas (0.2 au lieu de 0.3) pour le rendre plus factuel et direct
                do_sample=True,
                repetition_penalty=1.2 # Légèrement augmenté pour chasser les répétitions et le bégaiement
            )

        decoded_output = self.tokenizer.decode(outputs[0][len(inputs["input_ids"][0]):], skip_special_tokens=True)

        # Nettoyage
        clean_response = decoded_output.split("instruction:")[0].split("response:")[0].strip()

        print("--- SORTIE DE TON MODÈLE FINE-TUNÉ ---")
        print(clean_response)
        print("---------------------------------------")

        # Extraction de l'action pour l'UI
        action_suggeree = "Surveiller la tendance"
        description_action = "Conserver le suivi actuel de la courbe pour détecter tout changement."

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