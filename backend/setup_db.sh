#!/bin/bash
# Quick database setup script

echo "🗄️  Setting up PostgreSQL database..."

# Create database
sudo -u postgres psql -c "CREATE DATABASE concise_dev;" 2>/dev/null || echo "✅ Database already exists"

# Set password (if needed)
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';" 2>/dev/null || echo "✅ Password already set"

echo ""
echo "✅ PostgreSQL setup complete!"
echo ""
echo "Database: concise_dev"
echo "User: postgres"
echo "Password: postgres"
