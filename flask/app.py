from tensorflow.keras.models import load_model
import numpy as np
import os
import io
import cv2
from werkzeug.utils import secure_filename
from datetime import datetime as dt
from flask import Flask, flash, request, redirect, render_template
from PIL import Image
from pillow_heif import register_heif_opener


app = Flask(__name__)
upload_folder = "static/uploads"
app.config["SECRET_KEY"] = "SecretKey"
app.config["UPLOAD_FOLDER"] = upload_folder

# Load the saved model
model_path = "static/models/ann_model.h5"
model = load_model(model_path)

#CONVERT HEIC FORMAT IMAGE TO JPG
def heic_tp_jpg(img_path):
    register_heif_opener()
    heic_image = Image.open(img_path)
    # Convert to a format compatible with OpenCV (e.g., RGB)
    heic_image.convert('RGB').save(img_path+'.jpg')

# To verify file type
def allowed_file(filename):
    extensions = {"png", "jpg", "jpeg",".HEIC"}
    if filename.endswith(".HEIC"):
        heic_tp_jpg(filename)
    return "." in filename and filename.rsplit(".")[1].lower() in extensions

def prepare_image(image_path):
    # Define the target image size
    IMG_SIZE = (128, 128)
    img = cv2.imread(image_path)
    img = cv2.resize(img, IMG_SIZE) 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #Apply Gaussian Blur
    blurred = cv2.GaussianBlur(gray, ksize=(3, 3), sigmaX=1) 

    #Apply Canny Edge 
    v = np.median(blurred)
    sigma = 0.33
    lower = int(max(50, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    aperture_size = 3
    img_edge = cv2.Canny(blurred,lower,upper,apertureSize=aperture_size,L2gradient=True)

    img_edge = img_edge / 255.0  # Normalisasi ke rentang [0,1]
    img_edge = np.stack((img_edge,) * 3, axis=-1)
    img_edge = np.expand_dims(img_edge, axis=0)  # Tambahkan dimensi batch
    return img_edge


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)

        image_file = request.files["file"]

        if image_file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            dt_now = dt.now().strftime("%Y%m%d%H%M%S%f")
            filename = dt_now + ".jpg"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(file_path)

            # Load and preprocess the image
            img = prepare_image(file_path)

            # Make a prediction
            predictions = model.predict(img)
            predicted_class = np.argmax(predictions[0]) # Assuming a classification task

            # Customize based on your class labels
            class_labels = ["Apartment","Penthouse","Ruko","Rumah 1 Lantai"]
            building_class = class_labels[predicted_class]
            confidence  = predictions[0][predicted_class] * 100

            return render_template("results.html", img_path=file_path, result=building_class,
                                   confidence=confidence)

    return render_template("index.html")


if __name__ == "__main__":
    app.run()
