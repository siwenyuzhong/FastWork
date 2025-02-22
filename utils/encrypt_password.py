from Crypto.Cipher import DES

"""
DES加密
全称为Data EncryptionStandard，即数据加密标准，是一种使用密钥加密的块算法

入口参数有三个：Key、Data、Mode
Key为7个字节共56位，是DES算法的工作密钥；
Data为8个字节64位，是要被加密或被解密的数据；
Mode为DES的工作方式,有两种:加密或解密
3DES（即Triple DES）是DES向AES过渡的加密算法，
使用两个密钥，执行三次DES算法，
加密的过程是加密-解密-加密
解密的过程是解密-加密-解密
"""


def pad(text):
    """
    # 加密函数，如果text不是8的倍数【加密文本text必须为8的倍数！】，那就补足为8的倍数
    :param text:
    :return:
    """
    while len(text) % 8 != 0:
        text += ' '
    return text


# 加密
def encrypt_password(password):
    key = b'!@QWas:{'  # 密钥 8位或16位,必须为bytes
    des = DES.new(key, DES.MODE_ECB)  # 创建一个DES实例
    padded_text = pad(password)
    encrypted_text = des.encrypt(padded_text.encode('utf-8'))  # 加密
    return encrypted_text


# 解密
def descrypt_password(password):
    key = b'!@QWas:{'  # 密钥 8位或16位,必须为bytes
    des = DES.new(key, DES.MODE_ECB)  # 创建一个DES实例
    # rstrip(' ')返回从字符串末尾删除所有字符串的字符串(默认空白字符)的副本
    plain_text = des.decrypt(password).decode().rstrip(' ')  # 解密
    return plain_text


if __name__ == '__main__':
    print(encrypt_password(str(1236775432222)))
    print(descrypt_password(b'Kta^\xb5\xaa\xe8=\xb3\xfb\xa4\xac\x8c\x10\x92\x18'))
