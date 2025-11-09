#!/bin/bash
# PostgreSQL Setup Script for Concise API

echo "🚀 Setting up PostgreSQL for Concise API"
echo "========================================="
echo ""

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "✅ Docker is available"
    echo ""
    echo "Starting PostgreSQL container..."

    docker run -d \
      --name concise-postgres \
      -e POSTGRES_PASSWORD=postgres \
      -e POSTGRES_USER=postgres \
      -e POSTGRES_DB=concise_dev \
      -p 5432:5432 \
      postgres:15-alpine

    if [ $? -eq 0 ]; then
        echo "✅ PostgreSQL container started successfully!"
        echo ""
        echo "Waiting for PostgreSQL to be ready..."
        sleep 5

        echo "✅ PostgreSQL is ready!"
        echo ""
        echo "Connection details:"
        echo "  Host: localhost"
        echo "  Port: 5432"
        echo "  Database: concise_dev"
        echo "  User: postgres"
        echo "  Password: postgres"
        echo ""
        echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/concise_dev"
        echo ""
        echo "Next steps:"
        echo "1. Run migrations: alembic upgrade head"
        echo "2. Run tests: python test_system.py"
        echo "3. Start server: uvicorn app.main:app --reload"

    else
        echo "❌ Failed to start container. Container may already exist."
        echo ""
        echo "To remove existing container and try again:"
        echo "  docker rm -f concise-postgres"
        echo "  ./setup_postgres.sh"
    fi

else
    echo "❌ Docker not found"
    echo ""
    echo "Option 1: Install Docker"
    echo "  curl -fsSL https://get.docker.com | sh"
    echo ""
    echo "Option 2: Install PostgreSQL locally"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install -y postgresql postgresql-contrib"
    echo "  sudo systemctl start postgresql"
    echo "  sudo -u postgres psql -c \"CREATE DATABASE concise_dev;\""
    echo "  sudo -u postgres psql -c \"ALTER USER postgres PASSWORD 'postgres';\""
fi
