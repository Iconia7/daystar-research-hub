#!/bin/bash

# ResearchHub Backend Setup Script
# This script sets up all the critical backend fixes and installs dependencies

set -e  # Exit on error

echo "🚀 ResearchHub Backend Setup Script"
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Navigate to project directory
cd /home/bantu/Documents/ResearchHub

echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "🗄️  Running database migrations..."
python manage.py migrate

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Create a superuser: python manage.py createsuperuser"
echo "2. Start the server: python manage.py runserver"
echo "3. Access the API: http://localhost:8000/api/"
echo "4. View documentation: http://localhost:8000/api/docs/"
echo ""
