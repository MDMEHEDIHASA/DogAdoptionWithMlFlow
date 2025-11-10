#!/bin/bash

# Dog Breed Detection & Adoption Platform Setup Script
# This script will set up the entire project for you

set -e  # Exit on any error

echo "🐕 Dog Breed Detection & Adoption Platform Setup"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Node.js is installed
check_nodejs() {
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_status "Node.js is installed: $NODE_VERSION"
        
        # Check if version is 18+
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
        if [ "$NODE_MAJOR" -lt 20 ]; then
            print_warning "Node.js version 20+ recommended. Current: $NODE_VERSION"
        fi
    else
        print_error "Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    fi
}

# Check if npm is installed
check_npm() {
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_status "npm is installed: $NPM_VERSION"
    else
        print_error "npm is not installed. Please install npm."
        exit 1
    fi
}

# Check if Docker is installed (optional)
check_docker() {
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        print_status "Docker and Docker Compose are available"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker not found. You can still run the project without Docker."
        DOCKER_AVAILABLE=false
    fi
}

# Setup backend
setup_backend() {
    print_info "Setting up backend..."
    
    cd backend
    
    # Install dependencies
    print_info "Installing backend dependencies..."
    npm install
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_info "Creating .env file..."
        cp env.example .env
        print_status "Created .env file with default values"
    else
        print_status ".env file already exists"
    fi
    
    # Create uploads directory
    mkdir -p uploads
    print_status "Created uploads directory"
    
    cd ..
    print_status "Backend setup complete!"
}

# Setup frontend
setup_frontend() {
    print_info "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_info "Installing frontend dependencies..."
    npm install
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_info "Creating .env file..."
        echo "REACT_APP_API_URL=http://localhost:5000/api" > .env
        print_status "Created .env file with default values"
    else
        print_status ".env file already exists"
    fi
    
    cd ..
    print_status "Frontend setup complete!"
}

# Test the setup
test_setup() {
    print_info "Testing the setup..."
    
    # Test backend
    print_info "Starting backend server..."
    cd backend
    npm start &
    BACKEND_PID=$!
    
    # Wait for backend to start
    sleep 5
    
    # Test if backend is responding
    if curl -s http://localhost:5000/api/health > /dev/null; then
        print_status "Backend is running successfully!"
    else
        print_error "Backend failed to start"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    
    # Stop backend
    kill $BACKEND_PID 2>/dev/null || true
    
    cd ..
    print_status "Setup test completed successfully!"
}

# Main setup function
main() {
    echo ""
    print_info "Checking prerequisites..."
    
    # Check prerequisites
    check_nodejs
    check_npm
    check_docker
    
    echo ""
    print_info "Setting up the project..."
    
    # Setup backend and frontend
    setup_backend
    setup_frontend
    
    echo ""
    print_info "Testing the setup..."
    test_setup
    
    echo ""
    print_status "🎉 Setup completed successfully!"
    echo ""
    print_info "Next steps:"
    echo ""
    echo "1. Start the backend:"
    echo "   cd backend && npm run dev"
    echo ""
    echo "2. Start the frontend (in a new terminal):"
    echo "   cd frontend && npm start"
    echo ""
    echo "3. Open your browser and go to:"
    echo "   http://localhost:3000"
    echo ""
    
    if [ "$DOCKER_AVAILABLE" = true ]; then
        echo "4. Or use Docker:"
        echo "   docker-compose up -d"
        echo ""
    fi
    
    echo "📚 For more information, check:"
    echo "   - README.md (main documentation)"
    echo "   - QUICK_START.md (detailed setup guide)"
    echo "   - DEPLOYMENT.md (production deployment)"
    echo ""
    print_status "Happy coding! 🐕"
}

# Run main function
main
