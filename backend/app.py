#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NL2SQL自动化数据生成系统 - FastAPI后端服务器
提供REST API和WebSocket接口，连接前端界面和后端生成模块
"""

import os
import shutil
import glob
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from api.routes import router as api_router
from api.websocket import router as ws_router
from api.download import router as download_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理 - 清理data文件夹"""
    # 启动时的操作
    print("=" * 50)
    print("FastAPI app starting...")
    print("=" * 50)

    # 清理data文件夹
    data_dir = "./data"
    print(f"\nCleaning {data_dir}...")

    try:
        if os.path.exists(data_dir):
            # 删除data文件夹下的所有文件和子文件夹
            for filename in os.listdir(data_dir):
                file_path = os.path.join(data_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        print(f"  Deleted file: {filename}")
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        print(f"  Deleted dir: {filename}")
                except Exception as e:
                    print(f"  Failed to delete {file_path}: {e}")

            print(f"Done cleaning {data_dir}")
        else:
            # 如果data文件夹不存在，创建它
            os.makedirs(data_dir, exist_ok=True)
            print(f"Created {data_dir}")

    except Exception as e:
        print(f"Failed to clean data dir: {e}")

    yield  # 应用运行期间

    # 关闭时的操作
    print("\n" + "=" * 50)
    print("FastAPI app shutting down...")
    print("=" * 50)

    # 可选：关闭时也可以清理
    print("Cleaning up...")

# 创建FastAPI应用
app = FastAPI(
    title="NL2SQL数据生成系统API",
    description="企业级NL2SQL训练数据自动生成工具API接口",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS - 允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api", tags=["API"])
app.include_router(ws_router, prefix="/ws", tags=["WebSocket"])
app.include_router(download_router, prefix="/api", tags=["Download"])

# 静态文件服务（前端构建文件）- 支持 backend/dist 或 frontend/dist
_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dist_dir = os.path.join(os.path.dirname(__file__), "dist")
if not os.path.exists(dist_dir):
    dist_dir = os.path.join(_base, "frontend", "dist")
if os.path.exists(dist_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_dir, "assets")), name="assets")
    
    @app.get("/")
    async def serve_frontend():
        """服务前端页面"""
        index_file = os.path.join(dist_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "请先构建前端: npm run build"}


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "ok",
        "service": "nl2sql-api",
        "version": "1.0.0"
    }


def main():
    """启动服务器"""
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print("=" * 80)
    print("[OK] NL2SQL API server starting...")
    print("=" * 80)
    print(f"API: http://{host}:{port}/api")
    print(f"WebSocket: ws://{host}:{port}/ws")
    print(f"Health: http://{host}:{port}/health")
    print(f"Docs: http://{host}:{port}/docs")
    print("=" * 80)
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True,  # 开发模式自动重载
        log_level="info"
    )


if __name__ == "__main__":
    main()
