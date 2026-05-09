# 查询ec2信息
import boto3
import config
import time
import aws_select_iam
import json
from enumerate_iam.main import get_client
from botocore.session import ComponentLocator
import urllib3
from aws_select_iam import iam_md5

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# import socket, socks
# default_socket = socket.socket
# socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_PROXY_HOST, config.SOCKS5_PROXY_PORT)
# socket.socket = socks.socksocket

def query_ec2_instances(AccessKeyID, AccessKeySecret):
    ec2_info = {}
    Agent_info = {}
    ec2 = boto3.client('ec2', region_name='us-east-1', aws_access_key_id=AccessKeyID,
                       aws_secret_access_key=AccessKeySecret)
    response = ec2.describe_regions()
    for region in response['Regions']:
        RegionId = region['RegionName']
        print("正在检索: " + RegionId)
        component = ComponentLocator()
        component.register_component(name='AWS_ENDPOINT', component=iam_md5[1:])
        ec2_client = get_client(access_key=AccessKeyID, secret_key=AccessKeySecret, service_name='ec2',
                                session_token=None,
                                region=RegionId, components=component)
        ssm_client = get_client(access_key=AccessKeyID, secret_key=AccessKeySecret, service_name='ssm',
                                session_token=None,
                                region=RegionId, components=component)
        try:
            ssm_ec2_infos = ssm_client.describe_instance_information()['InstanceInformationList']
            for ssm_ec2_info in ssm_ec2_infos:
                Agent_InstanceId = ssm_ec2_info['InstanceId']
                Agent_info[Agent_InstanceId] = ssm_ec2_info
            response = ec2_client.describe_instances()
            while True:
                for reservation in response['Reservations']:
                    InstanceId = reservation.get('Instances', [])[0].get('InstanceId')
                    ec2_info[InstanceId] = reservation.get('Instances', [])[0]
                    ec2_info[InstanceId]['RegionId'] = RegionId
                    ec2_info[InstanceId]['Agent'] = Agent_info.get(InstanceId)
                if "nextToken" in response:
                    response = ec2_client.describe_instances(
                        nextToken=response['nextToken']
                    )
                else:
                    break
        except AttributeError as e:
            print(e)
    return ec2_info


if __name__ == '__main__':
    AccessKeyID = config.AccessKeyID
    AccessKeySecret = config.AccessKeySecret
    if not AccessKeyID:
        AccessKeyID = input("请输入AccessKeyID:")
    if not AccessKeySecret:
        AccessKeySecret = input("请输入AccessKeySecret:")
    ec2_info = query_ec2_instances(AccessKeyID, AccessKeySecret)
    if not ec2_info:
        print("no ec2")
        exit(0)
    with open(f"ec2_info_{AccessKeyID}.json", 'w') as f:
        f.write(json.dumps(ec2_info, indent=4, sort_keys=True, default=str))
    print(f"ec2_info可在ec2_info_{AccessKeyID}.json文件中查看")
