# Enhanced Dog Breed Detection API with Adoption Centers & Direct Redirects

## Overview
This enhanced API not only detects dog breeds from uploaded images but also provides real adoption centers and **direct redirect links** that take users to adoption websites with the specific breed already searched.

## Features
- 🐕 Dog breed detection using YOLO + custom CNN model
- 🏠 Real adoption center recommendations
- 🔗 **Direct redirect URLs** to adoption sites with breed pre-searched
- 🌐 Multiple API endpoints for different use cases
- 📱 JSON responses with comprehensive information
- 🎯 **One-click adoption search** - users go directly to Petfinder/Adopt-a-Pet with their breed

## API Endpoints

### 1. POST /predict
**Purpose**: Upload an image to detect the dog breed and get adoption center recommendations

**Request**:
- Method: POST
- Content-Type: multipart/form-data
- Body: file (image file)

**Response**:
```json
{
  "breed": "German Shepherd",
  "confidence": 0.95,
  "adoption_centers": [
    {
      "name": "German Shepherd Rescue of Orange County",
      "website": "https://www.gsroc.org",
      "direct_search_url": "https://www.petfinder.com/search/dogs-for-adoption/?breed=German%20Shepherd",
      "phone": "1-714-974-7762",
      "location": "Orange County, CA",
      "description": "Specialized rescue for German Shepherds",
      "search_available": true
    }
  ],
  "direct_search_urls": {
    "petfinder": "https://www.petfinder.com/search/dogs-for-adoption/?breed=German%20Shepherd",
    "adoptapet": "https://www.adoptapet.com/s/adoptable-dogs?breed=German%20Shepherd",
    "aspca": "https://www.aspca.org/adopt-pet?animal=dog&breed=German%20Shepherd",
    "humane_society": "https://www.humanesociety.org/adopt?animal=dog&breed=German%20Shepherd",
    "petsmart_charities": "https://www.petsmartcharities.org/adopt-a-pet?animal=dog&breed=German%20Shepherd",
    "rescue_me": "https://www.rescueme.org/dog?breed=German%20Shepherd",
    "akc_rescue": "https://www.akc.org/rescue-network/?breed=German%20Shepherd"
  },
  "redirect_info": {
    "petfinder_url": "https://www.petfinder.com/search/dogs-for-adoption/?breed=German%20Shepherd",
    "adoptapet_url": "https://www.adoptapet.com/s/adoptable-dogs?breed=German%20Shepherd",
    "aspca_url": "https://www.aspca.org/adopt-pet?animal=dog&breed=German%20Shepherd",
    "note": "Click any URL to search for this breed directly on the adoption website"
  },
  "message": "Found 5 adoption centers for German Shepherd dogs"
}
```

### 2. GET /adoption-centers
**Purpose**: Get all available adoption centers

**Response**:
```json
{
  "general_centers": [
    {
      "name": "American Society for the Prevention of Cruelty to Animals (ASPCA)",
      "website": "https://www.aspca.org/adopt-pet",
      "phone": "1-800-628-0028",
      "location": "National (Multiple Locations)",
      "description": "Leading animal welfare organization with adoption centers nationwide"
    }
  ],
  "breed_specific_centers": [
    "golden_retriever",
    "labrador_retriever",
    "german_shepherd",
    "bulldog",
    "poodle"
  ]
}
```

### 3. GET /adoption-centers/<breed_name>
**Purpose**: Get adoption centers for a specific breed

**Example**: GET /adoption-centers/german_shepherd

**Response**:
```json
{
  "breed": "german_shepherd",
  "adoption_centers": [
    {
      "name": "German Shepherd Rescue of Orange County",
      "website": "https://www.gsroc.org",
      "direct_search_url": "https://www.petfinder.com/search/dogs-for-adoption/?breed=German%20Shepherd",
      "phone": "1-714-974-7762",
      "location": "Orange County, CA",
      "description": "Specialized rescue for German Shepherds",
      "search_available": true
    }
  ],
  "count": 5
}
```

### 4. GET /redirect/<breed_name>
**Purpose**: Direct redirect to Petfinder with breed pre-searched

**Example**: GET /redirect/german%20shepherd

**Response**: HTTP 302 Redirect to Petfinder with German Shepherd search

