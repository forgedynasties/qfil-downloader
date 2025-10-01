#!/bin/bash

# QFIL Downloader - Container Update Script
# Usage: ./update.sh [quick|clean|rolling]

set -e

UPDATE_TYPE=${1:-quick}
COMPOSE_FILE="docker-compose.yml"

echo "🔄 QFIL Downloader Container Update"
echo "Update type: $UPDATE_TYPE"
echo "=================================="

case $UPDATE_TYPE in
    "quick")
        echo "📦 Performing quick update (code changes only)..."
        
        # Backup current projects.json if it exists
        if [ -f "projects.json" ]; then
            echo "💾 Backing up projects.json..."
            cp projects.json projects.json.backup.$(date +%Y%m%d_%H%M%S)
        fi
        
        echo "🛑 Stopping containers..."
        docker-compose down
        
        echo "🔨 Building new image..."
        docker-compose build --no-cache
        
        echo "🚀 Starting updated containers..."
        docker-compose up -d
        
        echo "⏳ Waiting for health check..."
        sleep 15
        
        echo "🔍 Checking container status..."
        docker-compose ps
        ;;
        
    "clean")
        echo "🧹 Performing clean update (removes all data)..."
        
        # Backup projects.json
        if [ -f "projects.json" ]; then
            echo "💾 Backing up projects.json..."
            cp projects.json projects.json.backup.$(date +%Y%m%d_%H%M%S)
        fi
        
        echo "🛑 Stopping and removing containers..."
        docker-compose down --volumes --remove-orphans
        
        echo "🗑️ Removing old images..."
        docker image prune -f
        docker volume prune -f
        
        echo "🔨 Building fresh image..."
        docker-compose build --no-cache --pull
        
        echo "🚀 Starting fresh containers..."
        docker-compose up -d
        
        echo "⏳ Waiting for health check..."
        sleep 20
        
        echo "🔍 Checking container status..."
        docker-compose ps
        ;;
        
    "rolling")
        echo "🔄 Performing rolling update (zero downtime)..."
        
        echo "🔨 Building new image..."
        docker-compose build --no-cache
        
        echo "📈 Scaling up with new version..."
        docker-compose up -d --scale qfil-downloader=2 --no-recreate
        
        echo "⏳ Waiting for new container to be healthy..."
        sleep 30
        
        echo "📉 Scaling down to single instance..."
        docker-compose up -d --scale qfil-downloader=1
        
        echo "🔍 Final status check..."
        docker-compose ps
        ;;
        
    *)
        echo "❌ Invalid update type: $UPDATE_TYPE"
        echo "Valid options: quick, clean, rolling"
        exit 1
        ;;
esac

echo ""
echo "✅ Update completed successfully!"
echo "🌐 Application available at: http://localhost:5000"
echo "📊 View logs with: docker-compose logs -f"
echo "🔧 Manage projects at: http://localhost:5000/manage"

# Health check
echo ""
echo "🏥 Performing health check..."
if curl -f -s http://localhost:5000/ > /dev/null; then
    echo "✅ Health check passed - Application is running correctly"
else
    echo "❌ Health check failed - Please check logs with: docker-compose logs"
    exit 1
fi