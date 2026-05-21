from enum import Enum


class Status(Enum):
    Detected = "Detected"
    pending = "Pending"
    treatment = "Treatment"
    done = "Done"