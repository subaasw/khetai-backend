import os
import json
from PIL import Image

import numpy as np  
import tensorflow as tf

working_dir = os.path.dirname(os.path.abspath(__file__))
model_path = f"{working_dir}/../trained_models/plant_disease_prediction_model.keras"

# Model the pretrain model
model = tf.keras.models.load_model(model_path)

# lading the class names
class_indices = json.load(open(f"{working_dir}/../class_indices.json"))

# Function to load and preprocess the image using pillow 
def load_and_preprocess_image(image_path, target_size=(224, 224)):
    img = Image.open(image_path)
    img = img.resize(target_size)
    
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array.astype('float32') / 255. 
    
    return img_array

# Function to predict the class of an image 
def predict_image_class(image_path, model = model, class_indices = class_indices):
    preprocessed_image = load_and_preprocess_image(image_path)
    predictions = model.predict(preprocessed_image)
    
    predict_class_index = np.argmax(predictions, axis=1)[0]
    predict_class_name = class_indices[str(predict_class_index)]
    return predict_class_name
