"""
Preprocesamiento de imágenes para los modelos.

IMPORTANTE: los 3 modelos guardados (.keras) YA incluyen su normalización dentro
del grafo (además de las capas de data augmentation, inactivas en inferencia).
Por eso el código NO debe volver a aplicar `keras.applications.*.preprocess_input`:
hacerlo cambia el rango de entrada respecto al usado en el entrenamiento y degrada
las predicciones. Se entrega la imagen cruda float32 en rango [0, 255].
Ver INVESTIGACION_BUG.md §6 para la evidencia.
"""

import numpy as np
from PIL import Image, ImageOps


def load_image_as_rgb(file_stream):
    """Abre un archivo/stream de imagen y lo normaliza a RGB (soporta PNG con alpha, etc.).

    Aplica la orientación EXIF para que las fotos verticales tomadas con celular no
    entren rotadas 90° a la red.
    """
    img = Image.open(file_stream)
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    return img


def prepare_batch(pil_image: Image.Image, target_size: tuple, preprocess_key: str = None) -> np.ndarray:
    """
    Redimensiona la imagen al tamaño esperado por el modelo y devuelve el batch
    crudo en float32 [0, 255], que es lo que esperan los modelos (la normalización
    ya vive dentro del grafo).

    Nota: se redimensiona directamente al tamaño objetivo (sin recorte ni
    padding) con interpolación bilineal, igual que `image_dataset_from_directory`
    por defecto durante el entrenamiento.

    `preprocess_key` se conserva por compatibilidad con la firma usada en
    inference.py, pero ya no se utiliza (la normalización es interna al modelo).
    """
    resized = pil_image.resize(target_size, Image.BILINEAR)
    arr = np.asarray(resized, dtype=np.float32)
    arr = np.expand_dims(arr, axis=0)  # (1, H, W, 3)
    return arr
