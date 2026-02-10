#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.

# Ensure we are in the script's directory (project root)
cd "$(dirname "$0")"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}>>> Starting ECS Deployment Script (Systemd Version) for BytePlus RAG Assistant...${NC}"

# 1. System Check & Dependencies
echo -e "${YELLOW}[1/6] Checking system dependencies...${NC}"
if command -v apt-get >/dev/null; then
    echo "Detected apt-based system (Ubuntu/Debian/veLinux). Updating..."
    sudo apt-get update -qq
    sudo apt-get install -y python3-venv python3-pip git
else
    echo -e "${RED}Error: This script supports Ubuntu/Debian/veLinux (apt) only.${NC}"
    echo "Please install python3-venv, python3-pip, and git manually."
    exit 1
fi

# 2. Python Virtual Environment
echo -e "${YELLOW}[2/6] Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    echo "Creating venv..."
    python3 -m venv venv
else
    echo "venv already exists."
fi

# Use absolute path for python executable in venv
PROJECT_ROOT=$(pwd)
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"
VENV_PIP="$PROJECT_ROOT/venv/bin/pip"
STREAMLIT_BIN="$PROJECT_ROOT/venv/bin/streamlit"

# 3. Install Python Dependencies
echo -e "${YELLOW}[3/6] Installing Python requirements...${NC}"
$VENV_PIP install --upgrade pip
# Removed Tsinghua mirror for overseas ECS
$VENV_PIP install -r requirements.txt

# 4. Environment Configuration Check
echo -e "${YELLOW}[4/6] Checking configuration...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create a .env file with your API keys before running this script."
    echo "Example:"
    echo "DEEPSEEK_API_KEY=sk-..."
    echo "DOUBAO_API_KEY=sk-..."
    exit 1
fi

# 5. Data Initialization (Crawler & Indexing)
echo -e "${YELLOW}[5/6] Initializing RAG data...${NC}"
INDEX_FILE="data/byteplus.index"

if [ -f "$INDEX_FILE" ]; then
    echo "Index file exists. Skipping crawling and indexing."
    echo "To force rebuild, run: rm $INDEX_FILE"
else
    echo "Index not found. Starting fresh build..."
    
    # Run Crawler
    echo ">>> Running Crawler..."
    $VENV_PYTHON src/crawler/byteplus_crawler.py
    
    # Run Index Builder
    echo ">>> Building Vector Index..."
    $VENV_PYTHON src/retrieval/build_index.py
fi

# 6. Systemd Service Setup
echo -e "${YELLOW}[6/6] Configuring Systemd Service...${NC}"

SERVICE_FILE="rag.service"
TARGET_SERVICE_PATH="/etc/systemd/system/rag.service"

if [ ! -f "$SERVICE_FILE" ]; then
    echo -e "${RED}Error: $SERVICE_FILE not found in current directory.${NC}"
    exit 1
fi

# Get current user to run the service
CURRENT_USER=$(whoami)
echo "Service will run as user: $CURRENT_USER"

# Update paths and user in rag.service dynamically
echo "Updating service file paths to: $PROJECT_ROOT"
# Create a temporary service file with correct paths and user
sed "s|WorkingDirectory=.*|WorkingDirectory=$PROJECT_ROOT|g" $SERVICE_FILE > rag.service.tmp
sed "s|ExecStart=.*|ExecStart=$STREAMLIT_BIN run src/web_ui.py --server.port 8501 --server.address 0.0.0.0|g" rag.service.tmp > rag.service.tmp2
sed "s|User=.*|User=$CURRENT_USER|g" rag.service.tmp2 > rag.service.tmp3
sed "s|EnvironmentFile=.*|EnvironmentFile=$PROJECT_ROOT/.env|g" rag.service.tmp3 > rag.service.final

echo "Installing service to $TARGET_SERVICE_PATH..."
sudo mv rag.service.final $TARGET_SERVICE_PATH
rm rag.service.tmp rag.service.tmp2 rag.service.tmp3

# Reload systemd and enable service
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload
echo "Enabling rag.service..."
sudo systemctl enable rag.service
echo "Restarting rag.service..."
sudo systemctl restart rag.service

echo -e "${GREEN}>>> Deployment Complete!${NC}"
echo -e "Service status:"
sudo systemctl status rag.service --no-pager | head -n 10
echo -e "\nLogs available at: /var/log/rag_assistant.log"
echo -e "Access your service at: http://<YOUR_ECS_IP>:8501"
