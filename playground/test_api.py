#!/usr/bin/env python3
"""
NL2SQL 后端 API 接口测试
测试所有 REST API 端点的输入输出
"""
import json
import requests

API_BASE = "http://localhost:8000"


def test_health():
    """健康检查"""
    r = requests.get(f"{API_BASE}/health", timeout=5)
    print(f"[GET] /health")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.json()}")
    print()


def test_status():
    """获取任务状态"""
    r = requests.get(f"{API_BASE}/api/status", timeout=5)
    print(f"[GET] /api/status")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.json()}")
    print()


def test_logs():
    """获取日志"""
    r = requests.get(f"{API_BASE}/api/logs?limit=10", timeout=5)
    print(f"[GET] /api/logs")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.json()}")
    print()


def test_db_connection():
    """测试数据库连接"""
    payload = {
        "type": "mysql",
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "csd123456",
        "database": "ai_sales_data",
    }
    r = requests.post(f"{API_BASE}/api/test-db-connection", json=payload, timeout=10)
    print(f"[POST] /api/test-db-connection")
    print(f"  Request: {json.dumps(payload, indent=2)}")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.json()}")
    print()


def test_llm_connection():
    """测试 LLM 连接"""
    payload = {
        "api_base": "https://api.deepseek.com",
        "api_key": "sk-078749ee2b624d8b9c372df17385ff4f",
        "model_name": "deepseek-chat",
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 4096,
        "timeout": 60,
        "max_retries": 3,
    }
    r = requests.post(f"{API_BASE}/api/test-llm-connection", json=payload, timeout=30)
    print(f"[POST] /api/test-llm-connection")
    print(f"  Request: {json.dumps(payload, indent=2)}")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.json()}")
    print()


def test_start_generation():
    """启动生成任务"""
    payload = {
        "db": {
            "type": "mysql",
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "csd123456",
            "database": "ai_sales_data",
        },
        "llm": {
            "api_base": "https://api.deepseek.com",
            "api_key": "sk-078749ee2b624d8b9c372df17385ff4f",
            "model_name": "deepseek-chat",
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 4096,
            "timeout": 60,
            "max_retries": 3,
        },
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
    r = requests.post(f"{API_BASE}/api/start-generation", json=payload, timeout=10)
    print(f"[POST] /api/start-generation")
    print(f"  Request: {json.dumps(payload, indent=2)}")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.json()}")
    print()
    return r.json().get("task_id")


def test_cancel():
    """取消任务"""
    r = requests.post(f"{API_BASE}/api/cancel", timeout=5)
    print(f"[POST] /api/cancel")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.json()}")
    print()


def test_download():
    """下载生成的数据"""
    r = requests.get(f"{API_BASE}/api/download/latest", timeout=5)
    print(f"[GET] /api/download/latest")
    print(f"  Status: {r.status_code}")
    print(f"  Content-Type: {r.headers.get('Content-Type')}")
    print(f"  Content-Length: {r.headers.get('Content-Length')}")
    print()


def test_download_rag():
    """下载 RAG 训练数据包"""
    r = requests.get(f"{API_BASE}/api/download/rag", timeout=5)
    print(f"[GET] /api/download/rag")
    print(f"  Status: {r.status_code}")
    print(f"  Content-Type: {r.headers.get('Content-Type')}")
    print(f"  Response: {r.text[:200] if r.status_code != 200 else 'File downloaded'}")
    print()


def main():
    print("=" * 60)
    print("NL2SQL 后端 API 接口测试")
    print("=" * 60)
    print()

    # 基础接口
    test_health()
    test_status()
    test_logs()

    # 测试接口
    test_db_connection()
    test_llm_connection()

    # 生成任务接口（谨慎使用，会实际调用 LLM）
    # test_start_generation()
    # test_cancel()

    # 下载接口
    # test_download()
    # test_download_rag()  # 需要先生成 RAG 数据

    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
