#!/bin/bash

# Blog Wire Setup Script

echo "========================================="
echo "Blog Wire - Automated Blog Platform Setup"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python installation..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your:"
    echo "   - OPENAI_API_KEY"
    echo "   - ADSENSE_CLIENT_ID (optional)"
    echo "   - SECRET_KEY (for Flask sessions)"
else
    echo ""
    echo ".env file already exists, skipping..."
fi

# Create database
echo ""
echo "Initializing database..."
python << END
from app import app, db
with app.app_context():
    db.create_all()
    print("✓ Database initialized")
END

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your API keys"
echo "  2. Run the web app: python app.py"
echo "  3. Run the scheduler: python scheduler.py"
echo ""
echo "Access your blog at: http://localhost:5000"
echo ""
