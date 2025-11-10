import os
import numpy as np
import cv2
from flask import Flask, request, jsonify
from PIL import Image
from ultralytics import YOLO
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input  # Add this import
import tensorflow as tf
import random

print(tf.__version__)

# ----------------------------
# [INFO] Load models
# ----------------------------
print("[INFO] Loading YOLO model...")
yolo = YOLO("yolov8n.pt")

print("[INFO] Loading custom breed model...")
classifier = load_model("saved_model/model-2025-10-20-14-42-38.keras")

with open("dog_classes.txt") as f:
    BREED_CLASSES = [line.strip() for line in f]

# ----------------------------
# Adoption Centers Database
# ----------------------------
ADOPTION_CENTERS = {
    "general": [
        {
            "name": "American Society for the Prevention of Cruelty to Animals (ASPCA)",
            "website": "https://www.aspca.org/adopt-pet",
            "phone": "1-800-628-0028",
            "location": "National (Multiple Locations)",
            "description": "Leading animal welfare organization with adoption centers nationwide"
        },
        {
            "name": "Humane Society of the United States",
            "website": "https://www.humanesociety.org/adopt",
            "phone": "1-202-452-1100",
            "location": "National (Multiple Locations)",
            "description": "Comprehensive animal welfare organization with local chapters"
        },
        {
            "name": "Petfinder",
            "website": "https://www.petfinder.com",
            "phone": "N/A",
            "location": "Online Platform",
            "description": "Largest online database of adoptable pets from shelters and rescues"
        },
        {
            "name": "Adopt-a-Pet.com",
            "website": "https://www.adoptapet.com",
            "phone": "N/A",
            "location": "Online Platform",
            "description": "Free online service to help find adoptable pets"
        }
    ],
    "breed_specific": {
        "golden_retriever": [
            {
                "name": "Golden Retriever Rescue of the Rockies",
                "website": "https://www.goldenrescue.com",
                "phone": "1-303-279-2400",
                "location": "Colorado, USA",
                "description": "Specialized rescue for Golden Retrievers"
            },
            {
                "name": "Golden Retriever Club of America Rescue",
                "website": "https://www.grca.org/rescue",
                "phone": "N/A",
                "location": "National",
                "description": "Official breed club rescue network"
            }
        ],
        "labrador_retriever": [
            {
                "name": "Labrador Retriever Rescue",
                "website": "https://www.labrescue.org",
                "phone": "1-800-555-0123",
                "location": "National",
                "description": "Dedicated to rescuing and rehoming Labrador Retrievers"
            }
        ],
        "german_shepherd": [
            {
                "name": "German Shepherd Rescue of Orange County",
                "website": "https://www.gsroc.org",
                "phone": "1-714-974-7762",
                "location": "Orange County, CA",
                "description": "Specialized rescue for German Shepherds"
            }
        ],
        "bulldog": [
            {
                "name": "Bulldog Club of America Rescue",
                "website": "https://www.bcarescue.org",
                "phone": "N/A",
                "location": "National",
                "description": "Official breed club rescue for Bulldogs"
            }
        ],
        "poodle": [
            {
                "name": "Poodle Rescue of New England",
                "website": "https://www.poodlerescueofnewengland.org",
                "phone": "1-617-555-0123",
                "location": "New England",
                "description": "Rescue organization for Poodles of all sizes"
            }
        ]
    }
}

# ----------------------------
# Helper function to create breed-specific search URLs
# ----------------------------
def create_breed_search_urls(breed_name):
    """
    Create direct search URLs for adoption websites with the specific breed
    """
    # Clean breed name for URL parameters
    breed_clean = breed_name.lower().replace(" ", "-").replace("_", "-")
    breed_encoded = breed_name.replace(" ", "%20")
    
    search_urls = {
        "petfinder": f"https://www.petfinder.com/search/dogs-for-adoption/?breed={breed_encoded}",
        "adoptapet": f"https://www.adoptapet.com/s/adoptable-dogs?breed={breed_encoded}",
        "aspca": f"https://www.aspca.org/adopt-pet?animal=dog&breed={breed_encoded}",
        "humane_society": f"https://www.humanesociety.org/adopt?animal=dog&breed={breed_encoded}",
        "petsmart_charities": f"https://www.petsmartcharities.org/adopt-a-pet?animal=dog&breed={breed_encoded}",
        "rescue_me": f"https://www.rescueme.org/dog?breed={breed_encoded}",
        "akc_rescue": f"https://www.akc.org/rescue-network/?breed={breed_encoded}"
    }
    
    return search_urls

