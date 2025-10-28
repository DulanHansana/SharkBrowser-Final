#!/bin/bash

# SharkBrowser API EC2 Deployment Script

echo "🦈 Deploying SharkBrowser API on EC2..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update -y

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
fi

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Build chromium-cdp image
echo "🔨 Building chromium-cdp image..."
docker build -f chromium-cdp.Dockerfile -t chromium-cdp .

if [ $? -eq 0 ]; then
    echo "✅ chromium-cdp image built successfully"
else
    echo "❌ Failed to build chromium-cdp image"
    exit 1
fi

# Build API image
echo "🔨 Building SharkBrowser API image..."
docker build -t sharkbrowser-api .

if [ $? -eq 0 ]; then
    echo "✅ SharkBrowser API image built successfully"
else
    echo "❌ Failed to build SharkBrowser API image"
    exit 1
fi

# Run the API
echo "🚀 Starting SharkBrowser API..."
docker run -d \
    --name sharkbrowser \
    -p 8000:8000 \
    -p 9000-9020:9000-9020 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --restart unless-stopped \
    sharkbrowser-api

if [ $? -eq 0 ]; then
    echo "✅ SharkBrowser API started successfully!"
    echo ""
    echo "🌐 API is now running at:"
    echo "   http://$(curl -s https://api.ipify.org):8000"
    echo "   http://$(curl -s https://api.ipify.org):8000/docs"
    echo ""
    echo "📋 Available endpoints:"
    echo "   POST /v1/sessions - Create browser session"
    echo "   POST /v1/sessions/multiple - Create 5 browsers"
    echo "   GET /v1/sessions - List sessions"
    echo "   POST /v1/sessions/release - Release session"
    echo "   GET /health - Health check"
    echo ""
    echo "🔧 To check logs: docker logs sharkbrowser"
    echo "🛑 To stop: docker stop sharkbrowser"
else
    echo "❌ Failed to start SharkBrowser API"
    exit 1
fi
