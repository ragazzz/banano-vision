import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")

# Orden de clases -> DEBE coincidir con el orden usado al entrenar
CLASS_NAMES = [
    "Cordana",
    "Healthy",
    "Panama Disease",
    "Yellow and Black Sigatoka",
]

# Nombres "bonitos" para mostrar en la interfaz (puedes editar el texto libremente,
# el ORDEN debe mantenerse igual al de CLASS_NAMES)
CLASS_DISPLAY_NAMES = {
    "Cordana": "Cordana (Neocordana musae)",
    "Healthy": "Hoja sana",
    "Panama Disease": "Mal de Panamá (Fusarium oxysporum f. sp. cubense)",
    "Yellow and Black Sigatoka": "Sigatoka amarilla / negra (Mycosphaerella spp.)",
}

# Configuración de cada modelo: archivo, tamaño de entrada, tipo de preprocesamiento
MODELS_CONFIG = {
    "VGG16": {
        "file": os.path.join(MODELS_DIR, "vgg16_banano.keras"),
        "input_size": (224, 224),
        "preprocess": "vgg16",
    },
    "DenseNet121": {
        "file": os.path.join(MODELS_DIR, "densenet121_banano.keras"),
        "input_size": (224, 224),
        "preprocess": "densenet",
    },
    "Xception": {
        "file": os.path.join(MODELS_DIR, "xception_banano.keras"),
        "input_size": (299, 299),
        "preprocess": "xception",
    },
}

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_CONTENT_LENGTH_MB = 15

DISEASE_INFO = {
    "Cordana": {
        "agente_causal": "Hongo Cordana musae (reclasificado recientemente como Neocordana musae)",
        "severidad": "Baja — enfermedad secundaria, rara vez es la limitante principal del cultivo",
        "sintomas": [
            "Manchas ovaladas a romboidales (forma de \u201cdiamante\u201d) de color café pálido",
            "Borde bien definido rodeado de un halo amarillo",
            "Las manchas pueden unirse y formar grandes áreas necróticas; la hoja termina secándose",
            "Suele aparecer sobre heridas o lesiones previas causadas por otros hongos (p. ej. Sigatoka)",
        ],
        "manejo": [
            "Deshoje sanitario: retirar y destruir las hojas afectadas",
            "Mejorar drenaje y nutrición de la planta para reducir el estrés que favorece la infección",
            "Evitar salpicaduras de agua entre plantas (el hongo se dispersa por lluvia y viento)",
            "El control químico rara vez es necesario; se reserva para infecciones severas con fungicidas de contacto registrados",
        ],
    },
    "Panama Disease": {
        "agente_causal": "Hongo de suelo Fusarium oxysporum f. sp. cubense (incluye la Raza 4 Tropical, muy agresiva)",
        "severidad": "Muy alta — puede causar pérdida total de la producción; no tiene cura una vez establecida",
        "sintomas": [
            "Amarillamiento progresivo de las hojas más viejas que avanza hacia las más jóvenes",
            "Hojas que se doblan y cuelgan alrededor del pseudotallo (aspecto de \u201cfalda\u201d)",
            "Al cortar el pseudotallo o rizoma, el tejido vascular interno se ve de color marrón-rojizo",
            "El hongo sobrevive en el suelo por más de 20 años, incluso sin cultivo presente",
        ],
        "manejo": [
            "No existe control químico eficaz una vez que la planta está infectada",
            "Usar material de siembra certificado y libre del patógeno",
            "Desinfectar botas, herramientas y maquinaria antes de entrar a zonas sanas",
            "Aislar y eliminar plantas afectadas; evitar mover suelo o agua entre lotes",
            "Reportar sospechas a la autoridad fitosanitaria local por el riesgo de propagación a otras fincas",
        ],
    },
    "Yellow and Black Sigatoka": {
        "agente_causal": "Hongos del género Mycosphaerella: M. musicola (Sigatoka amarilla) y M. fijiensis (Sigatoka negra, más agresiva)",
        "severidad": "Alta — es la enfermedad foliar más importante del banano a nivel mundial",
        "sintomas": [
            "Inicia como pequeñas pecas o rayas amarillas (cloróticas) en el envés de la hoja",
            "Evolucionan a manchas alargadas color marrón-negro con halo amarillo y centro grisáceo",
            "En etapas avanzadas las manchas se unen, la hoja se necrosa y muere prematuramente",
            "Reduce fuertemente la capacidad fotosintética y por lo tanto el rendimiento del racimo",
        ],
        "manejo": [
            "Control cultural: deshoje sanitario, manejo de malezas, buen drenaje y densidad de siembra adecuada",
            "Control químico: fungicidas rotados entre grupos químicos para evitar resistencia del hongo, aplicados según calendario o sistema de pre-aviso climático",
            "Uso de variedades resistentes o tolerantes cuando estén disponibles",
            "Control biológico complementario con antagonistas como Trichoderma o Bacillus en algunos programas de manejo integrado",
        ],
    },
    "Healthy": {
        "agente_causal": None,
        "severidad": "No aplica — hoja sin signos de enfermedad",
        "sintomas": [
            "Sin manchas, decoloración ni necrosis visibles",
        ],
        "manejo": [
            "Monitoreo periódico del cultivo para detectar síntomas tempranos",
            "Riego y drenaje adecuados, evitando encharcamientos",
            "Fertilización balanceada según análisis de suelo",
            "Deshoje preventivo de hojas viejas o dañadas para reducir fuentes de inóculo de otras enfermedades",
        ],
    },
}