### 5. GET /search-urls/<breed_name>
**Purpose**: Get all search URLs for a specific breed

**Example**: GET /search-urls/german%20shepherd

**Response**:
```json
{
  "breed": "german shepherd",
  "search_urls": {
    "petfinder": "https://www.petfinder.com/search/dogs-for-adoption/?breed=German%20Shepherd",
    "adoptapet": "https://www.adoptapet.com/s/adoptable-dogs?breed=German%20Shepherd",
    "aspca": "https://www.aspca.org/adopt-pet?animal=dog&breed=German%20Shepherd",
    "humane_society": "https://www.humanesociety.org/adopt?animal=dog&breed=German%20Shepherd",
    "petsmart_charities": "https://www.petsmartcharities.org/adopt-a-pet?animal=dog&breed=German%20Shepherd",
    "rescue_me": "https://www.rescueme.org/dog?breed=German%20Shepherd",
    "akc_rescue": "https://www.akc.org/rescue-network/?breed=German%20Shepherd"
  },
  "message": "Direct search URLs for german shepherd dogs"
}
```

## Testing with Postman

### 1. Test Image Upload (POST /predict)
1. Open Postman
2. Create a new POST request to `http://localhost:5000/predict`
3. Go to Body → form-data
4. Add key: `file`, type: File, value: select an image file
5. Send the request

### 2. Test Adoption Centers (GET /adoption-centers)
1. Create a new GET request to `http://localhost:5000/adoption-centers`
2. Send the request

### 3. Test Breed-Specific Centers (GET /adoption-centers/<breed>)
1. Create a new GET request to `http://localhost:5000/adoption-centers/german_shepherd`
2. Send the request

### 4. Test Direct Redirect (GET /redirect/<breed>)
1. Create a new GET request to `http://localhost:5000/redirect/german%20shepherd`
2. Send the request - you'll get a 302 redirect to Petfinder with German Shepherd pre-searched!

### 5. Test Search URLs (GET /search-urls/<breed>)
1. Create a new GET request to `http://localhost:5000/search-urls/german%20shepherd`
2. Send the request

## Adoption Centers Database

The API includes a comprehensive database of real adoption centers:

### General Centers
- ASPCA (American Society for the Prevention of Cruelty to Animals)
- Humane Society of the United States
- Petfinder (Online Platform)
- Adopt-a-Pet.com (Online Platform)

### Breed-Specific Centers
- Golden Retriever Rescue of the Rockies
- Labrador Retriever Rescue
- German Shepherd Rescue of Orange County
- Bulldog Club of America Rescue
- Poodle Rescue of New England

## Error Handling

The API includes comprehensive error handling:
- File upload validation
- Image processing errors
- Model prediction errors
- Network errors

## Installation & Setup

1. Install required dependencies:
```bash
pip install flask numpy opencv-python pillow ultralytics tensorflow
```

2. Download the YOLO model (yolov8n.pt)
3. Place your trained breed classification model at the specified path
4. Update the model paths in the code if needed

5. Run the API:
```bash
python functionalApi.py
```

## Usage Examples

### Python Client Example
```python
import requests

# Upload image and get breed + adoption centers
with open('dog_image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/predict', files=files)
    result = response.json()
    
    print(f"Detected breed: {result['breed']}")
    print(f"Confidence: {result['confidence']}")
    print("Adoption centers:")
    for center in result['adoption_centers']:
        print(f"- {center['name']}: {center['website']}")
```

### cURL Example
```bash
# Upload image
curl -X POST -F "file=@dog_image.jpg" http://localhost:5000/predict

# Get adoption centers for specific breed
curl http://localhost:5000/adoption-centers/golden_retriever
```

## Response Format

All successful responses include:
- `breed`: Detected dog breed name
- `confidence`: Model confidence score (0-1)
- `adoption_centers`: Array of adoption center objects
- `message`: Human-readable message about the results

Each adoption center object includes:
- `name`: Organization name
- `website`: Official website URL
- `phone`: Contact phone number
- `location`: Geographic location
- `description`: Brief description of services

## Future Enhancements

- Add location-based filtering for adoption centers
- Include pricing information for breeders
- Add user reviews and ratings
- Implement geolocation services
- Add more breed-specific rescue organizations
