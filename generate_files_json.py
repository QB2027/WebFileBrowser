# generate_files_json.py

import json
import oss2
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import secrets

# 读取配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

bucket_name = config.get('bucket_name')
endpoint = config.get('endpoint')

if not bucket_name or not endpoint:
    raise ValueError("Bucket name and endpoint must be specified in config.json")

# 获取环境变量中的 OSS 凭证
access_key_id = os.getenv('OSS_ACCESS_KEY_ID')
access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET')
encryption_password = os.getenv('ENCRYPTION_PASSWORD')

if not access_key_id or not access_key_secret:
    raise ValueError("OSS_ACCESS_KEY_ID and OSS_ACCESS_KEY_SECRET must be set")

if not encryption_password:
    raise ValueError("ENCRYPTION_PASSWORD must be set")

# 初始化 OSS Bucket
auth = oss2.Auth(access_key_id, access_key_secret)
bucket = oss2.Bucket(auth, endpoint, bucket_name)

# 要扫描的目录前缀（根目录为空字符串）
prefix = ''

# 获取所有文件和文件夹列表
file_list = []
folders = set()

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
        url = bucket.sign_url('GET', obj.key, 3600)
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
def encrypt_data(data, password):
    backend = default_backend()
    salt = secrets.token_bytes(16)  # 16字节的盐
    # 使用PBKDF2HMAC从密码生成密钥
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # AES-256
        salt=salt,
        iterations=100000,
        backend=backend
    )
    key = kdf.derive(password.encode())
    # 初始化AES加密器
    iv = secrets.token_bytes(16)  # 16字节的初始化向量
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(data.encode()) + encryptor.finalize()
    # 返回包含盐和IV的base64编码数据
    encrypted_data = base64.b64encode(salt + iv + encrypted).decode('utf-8')
    return encrypted_data

# 读取生成的 files.json
with open('files.json', 'r', encoding='utf-8') as f:
    files_json = f.read()

# 加密
encrypted_files_json = encrypt_data(files_json, encryption_password)

# 写入加密后的文件
with open('files.json.enc', 'w', encoding='utf-8') as f:
    f.write(encrypted_files_json)

print('files.json.enc 已生成。')

# 可选：删除明文 files.json
os.remove('files.json')
print('files.json 已删除。')
