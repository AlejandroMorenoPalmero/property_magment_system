#!/bin/bash
# Script to start the Property Manager system with Docker Compose

echo "🚀 Starting Property Manager System with Docker Compose..."
echo ""

# Check if .env.docker exists
if [ ! -f .env.docker ]; then
    echo "⚠️  .env.docker not found. Creating from .env.docker.example..."
    cp .env.docker.example .env.docker
    echo "✅ Created .env.docker - Please customize it with your settings"
    echo ""
fi

# Load environment variables
export $(cat .env.docker | grep -v '^#' | xargs)

echo "📦 Building and starting containers..."
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "✅ Property Manager System is starting!"
echo ""
echo "📊 Service URLs:"
echo "   - Backend API:  http://localhost:8000"
echo "   - API Docs:     http://localhost:8000/docs"
echo "   - Frontend UI:  http://localhost:8501"
echo "   - MySQL DB:     localhost:3306"
echo ""
echo "📝 Useful commands:"
echo "   - View logs:        docker-compose logs -f"
echo "   - Stop services:    docker-compose down"
echo "   - Restart:          docker-compose restart"
echo "   - View status:      docker-compose ps"
echo ""
echo "🔍 Check service health:"
docker-compose ps
