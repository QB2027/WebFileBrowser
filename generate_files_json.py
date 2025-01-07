import json
import oss2
import os
import sys

def main():
    try:
        # 加载配置
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

        # 构建目录结构
        print("Scanning OSS bucket for files and folders...")
        root_structure = build_directory_structure(bucket)

        # 打印目录结构以调试
        print("Generated directory structure:")
        print(json.dumps(root_structure, ensure_ascii=False, indent=2))

        # 写入 JSON 文件
        with open('files.json', 'w', encoding='utf-8') as f:
            json.dump(root_structure, f, ensure_ascii=False, indent=2)

        print('files.json 已生成。')

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
    构建 OSS 存储桶的目录结构，返回嵌套的 JSON 格式
    """
    files_map = {}
    directories = set()

    # 遍历 OSS 对象，区分文件和文件夹
    for obj in oss2.ObjectIterator(bucket, prefix=prefix):
        print(f"Processing object: {obj.key}")  # 调试信息

        if obj.key.endswith('/'):
            # 是文件夹
            directories.add(obj.key)
        else:
            # 是文件
            signed_url = bucket.sign_url('GET', obj.key, 3600)  # 1小时有效期
            parent_dir = os.path.dirname(obj.key) + '/'
            if parent_dir not in files_map:
                files_map[parent_dir] = []
            files_map[parent_dir].append({
                "name": os.path.basename(obj.key),
                "type": "file",
                "path": signed_url
            })

    # 递归生成嵌套目录
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


if __name__ == "__main__":
    main()
