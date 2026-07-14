import os
import uuid

from flask import Flask, request, jsonify, render_template, url_for

from config import ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH_MB, UPLOAD_DIR, DISEASE_INFO, CLASS_DISPLAY_NAMES
from model_loader import load_all_models
from preprocessing import load_image_as_rgb
from inference import predict_all_models

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH_MB * 1024 * 1024

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Carga los 3 modelos UNA vez, al iniciar el proceso (no en cada request)
print("Cargando modelos, esto puede tardar unos segundos...")
load_all_models()
print("Modelos listos.")


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No se envió ninguna imagen."}), 400

    file = request.files["image"]

    if file.filename == "" and not file.content_type.startswith("image/"):
        return jsonify({"error": "Archivo vacío o inválido."}), 400

    # Las fotos tomadas con la cámara llegan como blob sin nombre de archivo válido,
    # así que validamos por content-type también.
    if file.filename and not allowed_file(file.filename):
        return jsonify({"error": "Formato no soportado. Usa JPG, PNG o WEBP."}), 400

    try:
        pil_image = load_image_as_rgb(file.stream)
    except Exception:
        return jsonify({"error": "No se pudo leer la imagen. Verifica el archivo."}), 400

    # Guarda una copia para mostrarla en el resultado
    saved_name = f"{uuid.uuid4().hex}.jpg"
    saved_path = os.path.join(UPLOAD_DIR, saved_name)
    pil_image.save(saved_path, format="JPEG", quality=90)

    try:
        prediction = predict_all_models(pil_image)
    except Exception as e:
        return jsonify({"error": f"Error al predecir: {str(e)}"}), 500

    # Ficha informativa: solo para las clases que realmente aparecieron
    # como predicción entre los 3 modelos (evita mandar info irrelevante).
    unique_classes = list(dict.fromkeys(r["predicted_class"] for r in prediction["results"]))
    prediction["disease_info"] = [
        {
            "class_name": cls,
            "display_name": CLASS_DISPLAY_NAMES.get(cls, cls),
            **DISEASE_INFO.get(cls, {}),
        }
        for cls in unique_classes
    ]

    prediction["image_url"] = url_for("static", filename=f"uploads/{saved_name}")
    return jsonify(prediction)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True, use_reloader=False)