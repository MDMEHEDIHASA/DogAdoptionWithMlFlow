# 🚀 Quick Start Guide

This guide will help you get the Dog Breed Detection & Adoption Platform running in minutes.

## 📋 Prerequisites

Before starting, make sure you have:
- **Node.js 18+ For Backend and frontend 20+** and npm installed
- **Python 3.8+** (for your ML model integration)
- **Git** for cloning the repository

## 🎯 Option 1: Quick Local Development (Recommended for Testing)

### Step 1: Setup Backend

```bash
# Navigate to backend directory
cd backend

# Install dependencies
npm install

# Copy environment file
cp env.example .env

# Edit .env file (optional - defaults work for local development)
# PORT=5000
# NODE_ENV=development
# FRONTEND_URL=http://localhost:3000

# Start the backend server
npm run dev
```

**Backend will be running at:** http://localhost:5000

### Step 2: Setup Frontend (New Terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the React development server
npm start
```

**Frontend will be running at:** http://localhost:3000

### Step 3: Test the Application

1. Open http://localhost:3000 in your browser
2. Upload a dog image
3. See breed detection results
4. Click adoption center links

## 🐳 Option 2: Docker Deployment (Recommended for Production)

### Prerequisites
- Docker and Docker Compose installed

### Step 1: Clone and Setup

```bash
# Clone the repository (if not already done)
git clone <your-repository-url>
cd dog-breed-detection

# Create environment files
cp backend/env.example backend/.env
cp frontend/.env.example frontend/.env
```

### Step 2: Configure Environment Variables

**Backend (.env):**
```env
PORT=5000
NODE_ENV=production
FRONTEND_URL=http://localhost:3000
MAX_FILE_SIZE=10485760
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

**Frontend (.env):**
```env
REACT_APP_API_URL=http://localhost:5000/api
```

### Step 3: Build and Run with Docker

```bash
# Build and start all services
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- API Health: http://localhost:5000/api/health

## 🔧 Option 3: Production Deployment

### For Heroku Deployment

#### Backend Deployment
```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name-api

# Set environment variables
heroku config:set NODE_ENV=production
heroku config:set FRONTEND_URL=https://your-app-name-frontend.herokuapp.com

# Deploy backend
cd backend
git subtree push --prefix backend heroku main
```

#### Frontend Deployment
```bash
# Create another Heroku app for frontend
heroku create your-app-name-frontend

# Set environment variables
heroku config:set REACT_APP_API_URL=https://your-app-name-api.herokuapp.com/api

# Deploy frontend
cd frontend
git subtree push --prefix frontend heroku main
```

### For AWS/GCP/Azure

Follow the detailed instructions in `DEPLOYMENT.md`

## 🧪 Testing the Application

### 1. Test API Health
```bash
curl http://localhost:5000/api/health
```

**Expected Response:**
```json
{
  "status": "OK",
  "timestamp": "2024-01-20T10:30:00.000Z",
  "uptime": 123.456,
  "environment": "development"
}
```

### 2. Test Breed Detection
```bash
# Upload an image (replace with your image path)
curl -X POST http://localhost:5000/api/breed/detect \
  -F "image=@/path/to/your/dog/image.jpg"
```

### 3. Test Adoption Centers
```bash
# Get adoption centers for a specific breed
curl http://localhost:5000/api/adoption/centers/german%20shepherd

# Get all adoption centers
curl http://localhost:5000/api/adoption/centers
```

### 4. Test Direct Redirect
```bash
# This will redirect you to Petfinder with German Shepherd pre-searched
curl -L http://localhost:5000/api/adoption/redirect/german%20shepherd
```

## 🔧 Integration with Your Python ML Model

### Step 1: Update the Breed Detection Service

Edit `backend/services/breedDetection.js`:

```javascript
// Replace the mock implementation with your actual Python model
async function detectBreed(imagePath) {
  try {
    // Option 1: Call Python script directly
    const result = await callPythonModel(imagePath);
    return result;
    
    // Option 2: Call your existing functionalApi.py
    // const result = await callFlaskAPI(imagePath);
    // return result;
    
  } catch (error) {
    console.error('Breed detection error:', error);
    return {
      error: 'Breed detection failed',
      message: 'Unable to process the image for breed detection.'
    };
  }
}

