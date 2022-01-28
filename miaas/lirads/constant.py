import enum


class ImageType(enum.Enum):
    DCM = 0
    NII = 1
    NORMAL = 2


class SegModel(enum.Enum):
    instance = 0
    semantic = 1


class Stages(enum.Enum):
    LR_1 = 0
    LR_2 = 1
    LR_3 = 2
    LR_4 = 3
    LR_5 = 4
    LR_TIV = 5
    LR_M = 6
    none = -1


class HCCClass(enum.Enum):
    noAPHE = 0
    nonrimAPHE = 1
    none = 2


class MFType(enum.Enum):
    capsule = 0
    washout = 1
    none = 2


class LIRADSPhase(enum.Enum):
    Plain = 0
    Arterial_Phase = 1
    Portal_Venous_Phase = 2
    Delayed_Phase = 3
    NUM_PHASE = 4
    LIST_PHASE = ["PLAIN", "ARTERIAL", "VENOUS", "DELAY"]


class TumorType(enum.Enum):
    # Hemangioma = 0
    # HCC = 1

    Hemangioma = 0
    FNH = 1
    Adenoma = 2
    FLHCC = 3
    HCC = 4

    Metastases = 5


class TumorFeatures(enum.Enum):
    Capsule = 0
    Scar = 1
    Calcification = 2
    Inhomogeneity = 3


class ImagingFeatures(enum.Enum):
    Calcification = 0
    Capsule = 1
    CentralScar = 2
    HaloCapsule = 3
    Hypoattenuating = 4
    NoAPHE = 5
    Nodular = 6
    NonrimAPHE = 7
    Washout = 8
    RimAPHE = 9


class TumorSeverity:
    Benign = [TumorType.Hemangioma, TumorType.FNH, TumorType.Adenoma]
    Malignancy = [TumorType.FLHCC, TumorType.HCC, TumorType.Metastases]

