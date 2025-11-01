#!/bin/bash

# Blog Wire Startup Script

echo "🚀 Starting Blog Wire..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env is configured
if ! grep -q "sk-" .env 2>/dev/null; then
    echo "⚠️  Warning: OpenAI API key not configured in .env"
    echo ""
    echo "To configure:"
    echo "  1. Get API key from: https://platform.openai.com/api-keys"
    echo "  2. Edit .env file: nano .env"
    echo "  3. Add your key: OPENAI_API_KEY=sk-your-key-here"
    echo ""
    echo "Continue anyway? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check which mode to run
echo "Select mode:"
echo "  1) Web server only"
echo "  2) Web server + Scheduler (recommended)"
echo "  3) Test setup"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🌐 Starting web server..."
        echo "   Visit: http://localhost:5000"
        echo ""
        python app.py
        ;;
    2)
        echo ""
        echo "🌐 Starting web server and scheduler..."
        echo "   Web: http://localhost:5000"
        echo "   Scheduler: Running in background"
        echo ""
        echo "Press Ctrl+C to stop both services"
        echo ""

        # Start scheduler in background
        python scheduler.py &
        SCHEDULER_PID=$!

        # Start web server in foreground
        python app.py &
        WEB_PID=$!

        # Trap Ctrl+C to kill both processes
        trap "kill $SCHEDULER_PID $WEB_PID 2>/dev/null; exit" INT TERM

        # Wait for processes
        wait $WEB_PID $SCHEDULER_PID
        ;;
    3)
        echo ""
        echo "🧪 Running setup tests..."
        echo ""
        python test_setup.py
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
