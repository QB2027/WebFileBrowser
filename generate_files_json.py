import json
import oss2
import os


def load_config():
    """
    加载配置文件
    """
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def scan_oss_bucket(bucket, prefix="", exclude_dirs=None, exclude_files=None):
    """
    递归扫描 OSS Bucket 中的文件和目录，返回树状结构的列表。
    :param bucket: OSS Bucket 对象
    :param prefix: 当前扫描的路径前缀
    :param exclude_dirs: 要忽略的目录名集合
    :param exclude_files: 要忽略的文件名集合
    :return: 列表，每个元素是 {name, type, path, children?}
    """
    if exclude_dirs is None:
        exclude_dirs = set()
    if exclude_files is None:
        exclude_files = set()

    entries = []
    folders = set()  # 用于记录所有目录
    objects = oss2.ObjectIterator(bucket, prefix=prefix)

    for obj in objects:
        # 文件和文件夹路径分割
        path_parts = obj.key.split("/")
        name = path_parts[-1] if not obj.key.endswith("/") else path_parts[-2]

        # 处理文件夹
        if obj.key.endswith("/"):
            if name in exclude_dirs:
                continue
            folders.add(obj.key)
        else:
            # 处理文件
            if name in exclude_files:
                continue
            signed_url = bucket.sign_url('GET', obj.key, 3600)  # 为文件生成签名链接
            entries.append({
                "name": name,
                "type": "file",
                "path": signed_url
            })

    # 递归生成目录结构
    def build_tree(path):
        children = []

        # 子目录处理
        for folder in folders:
            if folder.startswith(path) and folder != path:
                folder_name = folder[len(path):].split("/")[0]
                folder_key = os.path.join(path, folder_name).replace("\\", "/")
                if folder_name not in exclude_dirs:
                    children.append({
                        "name": folder_name,
                        "type": "directory",
                        "path": folder_key,
                        "children": build_tree(folder)
                    })

        # 添加文件
        for entry in entries:
            if entry["path"].startswith(path) and "/" not in entry["path"][len(path):]:
                children.append(entry)

        return children

    return build_tree(prefix)


def main():
    try:
        config = load_config()
        bucket_name = config["bucket_name"]
        endpoint = config["endpoint"]
        exclude_dirs = set(config.get("exclude_dirs", []))
        exclude_files = set(config.get("exclude_files", []))

        access_key_id = os.getenv(config["oss_access_key_id_env"])
        access_key_secret = os.getenv(config["oss_access_key_secret_env"])

        if not access_key_id or not access_key_secret:
            raise ValueError("OSS credentials are not set in the environment variables.")

        # 初始化 OSS Bucket
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)

        # 生成目录结构
        print("Scanning OSS bucket for files and directories...")
        data = scan_oss_bucket(bucket, prefix="", exclude_dirs=exclude_dirs, exclude_files=exclude_files)

        # 写入 JSON 文件
        output_path = "files.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"文件树 JSON 已生成：{output_path}")

    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    main()
