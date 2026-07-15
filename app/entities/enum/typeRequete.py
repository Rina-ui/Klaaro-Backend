from enum import Enum

class TypeRequete(Enum):
    VULGARISATION = "vulgarisation"  # "Explique-moi ce graphique"
    ACTION_PROMPT = "action_prompt"  # "Que dois-je faire ?"
    CHAT_LIBRE = "chat_libre"