# ----------------------------
# Helper function to get adoption centers with redirect URLs
# ----------------------------
def get_adoption_centers(breed_name):
    """
    Get adoption centers for a specific breed with direct search URLs
    """
    breed_lower = breed_name.lower().replace(" ", "_").replace("-", "_")
    
    # Get breed-specific centers if available
    breed_centers = []
    if breed_lower in ADOPTION_CENTERS["breed_specific"]:
        breed_centers = ADOPTION_CENTERS["breed_specific"][breed_lower]
    
    # Always include general centers
    general_centers = ADOPTION_CENTERS["general"]
    
    # Create breed-specific search URLs
    search_urls = create_breed_search_urls(breed_name)
    
    # Enhance centers with direct search URLs
    enhanced_centers = []
    
    # Add breed-specific centers with search URLs
    for center in breed_centers:
        enhanced_center = center.copy()
        enhanced_center["direct_search_url"] = search_urls.get("petfinder", center["website"])
        enhanced_center["search_available"] = True
        enhanced_centers.append(enhanced_center)
    
    # Add general centers with search URLs
    for center in general_centers:
        enhanced_center = center.copy()
        if "petfinder" in center["name"].lower():
            enhanced_center["direct_search_url"] = search_urls["petfinder"]
        elif "adopt-a-pet" in center["name"].lower():
            enhanced_center["direct_search_url"] = search_urls["adoptapet"]
        elif "aspca" in center["name"].lower():
            enhanced_center["direct_search_url"] = search_urls["aspca"]
        elif "humane society" in center["name"].lower():
            enhanced_center["direct_search_url"] = search_urls["humane_society"]
        else:
            enhanced_center["direct_search_url"] = center["website"]
        
        enhanced_center["search_available"] = True
        enhanced_centers.append(enhanced_center)
    
    # Add additional search platforms
    additional_platforms = [
        {
            "name": "PetSmart Charities",
            "website": "https://www.petsmartcharities.org",
            "direct_search_url": search_urls["petsmart_charities"],
            "phone": "1-800-745-2275",
            "location": "National",
            "description": "PetSmart's charitable foundation with adoption centers",
            "search_available": True
        },
        {
            "name": "Rescue Me",
            "website": "https://www.rescueme.org",
            "direct_search_url": search_urls["rescue_me"],
            "phone": "N/A",
            "location": "Online Platform",
            "description": "Direct-to-adopter rescue platform",
            "search_available": True
        }
    ]
    
    enhanced_centers.extend(additional_platforms)
    
    # Combine and randomize to show variety
    random.shuffle(enhanced_centers)
    
    # Return top 4-5 centers with search URLs
    return enhanced_centers[:5]

