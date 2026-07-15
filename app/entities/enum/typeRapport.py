from enum import Enum

class TypeRapport(str, Enum):
    PREPROCESSING = "preprocessing"
    PREDICTION = "prediction"
    CLASSIFICATION = "classification"
    ANALYSE = "analyse"