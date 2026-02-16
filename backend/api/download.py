"""
文件下载模块
提供生成数据的下载功能
"""

import os
import zipfile
import tempfile
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/download/latest")
async def download_latest():
    """
    下载最新生成的训练数据
    
    Returns:
        最新的nl2sql.jsonl文件
    """
    # 尝试从任务管理器获取输出路径
    try:
        from .task_manager import TaskManager
        task_manager = TaskManager()
        file_path = task_manager.output_path
    except:
        # 如果失败，使用默认路径
        file_path = "./data/nl2sql.jsonl"

    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"训练数据文件不存在: {file_path}，请先生成数据")
    
    # 从路径中提取文件名
    filename = os.path.basename(file_path)
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/jsonl"
    )


@router.get("/download/rag")
async def download_latest_rag():
    """
    下载最新的RAG训练数据包

    Returns:
        ddl_mysql.zip 文件或错误信息
    """
    file_path = "./data/nl2sql.jsonl"

    # 获取文件所在目录
    file_dir = os.path.dirname(file_path)

    # 1. 检查是否存在 ddl_mysql 文件夹
    ddl_mysql_dir = os.path.join(file_dir, "ddl_mysql")
    if not os.path.exists(ddl_mysql_dir):
        raise HTTPException(
            status_code=404,
            detail="训练数据并没有提取documents数据，请先生成documents数据"
        )

    # 2. 检查必须包含的四个文件
    required_files = ["ddl.jsonl", "doc.jsonl", "plan.jsonl", "sql_parse.jsonl"]
    missing_files = []

    for required_file in required_files:
        file_path = os.path.join(ddl_mysql_dir, required_file)
        if not os.path.exists(file_path):
            missing_files.append(required_file)

    if missing_files:
        raise HTTPException(
            status_code=404,
            detail=f"训练数据documents缺失以下文件: {', '.join(missing_files)}"
        )

    # 3. 创建临时zip文件
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
            zip_path = temp_zip.name

        # 创建zip文件
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加所有文件到zip
            for root, dirs, files in os.walk(ddl_mysql_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 在zip中保持相对路径
                    arcname = os.path.relpath(file_path, ddl_mysql_dir)
                    zipf.write(file_path, arcname)

        # 返回zip文件
        return FileResponse(
            path=zip_path,
            filename="ddl_mysql.zip",
            media_type="application/zip",
            headers={
                "Content-Disposition": "attachment; filename=ddl_mysql.zip"
            }
        )

    except Exception as e:
        # 清理临时文件
        if os.path.exists(zip_path):
            os.unlink(zip_path)
        raise HTTPException(
            status_code=500,
            detail=f"创建zip文件时出错: {str(e)}"
        )

@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    下载生成的数据文件
    
    Args:
        filename: 文件名
        
    Returns:
        文件下载响应
    """
    # 安全检查：只允许下载data目录下的特定文件
    allowed_files = [
        "metadata.json",
        "table_cards.json", 
        "plan.json",
        "samples_raw.jsonl",
        "samples_valid.jsonl",
        "nl2sql.jsonl",
        "nl2sql_alpaca.jsonl",
        "nl2sql_sharegpt.jsonl"
    ]
    
    if filename not in allowed_files:
        raise HTTPException(status_code=403, detail="不允许下载此文件")
    
    file_path = os.path.join("./data", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 根据文件扩展名设置正确的 media type
    media_type = "application/octet-stream"
    if filename.endswith(".jsonl"):
        media_type = "application/jsonl"
    elif filename.endswith(".json"):
        media_type = "application/json"
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )

