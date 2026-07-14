"""
Preprocesamiento de imágenes para cada arquitectura.

Cada arquitectura de Keras Applications espera su propia normalización:
- VGG16: BGR + resta de medias de ImageNet (modo 'caffe')
- DenseNet121: reescala a [0,1] y normaliza con medias/std de ImageNet (modo 'torch')
- Xception: reescala a [-1, 1] (modo 'tf')

Usamos las funciones oficiales de keras.applications para no reinventar la rueda
y asegurar que coincidan exactamente con las usadas en `preprocess_input`
durante el entrenamiento (asunción documentada en config.py).
"""

import numpy as np
from PIL import Image

from tensorflow.keras.applications import vgg16, densenet, xception

_PREPROCESS_FUNCS = {
    "vgg16": vgg16.preprocess_input,
    "densenet": densenet.preprocess_input,
    "xception": xception.preprocess_input,
}


def load_image_as_rgb(file_stream):
    """Abre un archivo/stream de imagen y lo normaliza a RGB (soporta PNG con alpha, etc.)."""
    img = Image.open(file_stream)
    img = img.convert("RGB")
    return img


def prepare_batch(pil_image: Image.Image, target_size: tuple, preprocess_key: str) -> np.ndarray:
    """
    Redimensiona la imagen al tamaño esperado por el modelo y aplica el
    preprocesamiento correspondiente a su arquitectura.

    Nota: se redimensiona directamente al tamaño objetivo (sin recorte ni
    padding), que es el comportamiento por defecto de
    `image_dataset_from_directory` / `ImageDataGenerator` con `target_size`.
    """
    resized = pil_image.resize(target_size, Image.LANCZOS)
    arr = np.asarray(resized, dtype=np.float32)
    arr = np.expand_dims(arr, axis=0)  # (1, H, W, 3)

    preprocess_fn = _PREPROCESS_FUNCS[preprocess_key]
    arr = preprocess_fn(arr)
    return arr