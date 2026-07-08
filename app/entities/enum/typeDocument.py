from enum import Enum

class TypeDocument(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    PDF = "pdf"
    XML = "xml"
    IMAGE = "image"