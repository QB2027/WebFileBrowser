from ecies.utils import generate_eth_key, generate_key
from ecies import encrypt, decrypt

# 使用 generate_eth_key() 生成 Ethereum 密钥对
eth_k = generate_eth_key()
prvhex = eth_k.to_hex()  # 私钥的十六进制表示
pubhex = eth_k.public_key.to_hex()  # 公钥的十六进制表示
print(f"prv{eth_k}")
print(f"pub{eth_k.public_key}")

# 待加密的消息
data = b'this is a test'

# 使用公钥加密，私钥解密
encrypted = encrypt(pubhex, data)
decrypted = decrypt(prvhex, encrypted)
print(f"pubhex{pubhex}")
print(f"prvhex{prvhex}")

# 输出解密后的消息
print(f"Decrypted with Ethereum key: {decrypted}")  # 应该输出: b'this is a test'


# 使用 generate_key() 生成 secp256k1 密钥对
secp_k = generate_key()
prvhex = secp_k.to_hex()  # 私钥的十六进制表示
pubhex = secp_k.public_key.format(True).hex()  # 公钥的十六进制表示

# 使用公钥加密，私钥解密
encrypted = encrypt(pubhex, data)
decrypted = decrypt(prvhex, encrypted)

# 输出解密后的消息
print(f"Decrypted with secp256k1 key: {decrypted}")  # 应该输出: b'this is a test'
