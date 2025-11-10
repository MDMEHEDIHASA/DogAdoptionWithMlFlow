# 🚀 Deployment Guide

This guide covers various deployment options for the Dog Breed Detection & Adoption Platform.

## 📋 Prerequisites

- Node.js 20+ for frontend and backend Nodejs 18+ and npm
- Docker and Docker Compose (for containerized deployment)
- Domain name and SSL certificate (for production)
- Cloud provider account (AWS, GCP, Azure, Heroku, etc.)

## 🐳 Docker Deployment (Recommended)

### 1. Local Docker Deployment

```bash
# Clone the repository
git clone <repository-url>
cd dog-breed-detection

# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Production Docker Deployment

```bash
# Set production environment
export NODE_ENV=production
export FRONTEND_URL=https://your-domain.com

# Build and start
docker-compose -f docker-compose.prod.yml up -d
```

## ☁️ Cloud Deployment Options

### Heroku Deployment

#### Backend API
```bash
# Create Heroku app
heroku create dog-breed-api

# Set environment variables
heroku config:set NODE_ENV=production
heroku config:set FRONTEND_URL=https://your-frontend.herokuapp.com

# Deploy
git subtree push --prefix backend heroku main
```

#### Frontend
```bash
# Create Heroku app
heroku create dog-breed-frontend

# Set environment variables
heroku config:set REACT_APP_API_URL=https://your-api.herokuapp.com/api

# Deploy
git subtree push --prefix frontend heroku main
```

### AWS Deployment

#### Using Elastic Beanstalk

1. **Backend Deployment**
   ```bash
   # Install EB CLI
   pip install awsebcli
   
   # Initialize EB
   cd backend
   eb init
   eb create production
   eb deploy
   ```

2. **Frontend Deployment**
   ```bash
   # Build React app
   cd frontend
   npm run build
   
   # Deploy to S3 + CloudFront
   aws s3 sync build/ s3://your-bucket-name
   ```

#### Using ECS with Docker

```bash
# Build and push Docker images
docker build -t dog-breed-backend ./backend
docker build -t dog-breed-frontend ./frontend

# Tag for ECR
docker tag dog-breed-backend:latest your-account.dkr.ecr.region.amazonaws.com/dog-breed-backend:latest
docker tag dog-breed-frontend:latest your-account.dkr.ecr.region.amazonaws.com/dog-breed-frontend:latest

# Push to ECR
aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin your-account.dkr.ecr.region.amazonaws.com
docker push your-account.dkr.ecr.region.amazonaws.com/dog-breed-backend:latest
docker push your-account.dkr.ecr.region.amazonaws.com/dog-breed-frontend:latest
```

### Google Cloud Platform

#### Using Cloud Run

```bash
# Build and deploy backend
gcloud builds submit --tag gcr.io/your-project/dog-breed-backend ./backend
gcloud run deploy dog-breed-backend --image gcr.io/your-project/dog-breed-backend --platform managed --region us-central1

# Build and deploy frontend
gcloud builds submit --tag gcr.io/your-project/dog-breed-frontend ./frontend
gcloud run deploy dog-breed-frontend --image gcr.io/your-project/dog-breed-frontend --platform managed --region us-central1
```

### Azure Deployment

#### Using Container Instances

```bash
# Create resource group
az group create --name dog-breed-rg --location eastus

# Deploy backend
az container create --resource-group dog-breed-rg --name dog-breed-backend --image your-registry/dog-breed-backend --ports 5000

# Deploy frontend
az container create --resource-group dog-breed-rg --name dog-breed-frontend --image your-registry/dog-breed-frontend --ports 3000
```

## 🔧 Environment Configuration

### Production Environment Variables

#### Backend (.env)
```env
NODE_ENV=production
PORT=5000
FRONTEND_URL=https://your-frontend-domain.com
MAX_FILE_SIZE=10485760
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
LOG_LEVEL=info
```

#### Frontend (.env)
```env
REACT_APP_API_URL=https://your-api-domain.com/api
REACT_APP_ENVIRONMENT=production
```

## 🔒 SSL/TLS Configuration

### Using Let's Encrypt (Certbot)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Using Cloudflare

1. Add your domain to Cloudflare
2. Update DNS records to point to your server
3. Enable SSL/TLS encryption
4. Configure security settings

## 📊 Monitoring and Logging

### Application Monitoring

```bash
# Install PM2 for process management
npm install -g pm2

# Start application with PM2
pm2 start backend/server.js --name "dog-breed-api"
pm2 start frontend/build --name "dog-breed-frontend"

# Monitor
pm2 monit
pm2 logs
```

### Log Management

```bash
# Configure log rotation
sudo nano /etc/logrotate.d/dog-breed

# Add:
/var/log/dog-breed/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 root root
}
```

## 🚀 Performance Optimization

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/dog-breed
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Database Configuration (if needed)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb dog_breed_db

# Create user
sudo -u postgres createuser --interactive
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy Backend
      run: |
        cd backend
        docker build -t dog-breed-backend .
        docker push your-registry/dog-breed-backend:latest
    
    - name: Deploy Frontend
      run: |
        cd frontend
        docker build -t dog-breed-frontend .
        docker push your-registry/dog-breed-frontend:latest
```

## 🧪 Testing in Production

### Health Checks

```bash
# Test API health
curl https://your-api-domain.com/api/health

# Test frontend
curl https://your-frontend-domain.com

# Test breed detection
curl -X POST https://your-api-domain.com/api/breed/detect \
  -F "image=@test-dog.jpg"
```

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API performance
ab -n 1000 -c 10 https://your-api-domain.com/api/health

# Test file upload
ab -n 100 -c 5 -p test-image.jpg -T "multipart/form-data" https://your-api-domain.com/api/breed/detect
```

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors**
   ```bash
   # Check CORS configuration in backend
   # Ensure FRONTEND_URL is set correctly
   ```

2. **File Upload Issues**
   ```bash
   # Check file size limits
   # Verify upload directory permissions
   ```

3. **Memory Issues**
   ```bash
   # Monitor memory usage
   # Implement file cleanup
   # Use streaming for large files
   ```

### Log Analysis

```bash
# View application logs
pm2 logs dog-breed-api

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View system logs
sudo journalctl -u nginx -f
```

## 📈 Scaling

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    image: dog-breed-backend
    deploy:
      replicas: 3
    ports:
      - "5000-5002:5000"
  
  frontend:
    image: dog-breed-frontend
    deploy:
      replicas: 2
    ports:
      - "3000-3001:3000"
```

### Load Balancer Configuration

```nginx
upstream backend {
    server localhost:5000;
    server localhost:5001;
    server localhost:5002;
}

upstream frontend {
    server localhost:3000;
    server localhost:3001;
}
```

## 🔐 Security Checklist

- [ ] SSL/TLS certificates configured
- [ ] Security headers implemented
- [ ] Rate limiting enabled
- [ ] File upload validation
- [ ] CORS properly configured
- [ ] Environment variables secured
- [ ] Regular security updates
- [ ] Monitoring and alerting set up

---

**For additional support, check the main README.md or create an issue in the repository.**
