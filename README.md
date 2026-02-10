# BytePlus ECS RAG Assistant

[中文说明](#byteplus-ecs-rag-assistant-中文说明)

A Retrieval-Augmented Generation (RAG) intelligent QA system designed for BytePlus ECS documentation. This project implements a complete pipeline from data crawling, processing, and vector retrieval to an interactive Web UI, supporting mixed English-Chinese queries and flexible model configuration.

## 🌟 Features

- **Multi-language Retrieval**: Powered by `paraphrase-multilingual-MiniLM-L12-v2`, supporting Chinese queries to retrieve English documentation with strong cross-lingual semantic understanding.
- **Interactive Web UI**: Built with **Streamlit**, providing a ChatGPT-like conversational experience. Retrieved reference documents and source links are displayed below the answer to ensure transparency.
- **Flexible LLM Backend**: Out-of-the-box support for **DeepSeek** and **Doubao** models (via BytePlus ModelArk).
- **Deployment Friendly**: Refactored codebase eliminates hardcoded paths, supporting execution in any directory or on ECS servers.
- **Secure Configuration**: Key configurations (like API Keys and Model Endpoints) are prioritized from environment variables to prevent accidental commits.

## 🏗 Architecture

1.  **Crawler**: `src/crawler/` - Crawls BytePlus official documentation.
2.  **Processor**: `src/processor/` - Parses HTML/JSON and chunks text.
3.  **Embedding**: `src/embedding/` - Converts text to normalized vectors using SentenceTransformers.
4.  **Indexing**: `src/retrieval/` - Builds vector indices using FAISS (Inner Product / Cosine Similarity).
5.  **RAG Loop**:
    *   **Retrieve**: Fetches Top-K relevant documents.
    *   **Generate**: Constructs context with URLs and prompts the LLM to generate answers with source links.

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- BytePlus ModelArk service enabled with an API Key.

### 2. Installation

Clone the repository and install dependencies:

```bash
cd rag_project  # Ensure you are in the project root
pip install -r requirements.txt
```

### 3. Configuration (.env)

Create a `.env` file in the project root and fill in your keys and model endpoints:

```ini
# Example .env content

# API Keys (Required)
# Get API Key from BytePlus Console
DEEPSEEK_API_KEY=your_sk_key_here
DOUBAO_API_KEY=your_sk_key_here

# Model Overrides (Recommended)
# Note: Values here are "Online Inference Endpoint IDs", not model names.
# Format: ep-202xxxxxxx-xxxxx
# Path: BytePlus Console -> ModelArk -> Online Inference -> Endpoint Details
DEEPSEEK_MODEL=ep-202xxxxxxx-xxxxx
DOUBAO_MODEL=ep-202xxxxxxx-xxxxx
```

> **Important**: The system prioritizes `_MODEL` configurations from environment variables. Even if `config.yaml` is reset, your configuration will persist as long as the `.env` file exists.

### 4. Start Web UI

Run the Streamlit application:

```bash
streamlit run src/web_ui.py
```

Open `http://localhost:8501` in your browser to start chatting.

## 📂 Project Structure

```text
rag_project/
├── .env                  # Keys & Local Config (Not in git)
├── config/
│   └── rag_config.yaml   # Default Configuration
├── data/
│   ├── raw/              # Raw Crawled JSON Data
│   ├── processed/        # Processed Text Chunks
│   ├── byteplus.index    # FAISS Vector Index
│   └── byteplus_meta.json# Index Metadata
├── src/
│   ├── crawler/          # Data Crawler
│   ├── processor/        # Data Cleaning & Chunking
│   ├── embedding/        # Embedding Model Wrapper
│   ├── retrieval/        # Index Building & Search Engine
│   ├── generator/        # LLM Client & Prompt Builder
│   ├── utils/            # Path Helpers
│   ├── web_ui.py         # Web UI Entry Point
│   └── rag_test.py       # End-to-End Test Script
└── requirements.txt
```

## 🛠 Developer Guide

### Rebuild Index
If you change the Embedding model or update documentation data, you must rebuild the index:

```bash
# Recomputes all vectors and saves the .index file
python src/retrieval/build_index.py
```

### Test Retrieval
Test retrieval quality without consuming LLM tokens:

```bash
python src/retrieval/query_test.py
```

### Verify API Configuration
Check if API Key and Endpoint ID are valid:

```bash
python src/test_api_key.py
```

## 📝 Configuration Priority

The system loads configuration in the following order:

1.  **Environment Variables (.env)**: `DEEPSEEK_MODEL`, `DEEPSEEK_API_KEY`, etc. (Highest Priority).
2.  **Config File**: `config/rag_config.yaml`.
3.  **Code Defaults**: (Fallback only).

It is recommended to always manage sensitive information and environment-specific configurations via `.env`.

---

# BytePlus ECS RAG Assistant (中文说明)

这是一个基于 RAG (Retrieval-Augmented Generation) 架构的智能问答系统，专为 BytePlus ECS 文档设计。该项目实现了从数据抓取、处理、向量检索到交互式 Web UI 的完整链路，支持中英文混合提问，并具备灵活的模型配置能力。

## 🌟 核心特性 (Features)

- **多语言检索支持**: 底层采用 `paraphrase-multilingual-MiniLM-L12-v2` 向量模型，支持用中文提问来检索英文文档，跨语言语义理解能力强。
- **交互式 Web 界面**: 基于 **Streamlit** 构建，提供类 ChatGPT 的对话体验。回答下方会自动展示“检索到的参考文档”及原文链接，确保回答透明可信。
- **灵活的 LLM 后端**: 开箱支持 **DeepSeek** 和 **Doubao (豆包)** 模型（通过 BytePlus ModelArk 调用）。
- **部署友好**: 代码库经过重构，消除了硬编码路径，支持在任意目录或 ECS 服务器上直接运行。
- **配置安全**: 关键配置（如 API Key 和 Model Endpoint）优先从环境变量读取，避免代码变更导致配置丢失。

## 🏗 架构设计

1.  **Crawler (爬虫)**: `src/crawler/` - 抓取 BytePlus 官方文档。
2.  **Processor (处理)**: `src/processor/` - 解析 HTML/JSON，切分文本块 (Chunks)。
3.  **Embedding (向量化)**: `src/embedding/` - 使用 SentenceTransformers 将文本转为向量 (Normalized)。
4.  **Indexing (索引)**: `src/retrieval/` - 使用 FAISS 构建向量索引 (Inner Product / Cosine Similarity)。
5.  **RAG Loop (生成)**:
    *   **Retrieve**: 检索 Top-K 相关文档。
    *   **Generate**: 拼接包含 URL 的 Context，提示 LLM 生成带链接的回答。

## 🚀 快速开始 (Quick Start)

### 1. 环境准备
- Python 3.9+
- 已开通 BytePlus ModelArk 服务，并获取 API Key。

### 2. 安装依赖

克隆代码仓库并安装依赖：

```bash
cd rag_project  # 确保进入项目根目录
pip install -r requirements.txt
```

### 3. 配置环境 (.env)

在项目根目录下创建一个 `.env` 文件，填入你的密钥和模型接入点：

```ini
# .env 文件内容示例

# API Keys (必须)
# 从火山引擎/BytePlus 控制台获取 API Key
DEEPSEEK_API_KEY=your_sk_key_here
DOUBAO_API_KEY=your_sk_key_here

# Model Overrides (推荐)
# 注意：这里的值不是模型名，而是你在 ModelArk 平台创建的“在线推理接入点 ID”
# 格式通常为: ep-202xxxxxxx-xxxxx
# 获取路径: BytePlus Console -> ModelArk -> 在线推理 (Online Inference) -> 接入点详情
DEEPSEEK_MODEL=ep-202xxxxxxx-xxxxx
DOUBAO_MODEL=ep-202xxxxxxx-xxxxx
```

> **重要提示**: 系统会优先读取环境变量中的 `_MODEL` 配置。即使代码中的 `config.yaml` 被重置，只要 `.env` 文件存在，你的配置就不会丢失。

### 4. 启动 Web UI

运行 Streamlit 应用：

```bash
streamlit run src/web_ui.py
```

浏览器访问 `http://localhost:8501` 即可开始对话。

## 📂 项目结构

```text
rag_project/
├── .env                  # 密钥与本地配置 (不上传 git)
├── config/
│   └── rag_config.yaml   # 默认配置文件
├── data/
│   ├── raw/              # 爬取的原始 JSON 数据
│   ├── processed/        # 处理后的文本块
│   ├── byteplus.index    # FAISS 向量索引文件
│   └── byteplus_meta.json# 索引对应的元数据
├── src/
│   ├── crawler/          # 数据获取模块
│   ├── processor/        # 数据清洗与切分
│   ├── embedding/        # Embedding 模型封装 (单例)
│   ├── retrieval/        # 索引构建与检索引擎
│   ├── generator/        # LLM 客户端与 Prompt 构建
│   ├── utils/            # 路径管理工具 (Path Helpers)
│   ├── web_ui.py         # Web 界面入口
│   └── rag_test.py       # 端到端测试脚本
└── requirements.txt
```

## 🛠 开发者指南

### 重建索引 (Rebuild Index)
如果你更改了 Embedding 模型或更新了文档数据，必须重建索引：

```bash
# 这将重新计算所有向量并保存 .index 文件
python src/retrieval/build_index.py
```

### 测试检索效果
仅测试检索质量，不消耗 LLM Token：

```bash
python src/retrieval/query_test.py
```

### 验证 API 配置
检查 API Key 和 Endpoint ID 是否有效：

```bash
python src/test_api_key.py
```

## 📝 配置优先级逻辑

系统按以下顺序加载配置：

1.  **环境变量 (.env)**: `DEEPSEEK_MODEL`, `DEEPSEEK_API_KEY` 等 (优先级最高)。
2.  **配置文件**: `config/rag_config.yaml`。
3.  **代码默认值**: (仅作为兜底)。

推荐始终通过 `.env` 管理敏感信息和特定环境的配置。
