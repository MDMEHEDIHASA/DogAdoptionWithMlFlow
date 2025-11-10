#!/bin/bash

# Dog Breed Detection & Adoption Platform Run Script
# This script will start the entire application

set -e  # Exit on any error

echo "🚀 Starting Dog Breed Detection & Adoption Platform"
echo "================================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    if check_port $port; then
        print_warning "Port $port is in use. Attempting to free it..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Check if we should use Docker
if [ "$1" = "docker" ]; then
    print_info "Starting with Docker..."
    
    # Check if Docker is available
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose not found. Please install Docker and Docker Compose."
        exit 1
    fi
    
    # Start with Docker
    docker-compose up -d
    
    print_status "Application started with Docker!"
    echo ""
    print_info "Services running:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend:  http://localhost:5000"
    echo ""
    print_info "To view logs: docker-compose logs -f"
    print_info "To stop: docker-compose down"
    
else
    print_info "Starting with Node.js..."
    
    # Check if Node.js is available
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js not found. Please install Node.js 18+"
        exit 1
    fi
    
    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        echo "❌ npm not found. Please install npm"
        exit 1
    fi
    
    # Kill any existing processes on ports 3000 and 5000
    kill_port 3000
    kill_port 5000
    
    # Start backend
    print_info "Starting backend server..."
    cd backend
    npm start &
    BACKEND_PID=$!
    
    # Wait for backend to start
    print_info "Waiting for backend to start..."
    sleep 5
    
    # Check if backend is running
    if check_port 5000; then
        print_status "Backend is running on port 5000"
    else
        print_warning "Backend may not have started properly"
    fi
    
    # Start frontend
    print_info "Starting frontend server..."
    cd ../frontend
    npm start &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    print_info "Waiting for frontend to start..."
    sleep 5
    
    # Check if frontend is running
    if check_port 3000; then
        print_status "Frontend is running on port 3000"
    else
        print_warning "Frontend may not have started properly"
    fi
    
    print_status "Application started successfully!"
    echo ""
    print_info "Services running:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend:  http://localhost:5000"
    echo ""
    print_info "Process IDs:"
    echo "  Backend PID:  $BACKEND_PID"
    echo "  Frontend PID: $FRONTEND_PID"
    echo ""
    print_info "To stop the application:"
    echo "  kill $BACKEND_PID $FRONTEND_PID"
    echo ""
    print_info "Or press Ctrl+C to stop this script"
    
    # Wait for user to stop
    echo ""
    print_info "Press Ctrl+C to stop all services..."
    
    # Function to cleanup on exit
    cleanup() {
        print_info "Stopping services..."
        kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
        print_status "Services stopped"
        exit 0
    }
    
    # Set trap for cleanup
    trap cleanup SIGINT SIGTERM
    
    # Wait for processes
    wait
fi
