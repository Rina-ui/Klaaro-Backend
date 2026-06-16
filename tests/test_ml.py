# test_ml.py
from app.use_cases.services.ml.klaaro_ml_service import ml_service

print(ml_service.generate_explanation("Analyse ces données : montant=200000 FCFA, variation=-15%"))