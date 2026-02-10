#!/bin/bash
set -e

# Ensure we are in the script's directory (project root)
cd "$(dirname "$0")"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}>>> Starting Data Rebuild Process (Crawl + Index)...${NC}"

# Check for venv
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: venv not found. Please run deploy_ecs.sh first or create venv manually.${NC}"
    exit 1
fi

VENV_PYTHON="./venv/bin/python"

# 1. Run Crawler
echo -e "${YELLOW}[1/2] Running Crawler...${NC}"
$VENV_PYTHON src/crawler/byteplus_crawler.py

# 2. Run Index Builder
echo -e "${YELLOW}[2/2] Building Vector Index...${NC}"
$VENV_PYTHON src/retrieval/build_index.py

echo -e "${GREEN}>>> Data Rebuild Complete!${NC}"
echo "New data is ready for retrieval."
