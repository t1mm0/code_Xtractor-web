#!/bin/bash

# Code Extractor Web UI Launcher
# Purpose: Launch the Flask web interface for code extraction
# Last Modified: 2024-12-19
# Completeness: 100%

# Function to check if port is available
check_port() {
    local port=$1
    if command -v lsof &> /dev/null; then
        lsof -i :$port > /dev/null 2>&1
        return $?
    elif command -v netstat &> /dev/null; then
        netstat -an | grep -q ":$port.*LISTEN"
        return $?
    else
        # Fallback: try to connect to the port
        (echo > /dev/tcp/localhost/$port) > /dev/null 2>&1
        return $?
    fi
}

# Find available port starting from 5000
PREFERRED_PORT=5000
PORT=$PREFERRED_PORT

if check_port $PORT; then
    echo "⚠️  Port $PORT is in use, checking for alternative..."
    for i in {1..10}; do
        TEST_PORT=$((PREFERRED_PORT + i))
        if ! check_port $TEST_PORT; then
            PORT=$TEST_PORT
            echo "✅ Found available port: $PORT"
            break
        fi
    done
    
    if [ $PORT -eq $PREFERRED_PORT ]; then
        echo "⚠️  Ports $PREFERRED_PORT-$((PREFERRED_PORT + 10)) are in use"
        echo "   The application will attempt to find an available port automatically"
    fi
else
    echo "✅ Port $PORT is available"
fi

echo ""
echo "🚀 Starting Code Block Extractor Web Interface..."
echo ""
echo "📍 Server will be available at: http://localhost:$PORT"
if [ $PORT -ne $PREFERRED_PORT ]; then
    echo "   (Port $PREFERRED_PORT was in use, using $PORT instead)"
fi
echo ""
echo "Features:"
echo "  • Drag & Drop markdown files"
echo "  • Real-time processing status"
echo "  • Automatic download of extracted code"
echo "  • Manual download link available"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "================================================"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Determine Python command (python3 or python)
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python not found. Please install Python 3."
    exit 1
fi

# Check if Flask is installed
if ! $PYTHON_CMD -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask is not installed. Installing dependencies..."
    if command -v pip3 &> /dev/null; then
        pip3 install -r requirements.txt
    else
        pip install -r requirements.txt
    fi
    echo ""
fi

# Start the Flask app
echo "🌐 Starting Flask server..."
$PYTHON_CMD web_app.py

