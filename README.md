# Klaaro Backend

Système intelligent d'aide à la décision basé sur la data science et la cybersécurité pour les PME africaines.

## Stack technique

- **Framework** : FastAPI
- **Base de données** : PostgreSQL + Redis
- **Modèles ML** : Phi-3/Mistral + Isolation Forest
- **Authentification** : JWT + MFA

## Installation

### Prérequis
- Python 3.10+
- PostgreSQL
- Redis

### Étapes

1. Cloner le projet
```bash
git clone https://github.com/ton-username/klaaro-backend.git
cd klaaro-backend
```

2. Créer et activer l'environnement virtuel
```bash
python -m venv venv
source venv/bin/activate
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement
```bash
cp .env.example .env
```

5. Lancer le serveur
```bash
uvicorn app.main:app --reload
```

## Structure du projet
```bash
klaaro-backend/
├── app/
│   ├── entities/        # Modèles de données
│   ├── use_cases/       # Logique métier
│   ├── adapters/        # Routes API
│   └── infrastructure/  # BD et services externes
├── tests/
├── .env
└── requirements.txt
```

## Auteur

AZOUMARO Marina-Gracia — Owner du projet Klaaro