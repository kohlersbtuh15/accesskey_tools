import config
import boto3
import aws_select_iam
from enumerate_iam.main import get_client

# import socket, socks
# default_socket = socket.socket
# socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_PROXY_HOST, config.SOCKS5_PROXY_PORT)
# socket.socket = socks.socksocket

def query_rds_instances(AccessKeyID, AccessKeySecret):
    rds_info = {}
    ec2 = boto3.client('ec2', region_name='us-east-1', access_key=AccessKeyID, secret_key=AccessKeySecret)
    response = ec2.describe_regions()
    for region in response['Regions']:
        RegionId = region['RegionName']
        print("正在检索: " + RegionId)
        try:
            rds_client = get_client(access_key=AccessKeyID, secret_key=AccessKeySecret, service_name='rds', session_token=None,
                        region=RegionId)
            response = rds_client.describe_db_instances()
            for DBInstance in response['DBInstances']:
                print(DBInstance)
                # 不知道后期要用什么，所以索性全部输出，后续再加功能。值得关注的点 Endpoint， DBSecurityGroups --> describe_db_security_groups。
            snapshots_response = rds_client.describe_db_snapshots()
            if len(snapshots_response['DBSnapshots']) != 0:
                print(snapshots_response)
            cluster_snapshots_response = rds_client.describe_db_cluster_snapshots()
            if len(cluster_snapshots_response['DBClusterSnapshots']) != 0:
                print(cluster_snapshots_response)
        except AttributeError as e:
            pass
        continue

        # 快照属性
        # snapshot_attributes_response = rds_client.describe_db_snapshot_attributes(
        #     DBClusterSnapshotIdentifier='mydbclustersnapshot',
        # )

        # 集群快照属性
        # cluster_snapshot_attributes_response = rds_client.describe_db_cluster_snapshot_attributes(
        #     DBClusterSnapshotIdentifier='mydbclustersnapshot',
        # )

    # return rds_info
if __name__ == '__main__':
    AccessKeyID = config.AccessKeyID
    AccessKeySecret = config.AccessKeySecret
    if not AccessKeyID:
        AccessKeyID = input("请输入AccessKeyID:")
    if not AccessKeySecret:
        AccessKeySecret = input("请输入AccessKeySecret:")

    rds_info = query_rds_instances(AccessKeyID, AccessKeySecret)
    print(rds_info)