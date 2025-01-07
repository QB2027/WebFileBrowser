import json
import oss2
from datetime import datetime, timedelta
import os

# 获取环境变量中的 OSS 凭证
access_key_id = os.getenv('OSS_ACCESS_KEY_ID')
access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET')
bucket_name = 'class-files'  # 替换为你的 Bucket 名称
endpoint = 'oss-cn-shanghai.aliyuncs.com'  # 根据你的Bucket所在区域调整

# 初始化 OSS Bucket
auth = oss2.Auth(access_key_id, access_key_secret)
bucket = oss2.Bucket(auth, endpoint, bucket_name)

# 要扫描的目录前缀
prefix = ''

# 获取所有文件列表
file_list = []
for obj in oss2.ObjectIterator(bucket, prefix=prefix):
    if not obj.key.endswith('/'):
        # 生成预签名 URL，有效期为1小时
        url = bucket.sign_url('GET', obj.key, 3600)
        file_list.append({
            'name': obj.key.split('/')[-1],
            'path': obj.key,
            'url': url,
            'type': 'file'
        })

# 将文件列表写入 files.json
with open('files.json', 'w', encoding='utf-8') as f:
    json.dump(file_list, f, ensure_ascii=False, indent=2)

print('files.json 已生成。')
