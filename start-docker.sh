#!/bin/bash

# DevSecOps Knowledge Chat - Docker Compose Setup
# This script sets up and starts the application using Docker Compose

set -e

echo "🚀 Starting DevSecOps Knowledge Chat with Docker Compose..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
echo "🔍 Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    echo "Please start Docker Desktop first"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"

# Check if Ollama is accessible
echo "🔍 Checking Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${RED}❌ Ollama is not running!${NC}"
    echo "Please start Ollama first: https://ollama.ai"
    echo ""
    echo "On macOS/Linux:"
    echo "  brew install ollama"
    echo "  ollama serve"
    echo ""
    exit 1
fi
echo -e "${GREEN}✅ Ollama is running${NC}"

# Check if model is available
echo "🔍 Checking for qwen2.5:14b model..."
if ! ollama list | grep -q "qwen2.5:14b"; then
    echo -e "${YELLOW}⚠️  Model qwen2.5:14b not found${NC}"
    echo "Pulling model (this may take a while)..."
    ollama pull qwen2.5:14b
fi
echo -e "${GREEN}✅ Model is available${NC}"

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file${NC}"
fi

# Build and start containers
echo ""
echo "🐳 Building and starting Docker containers..."
docker-compose up --build

# Cleanup on exit
trap "docker-compose down" EXIT
