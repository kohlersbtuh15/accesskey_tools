import config
import boto3
import aws_select_iam
from botocore.exceptions import ClientError
from enumerate_iam.main import get_client

# import socket, socks
# default_socket = socket.socket
# socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_PROXY_HOST, config.SOCKS5_PROXY_PORT)
# socket.socket = socks.socksocket

def get_hosted_zones(client):
    hosted_zones = []
    paginator = client.get_paginator("list_hosted_zones")
    for hosted_zone in paginator.paginate():
        hosted_zones += hosted_zone["HostedZones"]
    zones = {}

    if len(hosted_zones) > 0:
        for zone in hosted_zones:
            zid = zone["Id"].split("/")[2]
            print(
                f"ZoneID: {zid}  Name: {zone['Name']} Private: {zone['Config']['PrivateZone']} "
            )
            zones[zid] = zone
    else:
        print("No HostedZones found")

    return zones

def get_query_logging_config(client):
    configs = client.list_query_logging_configs()["QueryLoggingConfigs"]

    if len(configs) > 0:
        print("QueryLoggingConfigs:")
        for con in configs:
            print(
                f"ZoneID: {con['HostedZoneId']} :: CloudWatchLogsLogGroupArn: {con['CloudWatchLogsLogGroupArn']}"
            )
    else:
        print("No QueryLoggingConfigs found")

    return configs

def query_route53_instances(AccessKeyID, AccessKeySecret):
    all_records_for_zone = []
    record_sets = {}
    route53_client = get_client(access_key=AccessKeyID, secret_key=AccessKeySecret, service_name='route53', session_token=None,
                            region=None)
    try:
        zones = get_hosted_zones(client=route53_client)
        for hosted_zone_id in zones.keys():
            paginator = route53_client.get_paginator("list_resource_record_sets")
            for resource_records in paginator.paginate(HostedZoneId=hosted_zone_id):
                all_records_for_zone += resource_records["ResourceRecordSets"]
            record_sets[hosted_zone_id] = {"ResourceRecordSets": all_records_for_zone}
            if len(record_sets[hosted_zone_id]) > 0:
                print(f"\nResourceRecordSets for {hosted_zone_id}:")
                for record in record_sets[hosted_zone_id]["ResourceRecordSets"]:
                    print(f"Name: {record['Name']} Type: {record['Type']}")
            else:
                print("No ResourceRecordSets found")

    except ClientError as error:
        print(f"Failed to list R53 Hosted Zones: {error}")
        return

    try:
        confs = get_query_logging_config(client=route53_client)
    except ClientError as error:
        print(f"Failed to list R53 Hosted Zone Query Logging Configurations: {error}")
        return

if __name__ == '__main__':
    AccessKeyID = config.AccessKeyID
    AccessKeySecret = config.AccessKeySecret
    if not AccessKeyID:
        AccessKeyID = input("请输入AccessKeyID:")
    if not AccessKeySecret:
        AccessKeySecret = input("请输入AccessKeySecret:")

    route53_info = query_route53_instances(AccessKeyID, AccessKeySecret)