# --------------------------
# Install packages
# --------------------------
#!pip install ultralytics opencv-python-headless matplotlib tensorflow

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import requests
from PIL import Image
from io import BytesIO
from ultralytics import YOLO
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import load_model

# --------------------------
# 1. Load Models
# --------------------------
detector = YOLO("yolov8n.pt")  # YOLOv8 object detector (for dog detection)
breed_classifier_model = load_model("saved_model/model-2025-10-20-14-42-38.keras")

# Load your custom breed class names (must match training order)
with open("dog_classes.txt") as f:
    class_names = [line.strip() for line in f]

# --------------------------
# 2. Download or Load a Sample Dog Image
# --------------------------
url = "https://static.vecteezy.com/system/resources/previews/005/857/332/non_2x/funny-portrait-of-cute-corgi-dog-outdoors-free-photo.jpg"
img_path = "Dog_test/zs.webp"

if not os.path.exists(img_path):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(img_path, "wb") as f:
        f.write(r.content)

# --------------------------
# 3. Run YOLO Detection
# --------------------------
try:
    img_pil = Image.open(img_path).convert("RGB")  # Ensure RGB
    img_array = np.array(img_pil)
    results = detector(img_array)  # Run YOLO detection
except Exception as e:
    print(f"Error loading or processing image: {e}")
    results = None

# --------------------------
# 4. Crop Dog Regions
# --------------------------
dog_crops = []
if results and results[0].boxes is not None:
    boxes = results[0].boxes.xyxy.cpu().numpy()   # Bounding boxes (x1,y1,x2,y2)
    labels = results[0].boxes.cls.cpu().numpy()   # Class labels
    img_cv = cv2.imread(img_path)                 # Load for cropping (BGR)

    for i, box in enumerate(boxes):
        if int(labels[i]) == 16:  # COCO class 16 = dog
            x1, y1, x2, y2 = map(int, box)
            h, w, _ = img_cv.shape
            x1, y1, x2, y2 = max(0,x1), max(0,y1), min(w,x2), min(h,y2)
            if x2 > x1 and y2 > y1:
                dog_crop = img_cv[y1:y2, x1:x2]
                dog_crops.append(dog_crop)
else:
    print("No dogs detected.")

# --------------------------
# 5. Breed Classification
# --------------------------
predictions = []
if dog_crops:
    for i, crop in enumerate(dog_crops):
        crop_path = f"dog_crop_{i}.jpg"
        cv2.imwrite(crop_path, crop)

        try:
            img = image.load_img(crop_path, target_size=(224,224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)  # Same preprocessing used in training

            preds = breed_classifier_model.predict(x)  # (1, num_classes)
            probs = preds[0]
            top_indices = probs.argsort()[-3:][::-1]  # Top 3 predictions you can make it one if you like
            decoded = [(class_names[j], float(probs[j])) for j in top_indices]
            predictions.append(decoded)
        except Exception as e:
            print(f"Error classifying dog crop {i}: {e}")
            predictions.append(f"Classification Error: {e}")

# --------------------------
# 6. Display Results
# --------------------------
if results:
    res_plot = results[0].plot()
    plt.figure(figsize=(10,5))
    plt.subplot(1, max(1, len(dog_crops) + (1 if dog_crops else 0)), 1)
    plt.imshow(cv2.cvtColor(res_plot, cv2.COLOR_BGR2RGB))
    plt.title("Detected Dog(s)")
    plt.axis("off")

if dog_crops:
    for i, crop in enumerate(dog_crops):
        plt.subplot(1, max(1, len(dog_crops) + (1 if results else 0)), i + (2 if results else 1))
        plt.imshow(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
        plt.title(f"Cropped Dog {i+1}")
        plt.axis("off")

plt.tight_layout()
plt.show()

# --------------------------
# 7. Print Breed Predictions
# --------------------------
if predictions:
    for i, decoded in enumerate(predictions):
        print(f"🐕 Dog {i+1} Breed Predictions:")
        if isinstance(decoded, list):
            for (breed, score) in decoded:
                print(f" - {breed} ({score*100:.2f}%)")
        else:
            print(decoded)
