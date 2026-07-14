"""
Ejecuta los 3 modelos sobre la misma imagen y devuelve resultados
en un formato listo para comparar en la interfaz.
"""

import time

from config import MODELS_CONFIG, CLASS_NAMES, CLASS_DISPLAY_NAMES
from preprocessing import prepare_batch
from model_loader import get_model, get_lock


def predict_single_model(model_name: str, pil_image):
    cfg = MODELS_CONFIG[model_name]
    model = get_model(model_name)

    batch = prepare_batch(pil_image, cfg["input_size"], cfg["preprocess"])

    lock = get_lock()
    t0 = time.time()
    with lock:  # TF no siempre es thread-safe para llamadas concurrentes al mismo modelo
        preds = model.predict(batch, verbose=0)[0]
    elapsed_ms = (time.time() - t0) * 1000

    probs = {CLASS_NAMES[i]: float(preds[i]) for i in range(len(CLASS_NAMES))}
    top_idx = int(preds.argmax())
    top_class = CLASS_NAMES[top_idx]

    return {
        "model": model_name,
        "input_size": cfg["input_size"],
        "predicted_class": top_class,
        "predicted_class_display": CLASS_DISPLAY_NAMES.get(top_class, top_class),
        "confidence": probs[top_class],
        "probabilities": probs,
        "probabilities_display": {
            CLASS_DISPLAY_NAMES.get(c, c): p for c, p in probs.items()
        },
        "inference_ms": round(elapsed_ms, 1),
    }


def predict_all_models(pil_image):
    results = []
    for model_name in MODELS_CONFIG.keys():
        results.append(predict_single_model(model_name, pil_image))

    # Determina si los 3 modelos coinciden en la clase predicha
    all_agree = len({r["predicted_class"] for r in results}) == 1

    return {
        "results": results,
        "all_agree": all_agree,
    }