import json
import os
import base64
import secrets
import oss2
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def load_config():
    """
    加载配置文件
    """
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_aes_key():
    """
    从环境变量中加载 Base64 编码的 AES 密钥，并解码为原始 32 字节密钥
    """
    encryption_password = os.getenv("ENCRYPTION_PASSWORD")
    if not encryption_password:
        raise ValueError("环境变量 ENCRYPTION_PASSWORD 未设置")

    try:
        # 尝试将 Base64 编码的密钥解码为原始字节
        key = base64.b64decode(encryption_password)
    except Exception:
        raise ValueError("无法解码 ENCRYPTION_PASSWORD，请确保它是 Base64 编码的字符串")

    if len(key) != 32:
        raise ValueError("解码后的 AES 密钥必须为 32 字节（256 位）")
    return key

def encrypt_aes(data, key):
    """
    使用 AES 加密数据
    """
    iv = secrets.token_bytes(16)  # 随机生成 IV
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data.encode("utf-8")) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_data).decode("utf-8")

def scan_oss_bucket(bucket, prefix="", exclude_dirs=None, exclude_files=None):
    """
    递归扫描 OSS Bucket 中的文件和目录，返回树状结构的列表。
    """
    if exclude_dirs is None:
        exclude_dirs = set()
    if exclude_files is None:
        exclude_files = set()

    entries = {}
    objects = oss2.ObjectIterator(bucket, prefix=prefix)

    for obj in objects:
        parts = obj.key.strip("/").split("/")
        name = parts[-1]

        if obj.key.endswith("/"):
            folder_path = "/".join(parts)
            if folder_path not in entries:
                entries[folder_path] = {"name": name, "type": "directory", "path": folder_path, "children": []}
        else:
            if name in exclude_files:
                continue
            file_path = "/".join(parts)
            signed_url = bucket.sign_url("GET", obj.key, 3600)  # 生成签名链接
            parent_path = "/".join(parts[:-1])
            if parent_path not in entries:
                entries[parent_path] = {"name": parts[-2] if len(parts) > 1 else "", "type": "directory", "path": parent_path, "children": []}
            entries[parent_path]["children"].append({"name": name, "type": "file", "path": signed_url})

    root = []
    for entry in entries.values():
        parent_path = "/".join(entry["path"].strip("/").split("/")[:-1])
        if parent_path in entries:
            entries[parent_path]["children"].append(entry)
        else:
            root.append(entry)

    return root

def main():
    try:
        # 加载配置
        config = load_config()
        bucket_name = config["bucket_name"]
        endpoint = config["endpoint"]
        exclude_dirs = set(config.get("exclude_dirs", []))
        exclude_files = set(config.get("exclude_files", []))

        access_key_id = os.getenv("OSS_ACCESS_KEY_ID")
        access_key_secret = os.getenv("OSS_ACCESS_KEY_SECRET")

        if not access_key_id or not access_key_secret:
            raise ValueError("OSS credentials are not set in the environment variables.")

        # 初始化 OSS Bucket
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)

        # 扫描 OSS 文件结构
        print("Scanning OSS bucket for files and directories...")
        files_structure = scan_oss_bucket(bucket, prefix="", exclude_dirs=exclude_dirs, exclude_files=exclude_files)
        files_json = json.dumps(files_structure, ensure_ascii=False, indent=2)

        # 加密文件结构
        aes_key = load_aes_key()
        encrypted_files = encrypt_aes(files_json, aes_key)

        # 保存加密后的文件结构
        with open("files.json.enc", "w", encoding="utf-8") as f:
            f.write(encrypted_files)
        print("加密后的文件列表已生成：files.json.enc")

    except Exception as e:
        print(f"发生错误：{e}")

if __name__ == "__main__":
    main()
