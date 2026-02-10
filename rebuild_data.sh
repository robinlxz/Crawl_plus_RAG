#!/bin/bash
set -e

# Ensure we are in the script's directory (project root)
cd "$(dirname "$0")"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}>>> Starting Data Rebuild Process (Crawl + Process + Index)...${NC}"

# Check for venv
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: venv not found. Please run deploy_ecs.sh first or create venv manually.${NC}"
    exit 1
fi

VENV_PYTHON="./venv/bin/python"

# 1. Run Crawler (Conditional)
RAW_DATA_DIR="data/raw/byteplus_ecs"
SHOULD_CRAWL=true

if [ -d "$RAW_DATA_DIR" ] && [ "$(ls -A $RAW_DATA_DIR 2>/dev/null)" ]; then
    echo -e "${YELLOW}Raw data detected in $RAW_DATA_DIR.${NC}"
    read -p "Do you want to re-crawl data? (y/N): " choice
    case "$choice" in 
        y|Y ) 
            echo "Re-crawling..."
            SHOULD_CRAWL=true
            ;;
        * ) 
            echo "Skipping crawler..."
            SHOULD_CRAWL=false
            ;;
    esac
else
    echo "No raw data found. Starting crawler..."
    SHOULD_CRAWL=true
fi

if [ "$SHOULD_CRAWL" = true ]; then
    echo -e "${YELLOW}[1/3] Running Crawler...${NC}"
    $VENV_PYTHON src/crawler/byteplus_crawler.py
else
    echo -e "${YELLOW}[1/3] Crawler Skipped.${NC}"
fi

# 2. Run Processor (Cleaning & Chunking)
echo -e "${YELLOW}[2/3] Processing Data...${NC}"
$VENV_PYTHON src/processor/byteplus_parser.py

# 3. Run Index Builder
echo -e "${YELLOW}[3/3] Building Vector Index...${NC}"
$VENV_PYTHON src/retrieval/build_index.py

echo -e "${GREEN}>>> Data Rebuild Complete!${NC}"
echo "New data is ready for retrieval."
