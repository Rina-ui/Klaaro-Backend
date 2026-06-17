import redis
import json
import hashlib

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_cache_key(instruction: str) -> str:
    # Génère une clé unique basée sur l'instruction
    return f"klaaro:explanation:{hashlib.md5(instruction.encode()).hexdigest()}"

def get_cached_response(instruction: str):
    # Récupère une réponse en cache si elle existe
    key = get_cache_key(instruction)
    cached = redis_client.get(key)
    return json.loads(cached) if cached else None

def set_cached_response(instruction: str, response: str, expiry_seconds: int = 3600):
    # Sauvegarde une réponse en cache pour 1h par défaut
    key = get_cache_key(instruction)
    redis_client.set(key, json.dumps(response), ex=expiry_seconds)