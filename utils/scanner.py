#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# 需要跳过的目录或文件
EXCLUDE_DIRS = {'.git', '.github'}
EXCLUDE_FILES = {
    'README.md', 'LICENSE', 'git_sync.bat', 'git_sync.sh', '.gitignore'
}

def scan_directory(base_path, current_path=""):
    """
    递归扫描 base_path 下的文件和目录，返回树状结构的列表。
    
    :param base_path: 要扫描的操作系统绝对路径
    :param current_path: 从仓库根目录开始的相对路径（用于前端显示或下载）
    :return: 一个列表，每个元素是:
             {
               "name": str,
               "type": "directory" or "file",
               "path": str,
               "children": list (仅当目录时存在)
             }
    """
    entries = []

    try:
        for entry in os.scandir(base_path):
            # 检查是否目录
            if entry.is_dir():
                # 跳过不需要的目录
                if entry.name in EXCLUDE_DIRS:
                    continue
                
                child = {
                    "name": entry.name,
                    "type": "directory",
                    # 统一使用 "/" 做分隔符
                    "path": os.path.join(current_path, entry.name).replace("\\", "/"),
                    # 递归扫描子目录
                    "children": scan_directory(
                        os.path.join(base_path, entry.name),
                        os.path.join(current_path, entry.name)
                    )
                }
                entries.append(child)
            else:
                # 跳过不需要的文件
                if entry.name in EXCLUDE_FILES:
                    continue
                
                child = {
                    "name": entry.name,
                    "type": "file",
                    "path": os.path.join(current_path, entry.name).replace("\\", "/")
                }
                entries.append(child)

    except PermissionError as e:
        print(f"PermissionError: Unable to access {base_path} - {e}")
    except Exception as e:
        print(f"Error scanning {base_path}: {e}")

    # 关键：在返回前对 entries 做排序
    # - 让文件夹 ("directory") 排在前面，文件 ("file") 排在后面
    # - 同类型的按名称字母顺序（忽略大小写）排序
    entries.sort(key=lambda x: (
        0 if x["type"] == "directory" else 1,
        x["name"].lower()
    ))

    return entries
