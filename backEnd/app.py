

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tensorflow as tf
import pyttsx3
import os
import tempfile
import numpy as np
from tensorflow.keras.preprocessing import image
import time  # For tracking performance

app = Flask(__name__)
CORS(app, origins=["192.168.1.21:8081"])

# Load the trained model and optimize by pre-loading it to memory
model_path = 'C:/Users/iisha_ol6x3qs/Documents/miniProject/backEnd/ingredient_model.keras'
model = tf.keras.models.load_model(model_path)

# Define image parameters
img_height, img_width = 224, 224  # Set to the image size the model was trained on

# Class names
class_names = ['Bean', 'Bitter_Gourd', 'Bottle_Gourd', 'Brinjal', 'Broccoli', 'Cabbage', 'Capsicum',
               'Carrot', 'Cauliflower', 'Cucumber', 'Papaya', 'Potato', 'Pumpkin', 'Radish', 'Tomato']

# Initialize text-to-speech engine
engine = pyttsx3.init()

def preprocess_image(img_path, img_height=224, img_width=224):
    # Load the image with target size
    img = image.load_img(img_path, target_size=(img_height, img_width))
    # Convert the image to array
    img_array = image.img_to_array(img)
    # Rescale the image (same as during training)
    img_array = img_array / 255.0
    # Expand dimensions to match the expected input shape for the model
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

@app.route('/')
def index():
    return "Welcome to the model API"

@app.route('/identify', methods=['POST'])
def identify():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    img_file = request.files['image']
    if img_file.filename == '':
        return jsonify({'error': 'No selected image'}), 400

    # Determine the temporary file path based on the operating system
    temp_dir = tempfile.gettempdir()
    img_path = os.path.join(temp_dir, secure_filename(img_file.filename))

    # Ensure the directory exists
    os.makedirs(temp_dir, exist_ok=True)
    
    img_file.save(img_path)
    print("Saved image to:", img_path)

    # Time the preprocessing step for optimization monitoring
    start_time = time.time()
    
    # Preprocess the image
    preprocessed_image = preprocess_image(img_path, img_height=img_height, img_width=img_width)
    
    preprocessing_time = time.time() - start_time
    print(f"Preprocessing time: {preprocessing_time:.4f} seconds")

    # Time the model inference step
    start_time = time.time()

    # Make predictions
    prediction = model.predict(preprocessed_image)
    
    inference_time = time.time() - start_time
    print(f"Inference time: {inference_time:.4f} seconds")

    predicted_class_index = np.argmax(prediction)
    predicted_class_name = class_names[predicted_class_index]
    
    # Use text-to-speech to speak the predicted class name
    try:
        # Ensure engine is not running
        if engine._inLoop:
            engine.endLoop()
        engine.say(f"The object is {predicted_class_name}")
        engine.runAndWait()
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500

    # Clean up temporary image file
    os.remove(img_path)

    return jsonify({
        'prediction': predicted_class_name,
        'preprocessing_time': f"{preprocessing_time:.4f} seconds",
        'inference_time': f"{inference_time:.4f} seconds"
    })

if __name__ == '__main__':
    app.run(debug=True)
