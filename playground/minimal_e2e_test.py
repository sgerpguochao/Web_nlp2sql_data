#!/usr/bin/env python3
"""
最小单元前后端测试 - 需后端已启动 (python app.py)
配置: DeepSeek + MySQL ai_sales_data
"""
import json
import time
import requests

API_BASE = "http://localhost:8000"

# 配置
DB_CONFIG = {
    "type": "mysql",
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "csd123456",
    "database": "ai_sales_data",
}

LLM_CONFIG = {
    "api_base": "https://api.deepseek.com",
    "api_key": "sk-078749ee2b624d8b9c372df17385ff4f",
    "model_name": "deepseek-chat",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 4096,
    "timeout": 60,
    "max_retries": 3,
}


def test_health():
    """1. 健康检查"""
    r = requests.get(f"{API_BASE}/health", timeout=5)
    assert r.status_code == 200, f"Health fail: {r.status_code}"
    assert r.json().get("status") == "ok"
    print("[OK] 1. 健康检查")


def test_db():
    """2. 数据库连接"""
    r = requests.post(
        f"{API_BASE}/api/test-db-connection",
        json=DB_CONFIG,
        timeout=10,
    )
    assert r.status_code == 200, f"DB fail: {r.status_code} {r.text}"
    data = r.json()
    assert data.get("success"), f"DB connect fail: {data}"
    print(f"[OK] 2. 数据库连接 (表数: {data.get('tables_count', '?')})")


def test_llm():
    """3. LLM 连接"""
    r = requests.post(
        f"{API_BASE}/api/test-llm-connection",
        json=LLM_CONFIG,
        timeout=30,
    )
    assert r.status_code == 200, f"LLM fail: {r.status_code} {r.text}"
    data = r.json()
    assert data.get("success"), f"LLM connect fail: {data}"
    print("[OK] 3. LLM 连接")


def test_generation():
    """4. 最小生成 (2 条样本)"""
    payload = {
        "db": DB_CONFIG,
        "llm": LLM_CONFIG,
        "generate": {
            "total_samples": 2,
            "dialect": "mysql",
            "output_path": "./data/nl2sql.jsonl",
            "output_format": "alpaca",
            "enable_validation": True,
            "min_tables_per_topic": 1,
            "max_tables_per_topic": 5,
        },
    }
    r = requests.post(
        f"{API_BASE}/api/start-generation",
        json=payload,
        timeout=10,
    )
    assert r.status_code == 200, f"Start fail: {r.status_code} {r.text}"
    data = r.json()
    assert data.get("success"), f"Start fail: {data}"
    task_id = data.get("task_id")
    print(f"[OK] 4. 任务已启动 {task_id}")

    # 轮询状态
    for _ in range(120):
        r = requests.get(f"{API_BASE}/api/status", timeout=5)
        s = r.json()
        status = s.get("status")
        step = s.get("current_step", 0)
        total = s.get("total_steps", 6)
        progress = s.get("progress", 0)
        if status == "completed":
            print(f"[OK] 5. 生成完成 (progress={progress}%)")
            return
        if status == "failed":
            raise AssertionError(f"生成失败: {s.get('error_message')}")
        print(f"      step {step}/{total} progress={progress}%", end="\r")
        time.sleep(2)
    raise TimeoutError("生成超时")


def main():
    print("=" * 50)
    print("NL2SQL 最小单元测试 (需后端已启动)")
    print("=" * 50)
    try:
        test_health()
        test_db()
        test_llm()
        test_generation()
        print("=" * 50)
        print("全部通过")
        print("=" * 50)
    except Exception as e:
        print(f"\n[FAIL] {e}")
        raise


if __name__ == "__main__":
    main()
