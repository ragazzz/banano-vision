"""
Carga de los 3 modelos .keras en memoria.

Los modelos se cargan UNA sola vez al iniciar la aplicación (no en cada
request) porque cargar un modelo de Keras es costoso en tiempo y memoria.
"""

import threading
import time

from tensorflow import keras

from config import MODELS_CONFIG

_models = {}
_predict_lock = threading.Lock()  # evita llamadas concurrentes a predict() sobre el mismo modelo


def load_all_models():
    """Carga los 3 modelos en el diccionario global _models. Se llama al arrancar la app."""
    for name, cfg in MODELS_CONFIG.items():
        print(f"[model_loader] Cargando {name} desde {cfg['file']} ...")
        t0 = time.time()
        model = keras.models.load_model(cfg["file"], compile=False)
        # "Calienta" el modelo con una predicción dummy para evitar que la
        # primera petición real del usuario sea lenta (tracing de TF).
        import numpy as np
        h, w = cfg["input_size"]
        dummy = np.zeros((1, h, w, 3), dtype="float32")
        model.predict(dummy, verbose=0)
        _models[name] = model
        print(f"[model_loader] {name} cargado en {time.time() - t0:.1f}s")
    return _models


def get_model(name):
    return _models[name]


def get_all_models():
    return _models


def get_lock():
    return _predict_lock