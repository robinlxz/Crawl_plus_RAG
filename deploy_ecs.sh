#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}>>> Starting ECS Deployment Script for BytePlus RAG Assistant...${NC}"

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
VENV_PYTHON="./venv/bin/python"
VENV_PIP="./venv/bin/pip"

# 3. Install Python Dependencies
echo -e "${YELLOW}[3/6] Installing Python requirements...${NC}"
$VENV_PIP install --upgrade pip
# Use Tsinghua mirror for speed in China regions (optional, can be removed if global)
$VENV_PIP install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

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

# 6. Start Service
echo -e "${YELLOW}[6/6] Starting Streamlit Service...${NC}"

# Kill existing streamlit process if running
if pgrep -f "streamlit run src/web_ui.py" > /dev/null; then
    echo "Stopping existing RAG service..."
    pkill -f "streamlit run src/web_ui.py"
    sleep 2
fi

# Start in background with nohup
nohup ./venv/bin/streamlit run src/web_ui.py --server.port 80 --server.address 0.0.0.0 > rag_service.log 2>&1 &

echo -e "${GREEN}>>> Deployment Complete!${NC}"
echo -e "Service is running in background. Logs are being written to ${YELLOW}rag_service.log${NC}"
echo -e "Access your service at: http://<YOUR_ECS_IP>"
