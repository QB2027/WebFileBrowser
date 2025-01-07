# generate_files_json.py

import json
import oss2
import os

# 获取环境变量中的 OSS 凭证
access_key_id = os.getenv('OSS_ACCESS_KEY_ID')
access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET')
bucket_name = 'class-files'  # 替换为你的 Bucket 名称
endpoint = 'oss-cn-hangzhou.aliyuncs.com'  # 根据你的 Bucket 所在区域调整

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
