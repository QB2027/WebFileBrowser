import json
import oss2
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import secrets
import sys

def main():
    try:
        # 读取配置
        config = load_config()

        bucket_name = config['bucket_name']
        endpoint = config['endpoint']

        if not bucket_name or not endpoint:
            raise ValueError("Bucket name and endpoint must be specified in config.json")

        # 获取环境变量中的 OSS 凭证
        access_key_id = os.getenv(config['oss_access_key_id_env'])
        access_key_secret = os.getenv(config['oss_access_key_secret_env'])
        encryption_password = os.getenv(config['encryption_password_env'])

        if not access_key_id or not access_key_secret:
            raise ValueError(f"{config['oss_access_key_id_env']} and {config['oss_access_key_secret_env']} must be set")

        if not encryption_password:
            raise ValueError(f"{config['encryption_password_env']} must be set")

        # 初始化 OSS Bucket
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)

        # 要扫描的目录前缀（根目录为空字符串）
        prefix = ''

        # 获取所有文件和文件夹列表
        file_list = []
        folders = set()

        print("Scanning OSS bucket for files and folders...")
        for obj in oss2.ObjectIterator(bucket, prefix=prefix):
            if obj.key.endswith('/'):
                # 识别为文件夹
                folders.add(obj.key)
            else:
                # 识别为文件
                # 确定文件所属的文件夹
                folder_path = os.path.dirname(obj.key) + '/'
                if folder_path != '/':
                    folders.add(folder_path)
                # 生成预签名 URL，有效期为1小时
                try:
                    url = bucket.sign_url('GET', obj.key, 3600)
                except Exception as e:
                    print(f"Error generating pre-signed URL for {obj.key}: {e}")
                    continue
                file_list.append({
                    'name': os.path.basename(obj.key),
                    'path': obj.key,
                    'url': url,
                    'type': 'file'
                })

        # 添加文件夹到列表
        for folder in folders:
            if folder == prefix:
                continue  # 跳过根目录
            file_list.append({
                'name': os.path.basename(folder.rstrip('/')),
                'path': folder,
                'url': '',
                'type': 'folder'
            })

        # 将文件和文件夹列表写入 files.json
        with open('files.json', 'w', encoding='utf-8') as f:
            json.dump(file_list, f, ensure_ascii=False, indent=2)

        print('files.json 已生成。')

        # 加密 files.json
        encrypted_files_json = encrypt_data('files.json', encryption_password, config)

        # 写入加密后的文件
        with open('files.json.enc', 'w', encoding='utf-8') as f:
            f.write(encrypted_files_json)

        print('files.json.enc 已生成。')

        # 可选：删除明文 files.json
        try:
            os.remove('files.json')
            print('files.json 已删除。')
        except Exception as e:
            print(f"Error deleting files.json: {e}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def load_config():
    """加载配置文件"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load config.json: {e}")

def encrypt_data(file_path, password, config):
    """加密数据"""
    try:
        backend = default_backend()
        salt = secrets.token_bytes(config['encryption_salt_length'])  # 动态盐长度
        # 使用PBKDF2HMAC从密码生成密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256
            salt=salt,
            iterations=config['encryption_iterations'],  # 动态迭代次数
            backend=backend
        )
        key = kdf.derive(password.encode())
        # 初始化AES加密器
        iv = secrets.token_bytes(config['encryption_iv_length'])  # 动态IV长度
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
        encryptor = cipher.encryptor()
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
        encrypted = encryptor.update(data.encode()) + encryptor.finalize()
        # 返回包含盐和IV的base64编码数据
        encrypted_data = base64.b64encode(salt + iv + encrypted).decode('utf-8')
        return encrypted_data
    except Exception as e:
        print(f"Error during encryption: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
