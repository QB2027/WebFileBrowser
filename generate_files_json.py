import json
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets
import sys


def encrypt_aes(data, key):
    """
    使用 AES 加密数据
    :param data: 待加密的字符串
    :param key: AES 密钥（字节形式，32 字节 = 256 位）
    :return: 加密后的 Base64 字符串
    """
    iv = secrets.token_bytes(16)  # 随机生成 IV（初始化向量）
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data.encode("utf-8")) + encryptor.finalize()
    # 返回包含 IV 和加密数据的 Base64 编码
    return base64.b64encode(iv + encrypted_data).decode("utf-8")


def load_aes_key():
    """
    从环境变量加载 AES 密钥
    :return: AES 密钥（字节形式）
    """
    encryption_password = os.getenv("ENCRYPTION_PASSWORD")
    if not encryption_password:
        raise ValueError("环境变量 ENCRYPTION_PASSWORD 未设置")

    # 确保密钥长度为 32 字节（256 位）
    key = encryption_password.encode("utf-8")
    if len(key) != 32:
        raise ValueError("加密密码必须是 32 个字符")
    return key


def scan_directory(base_path, exclude_dirs, exclude_files, current_path=""):
    """
    递归扫描目录，生成文件和目录的树状结构
    :param base_path: 基础路径
    :param exclude_dirs: 排除的目录列表
    :param exclude_files: 排除的文件列表
    :param current_path: 相对路径（用于构建层级结构）
    :return: 文件列表（树状结构）
    """
    entries = []
    for entry in os.scandir(base_path):
        if entry.is_dir():
            if entry.name in exclude_dirs:
                continue
            entries.append({
                "name": entry.name,
                "type": "directory",
                "path": f"{current_path}/{entry.name}".lstrip("/"),
                "children": scan_directory(entry.path, exclude_dirs, exclude_files, f"{current_path}/{entry.name}")
            })
        elif entry.is_file():
            if entry.name in exclude_files:
                continue
            entries.append({
                "name": entry.name,
                "type": "file",
                "path": f"{current_path}/{entry.name}".lstrip("/")
            })
    return entries


def main():
    try:
        # 加载配置文件
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

        # 获取 OSS bucket 配置
        bucket_name = config.get("bucket_name")
        endpoint = config.get("endpoint")
        if not bucket_name or not endpoint:
            raise ValueError("config.json 中必须指定 bucket_name 和 endpoint")

        # 获取排除的目录和文件
        exclude_dirs = config.get("exclude_dirs", [])
        exclude_files = config.get("exclude_files", [])

        # 扫描当前目录
        base_path = "."
        files = scan_directory(base_path, exclude_dirs, exclude_files)
        print("目录扫描完成，生成文件列表：")
        print(json.dumps(files, ensure_ascii=False, indent=2))

        # 从环境变量加载 AES 密钥
        aes_key = load_aes_key()

        # 将文件列表转换为 JSON 字符串并加密
        files_json = json.dumps(files, ensure_ascii=False, indent=2)
        encrypted_files = encrypt_aes(files_json, aes_key)

        # 保存加密后的文件列表到文件
        output_path = "files.json.enc"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(encrypted_files)

        print(f"加密后的文件列表已保存到：{output_path}")

    except Exception as e:
        print(f"发生错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