# ----------------------------
# Helper function
# ----------------------------
def predict_breed(img_path):
    try:
        # Load image as PIL Image first (like in working code)
        img_pil = Image.open(img_path).convert("RGB")
        img_array = np.array(img_pil)

        # Detect dog with YOLO
        results = yolo(img_array)

        # Check if any dogs were detected
        if results[0].boxes is None:
            return {"error": "No dogs detected"}

        boxes = results[0].boxes.xyxy.cpu().numpy()
        labels = results[0].boxes.cls.cpu().numpy()

        # Find the first dog (COCO class 16)
        dog_box = None
        for i, box in enumerate(boxes):
            if int(labels[i]) == 16:  # COCO class 16 = dog
                dog_box = box
                break

        if dog_box is None:
            return {"error": "No dog detected"}

        # Crop the dog region
        x1, y1, x2, y2 = map(int, dog_box)

        # Load image with OpenCV for cropping (like in working code)
        img_cv = cv2.imread(img_path)
        h, w, _ = img_cv.shape

        # Ensure coordinates are within bounds
        x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)

        if x2 <= x1 or y2 <= y1:
            return {"error": "Invalid crop dimensions"}

        dog_crop = img_cv[y1:y2, x1:x2]

        # Save cropped image temporarily
        crop_path = "temp_crop.jpg"
        cv2.imwrite(crop_path, dog_crop)

        # Load and preprocess exactly like in working code
        img = image.load_img(crop_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)  # Use ResNet50 preprocessing instead of /255.0

        # Predict
        preds = classifier.predict(x)

        # Get top 3 predictions like in working code
        probs = preds[0]
        top_indices = probs.argsort()[-3:][::-1]  # Top 3 predictions

        top_predictions = []
        for idx in top_indices:
            breed_name = BREED_CLASSES[idx]
            confidence = float(probs[idx])
            top_predictions.append({
                "breed": breed_name,
                "confidence": confidence
            })

        print("Check top predictions---------->", top_predictions)

        # Clean up temporary file
        if os.path.exists(crop_path):
            os.remove(crop_path)

        # Get adoption centers for the detected breed
        adoption_centers = get_adoption_centers(top_predictions[0]["breed"])
        
        # Create direct search URLs for the breed
        search_urls = create_breed_search_urls(top_predictions[0]["breed"])
        
        return {
            "breed": top_predictions[0]["breed"],
            "confidence": top_predictions[0]["confidence"],
            "adoption_centers": adoption_centers,
            "direct_search_urls": search_urls,
            "message": f"Found {len(adoption_centers)} adoption centers for {top_predictions[0]['breed']} dogs",
            "redirect_info": {
                "petfinder_url": search_urls["petfinder"],
                "adoptapet_url": search_urls["adoptapet"],
                "aspca_url": search_urls["aspca"],
                "note": "Click any URL to search for this breed directly on the adoption website"
            }
        }
    except Exception as e:
        print(f"Error in predict_breed: {e}")
        return {"error": str(e)}

# ----------------------------
# Flask API
# ----------------------------
app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    f = request.files["file"]
    if f.filename == '':
        return jsonify({"error": "No file selected"}), 400

    filepath = os.path.join("uploads", f.filename)
    os.makedirs("uploads", exist_ok=True)
    f.save(filepath)

    try:
        result = predict_breed(filepath)
        # Clean up uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/adoption-centers/<breed_name>", methods=["GET"])
def get_adoption_centers_by_breed(breed_name):
    """
    Get adoption centers for a specific breed
    """
    try:
        centers = get_adoption_centers(breed_name)
        return jsonify({
            "breed": breed_name,
            "adoption_centers": centers,
            "count": len(centers)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/adoption-centers", methods=["GET"])
def get_all_adoption_centers():
    """
    Get all available adoption centers
    """
    try:
        return jsonify({
            "general_centers": ADOPTION_CENTERS["general"],
            "breed_specific_centers": list(ADOPTION_CENTERS["breed_specific"].keys())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/redirect/<breed_name>", methods=["GET"])
def redirect_to_adoption_site(breed_name):
    """
    Redirect user to adoption site with breed pre-searched
    """
    from flask import redirect
    
    try:
        search_urls = create_breed_search_urls(breed_name)
        
        # Default to Petfinder as it's the most popular
        redirect_url = search_urls.get("petfinder", "https://www.petfinder.com")
        
        return redirect(redirect_url)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/search-urls/<breed_name>", methods=["GET"])
def get_search_urls(breed_name):
    """
    Get all search URLs for a specific breed
    """
    try:
        search_urls = create_breed_search_urls(breed_name)
        return jsonify({
            "breed": breed_name,
            "search_urls": search_urls,
            "message": f"Direct search URLs for {breed_name} dogs"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)