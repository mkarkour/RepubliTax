#!/bin/bash
# To execute this script, run the following commands in your terminal:
# 1. Make it executable: chmod +x run_docker.sh
# 2. Run the script:     ./run_docker.sh

IMAGE_NAME="AutoMTO"

echo "🔨 Building the Docker image..."
docker build -t $IMAGE_NAME .

echo "✅ Image successfully built."

echo ""
echo "📦 Please select an action:"
echo "1. Run the application on port 8501"
echo "2. Open an interactive terminal in the container"
read -p "Your choice (1/2): " CHOICE

if [ "$CHOICE" == "1" ]; then
    echo "🚀 Starting the application on http://localhost:8501"
    docker run -p 8501:8501 $IMAGE_NAME
elif [ "$CHOICE" == "2" ]; then
    echo "🔧 Launching an interactive terminal in the container..."
    docker run -it $IMAGE_NAME bash
else
    echo "❌ Invalid selection."
fi
