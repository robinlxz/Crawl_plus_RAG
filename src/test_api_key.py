import os
import sys
import yaml
from openai import OpenAI

def load_env_manual():
    """Manually load .env to ensure we are reading the right file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, "../.env")
    
    print(f"[Info] Loading .env from: {os.path.abspath(env_path)}")
    
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value
                    if "KEY" in key:
                         print(f"Loaded {key}: {value[:8]}...{value[-4:]} (Len: {len(value)})")
    else:
        print("Error: .env file not found!")

def load_config():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "../config/rag_config.yaml") # Adjusted path: src/test.py -> ../config
    
    print(f"[Info] Loading config from: {os.path.abspath(config_path)}")
    
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            print(f"[Info] Config keys: {list(data.keys())}")
            return data
    else:
        print(f"[Error] Config file not found at {config_path}")
    return {}

def test_provider(name, api_key_env, base_url, model):
    print(f"\n{'='*20} Testing {name.upper()} {'='*20}")
    api_key = os.environ.get(api_key_env)
    
    if not api_key:
        print(f"Skipping {name}: {api_key_env} is not set.")
        return

    print(f"Endpoint: {base_url}")
    print(f"Model: {model}")
    
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    messages = [{"role": "user", "content": "Hello, simply say 'OK'."}]
    print(f"Input: {messages}")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=10
        )
        print(">>> Success!")
        print(f"Output: {response.choices[0].message.content}")
    except Exception as e:
        print(f">>> Failed: {e}")

def main():
    load_env_manual()
    config = load_config()
    
    # 1. Test DeepSeek
    # Note: DeepSeek config is usually static, but we can read from yaml if present
    ds_conf = config.get("deepseek", {})
    test_provider(
        name="DeepSeek",
        api_key_env=ds_conf.get("api_key_env", "DEEPSEEK_API_KEY"),
        base_url=ds_conf.get("base_url", "https://api.deepseek.com"),
        model=ds_conf.get("model", "deepseek-chat")
    )
    
    # 2. Test Doubao
    db_conf = config.get("doubao", {})
    test_provider(
        name="Doubao",
        api_key_env=db_conf.get("api_key_env", "DOUBAO_API_KEY"),
        base_url=db_conf.get("base_url", "https://ark.cn-beijing.volces.com/api/v3"),
        model=db_conf.get("model", "ep-20250209123456-abcde") # Use config value
    )

if __name__ == "__main__":
    main()
