import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# seeder
np.random.seed(42)

N_NORMAL = 1000
N_ANOMALIE = 50

def generate_normal_data(n):
    data = {
        'date': pd.date_range(start='2024-01-01', end='2024-12-31', periods=n),
        'montant': np.random.randint(5000, 500000, n),
        'quantite': np.random.randint(1, 100, n),
        'heure': np.random.randint(8, 20, n),
        'type_transaction': random.choices(['vente', 'achat', 'remboursement'], k=n),
        'is_anomalie': [0] * n
    }
    return pd.DataFrame(data)

def generate_anomalie_data(n):
    data = {
        'date': pd.date_range(start='2025-01-01', end='2025-12-31', periods=n),
        'montant': np.random.randint(2000000, 5000000, n),
        'quantite': np.random.randint(500, 1000, n),
        'heure': np.random.randint(0, 5, n),
        'type_transaction': random.choices(['vente', 'achat', 'remboursement'], k=n),
        'is_anomalie': [1] * n
    }
    return pd.DataFrame(data)

if __name__ == "__main__":
    normal = generate_normal_data(N_NORMAL)
    anomalies = generate_anomalie_data(N_ANOMALIE)

    dataset = pd.concat([normal, anomalies], ignore_index=True)
    dataset = dataset.sample(frac=1).reset_index(drop=True)

    import os
    os.makedirs('ml/datasets', exist_ok=True)
    dataset.to_csv('ml/datasets/klaaro_dataset.csv', index=False)
    print(f"Dataset généré : {len(dataset)} lignes")