// Function to call your Python model
async function callPythonModel(imagePath) {
  return new Promise((resolve, reject) => {
    const { spawn } = require('child_process');
    const path = require('path');
    
    const pythonProcess = spawn('python', [
      path.join(__dirname, '../ml/breed_detector.py'),
      imagePath
    ]);
    
    let result = '';
    let error = '';
    
    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}: ${error}`));
        return;
      }
      
      try {
        const parsedResult = JSON.parse(result);
        resolve(parsedResult);
      } catch (parseError) {
        reject(new Error(`Failed to parse Python output: ${parseError.message}`));
      }
    });
  });
}
```

### Step 2: Create Python Integration Script

Create `backend/ml/breed_detector.py`:

```python
import sys
import json
import os
from your_existing_model import predict_breed  # Import your existing function

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid arguments"}))
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        # Use your existing predict_breed function
        result = predict_breed(image_path)
        
        # Return JSON result
        print(json.dumps(result))
        
    except Exception as e:
        error_result = {
            "error": "Breed detection failed",
            "message": str(e)
        }
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Port Already in Use
```bash
# Kill process using port 5000
lsof -ti:5000 | xargs kill -9

# Or use different port
PORT=5001 npm start
```

#### 2. CORS Errors
```bash
# Check if FRONTEND_URL is set correctly in backend/.env
FRONTEND_URL=http://localhost:3000
```

#### 3. File Upload Issues
```bash
# Check file size limits
# Ensure uploads directory exists
mkdir -p backend/uploads
```

#### 4. Docker Issues
```bash
# Clean up Docker containers
docker-compose down
docker system prune -a

# Rebuild containers
docker-compose up --build
```

#### 5. Node Modules Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Check Service Status

```bash
# Check if backend is running
curl http://localhost:5000/api/health

# Check if frontend is running
curl http://localhost:3000

# Check Docker containers
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend
```

## 📊 Performance Monitoring

### Check Application Performance

```bash
# Monitor CPU and memory usage
htop

# Check disk space
df -h

# Monitor network connections
netstat -tulpn | grep :5000
netstat -tulpn | grep :3000
```

### API Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API performance
ab -n 100 -c 10 http://localhost:5000/api/health

# Test file upload (if you have a test image)
ab -n 10 -c 2 -p test-image.jpg -T "multipart/form-data" http://localhost:5000/api/breed/detect
```

## 🔄 Development Workflow

### Making Changes

1. **Backend Changes:**
   ```bash
   cd backend
   npm run dev  # Auto-restarts on changes
   ```

2. **Frontend Changes:**
   ```bash
   cd frontend
   npm start    # Hot reload on changes
   ```

3. **Docker Changes:**
   ```bash
   # Rebuild and restart
   docker-compose up --build
   ```

### Git Workflow

```bash
# Make changes
git add .
git commit -m "Your changes"
git push origin main

# For Docker deployment
docker-compose up --build
```

## 📞 Getting Help

If you encounter issues:

1. **Check the logs:**
   ```bash
   # Backend logs
   npm run dev  # or docker-compose logs backend
   
   # Frontend logs
   npm start    # or docker-compose logs frontend
   ```

2. **Verify all services are running:**
   - Backend: http://localhost:5000/api/health
   - Frontend: http://localhost:3000

3. **Check environment variables:**
   - Backend: `backend/.env`
   - Frontend: `frontend/.env`

4. **Review the documentation:**
   - `README.md` - Main documentation
   - `DEPLOYMENT.md` - Detailed deployment guide
   - `API_DOCUMENTATION.md` - API reference

---

**🎉 You're all set! Your Dog Breed Detection & Adoption Platform should now be running successfully.**
