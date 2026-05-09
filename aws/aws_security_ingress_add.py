import boto3
import config

# import socket, socks
# default_socket = socket.socket
# socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_PROXY_HOST, config.SOCKS5_PROXY_PORT)
# socket.socket = socks.socksocket
regionId = ""  # 安全组所属地区ID
sec_group_id = ""   # 安全组ID，即为ec2_info的SecurityGroups数据的GroupId
port = 22  # 想添加的安全组白名单端口号，设置为-1即为开放所有端口
IpPermissions = [
            {
                'FromPort': port,
                'IpProtocol': 'tcp',
                'IpRanges': [{
                    'CidrIp': '1.1.1.1',  # 此处也可替换为0.0.0.0/0，即向所有ip开放端口
                    'Description': 'Allow'
                }],
                'Ipv6Ranges': [],
                'PrefixListIds': [],
                'ToPort': port,
                'UserIdGroupPairs': []
            },
        ]


def sec_add(AccessKeyID, AccessKeySecret):
    print("正在检索: " + regionId)
    ec2_client = boto3.client('ec2', region_name=regionId, aws_access_key_id=AccessKeyID,
                              aws_secret_access_key=AccessKeySecret)
    #  添加安全组白名单
    ec2_client.authorize_security_group_ingress(
        GroupId=sec_group_id,
        IpPermissions=IpPermissions
    )

    # 删除添加的安全组白名单
    ec2_client.revoke_security_group_ingress(
        GroupId=sec_group_id,
        IpPermissions=IpPermissions
    )

    # 查看当前安全组规则
    sec_group_response = ec2_client.describe_security_groups(GroupIds=[
        sec_group_id,
    ])
    print(sec_group_response['SecurityGroups'])


if __name__ == '__main__':
    AccessKeyID = config.AccessKeyID
    AccessKeySecret = config.AccessKeySecret
    sec_add(AccessKeyID, AccessKeySecret)
