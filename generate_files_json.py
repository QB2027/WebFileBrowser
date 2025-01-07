import json
import oss2
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import secrets


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

        if not access_key_id or not access_key_secret:
            raise ValueError(f"{config['oss_access_key_id_env']} and {config['oss_access_key_secret_env']} must be set")

        # 初始化 OSS Bucket
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)

        # 获取所有文件和文件夹列表并生成目录结构
        print("Scanning OSS bucket for files and folders...")
        root_structure = build_directory_structure(bucket)

        # 将目录结构写入 JSON 文件
        with open('files.json', 'w', encoding='utf-8') as f:
            json.dump(root_structure, f, ensure_ascii=False, indent=2)

        print('files.json 已生成。')

        # 读取用户信息并为每个用户生成加密文件
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)

        for user_id, password_hash in users.items():
            print(f"Encrypting files for user: {user_id}")
            encrypted_files_json = encrypt_data('files.json', password_hash, config)

            # 写入用户加密文件
            encrypted_file_path = f"files_{user_id}.json.enc"
            with open(encrypted_file_path, 'w', encoding='utf-8') as enc_file:
                enc_file.write(encrypted_files_json)

            print(f"Encrypted file generated for user {user_id}: {encrypted_file_path}")

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


def build_directory_structure(bucket, prefix=''):
    """
    构建 OSS 存储桶的目录结构，文件带有签名 URL
    """
    directory_structure = []
    objects = oss2.ObjectIterator(bucket, prefix=prefix)

    # 使用临时存储路径的文件和目录
    files_map = {}
    directories = set()

    for obj in objects:
        # 如果是文件夹，添加到目录集合
        if obj.key.endswith('/'):
            directories.add(obj.key)
        else:
            # 是文件，生成签名 URL
            signed_url = bucket.sign_url('GET', obj.key, 3600)  # 有效期1小时
            parent_dir = os.path.dirname(obj.key) + '/'
            if parent_dir not in files_map:
                files_map[parent_dir] = []
            files_map[parent_dir].append({
                "name": os.path.basename(obj.key),
                "type": "file",
                "path": signed_url
            })

    # 递归生成目录结构
    def build_tree(path):
        children = []

        # 处理子文件夹
        for directory in directories:
            if os.path.dirname(directory).rstrip('/') == path.rstrip('/'):
                children.append({
                    "name": os.path.basename(directory.rstrip('/')),
                    "type": "directory",
                    "path": directory.rstrip('/'),
                    "children": build_tree(directory)
                })

        # 添加文件
        if path in files_map:
            children.extend(files_map[path])

        return children

    # 构建根目录结构
    return build_tree('')


def encrypt_data(file_path, password_hash, config):
    """使用用户密码哈希值加密数据"""
    try:
        backend = default_backend()
        salt = secrets.token_bytes(config['encryption_salt_length'])  # 动态盐长度
        # 使用 PBKDF2HMAC 从用户密码哈希生成密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256
            salt=salt,
            iterations=config['encryption_iterations'],  # 动态迭代次数
            backend=backend
        )
        key = kdf.derive(password_hash.encode())
        # 初始化 AES 加密器
        iv = secrets.token_bytes(config['encryption_iv_length'])  # 动态 IV 长度
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
        encryptor = cipher.encryptor()
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
        encrypted = encryptor.update(data.encode()) + encryptor.finalize()
        # 返回包含盐和 IV 的 base64 编码数据
        encrypted_data = base64.b64encode(salt + iv + encrypted).decode('utf-8')
        return encrypted_data
    except Exception as e:
        print(f"Error during encryption: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
