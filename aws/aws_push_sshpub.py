import boto3
import config
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# import socket, socks
# default_socket = socket.socket
# socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_PROXY_HOST, config.SOCKS5_PROXY_PORT)
# socket.socket = socks.socksocket


key_public = ""  # ssh公钥,建议提前生成
InstanceId = ""  # ec2实例id
RegionId = ""  # ec2实例对应区域id，如ap-southeast-2
user = "ec2-user"  # 用户名错误会导致密钥写入失败
# you can replace user with ec2-user, root, ubuntu,centos etc as required.(ubuntu可以直接写root)
# Debian用户是admin，Amazon Linux，用户名为 ec2-user。对于 RHEL5，用户名是 root 或ec2-user。对于 Ubuntu，用户名为ubuntu。对于
# Fedora，用户名是fedora或ec2-user。对于 SUSE Linux，用户名为root


# 向ec2实例写入ssh公钥。有效期60s。
def push_ec2_instances(AccessKeyID, AccessKeySecret, key_public=None):
    private_pem = ''
    if not key_public:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_key = private_key.public_key()
        public_openssh = public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH
        )
        key_public = public_openssh.decode('utf-8')
        with open("ssh_private", "wb") as f:
            f.write(private_pem)

    push_ec2_client = boto3.client('ec2-instance-connect', region_name=RegionId, aws_access_key_id=AccessKeyID,
                                   aws_secret_access_key=AccessKeySecret)
    response = push_ec2_client.send_ssh_public_key(
        InstanceId=InstanceId,
        InstanceOSUser=user,

        SSHPublicKey=key_public,
    )
    if private_pem:
        print(f"请使用私钥文件ssh_private和用户名{user}连接")
    else:
        print(f"请使用自定义私钥和用户名{user}连接")
    return response


if __name__ == '__main__':
    AccessKeyID = config.AccessKeyID
    AccessKeySecret = config.AccessKeySecret
    if not AccessKeyID:
        AccessKeyID = input("请输入AccessKeyID:")
    if not AccessKeySecret:
        AccessKeySecret = input("请输入AccessKeySecret:")
    ec2_info = push_ec2_instances(AccessKeyID, AccessKeySecret, key_public)
    print(ec2_info)
