from aliyunsdkcore.client import AcsClient
from aliyunsdkrds.request.v20140815.DescribeDBInstancesRequest import DescribeDBInstancesRequest
from aliyunsdkrds.request.v20140815.DescribeDBInstanceIPArrayListRequest import DescribeDBInstanceIPArrayListRequest

import json, config
# import socket, socks
# default_socket = socket.socket
# socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_PROXY_HOST, config.SOCKS5_PROXY_PORT)
# socket.socket = socks.socksocket


def DescribeDB(AccessKeyID, AccessKeySecret, RegionIds):
    rds_list = {}
    for RegionId in RegionIds:
        print('检索中-------' + RegionId)
        client = AcsClient(AccessKeyID, AccessKeySecret, RegionId)
        try:
            request = DescribeDBInstancesRequest()
            request.set_accept_format('json')
            request.set_PageNumber(1)
            request.set_PageSize(100)

            response = client.do_action_with_exception(request)
        except Exception as e:
            print(e)
            print('请检查输入Key与Secret值,或重新执行')
            continue
        data = json.loads(response)
        for each in data['Items']['DBInstance']:
            securitygroup = DescribeDBSecurityGroup(AccessKeyID, AccessKeySecret, each["DBInstanceId"],
                                                    each["RegionId"])
            each["SecurityGroup"] = securitygroup
            rds_list[each["DBInstanceId"]] = each
    return rds_list


# 获取rds列表和白名单ip
def DescribeDBSecurityGroup(AccessKeyID, AccessKeySecret, DBInstanceId, RegionId):
    client = AcsClient(AccessKeyID, AccessKeySecret, RegionId)
    try:
        request = DescribeDBInstanceIPArrayListRequest()
        request.set_DBInstanceId(DBInstanceId)
        request.set_accept_format('json')
        response = client.do_action_with_exception(request)
        return json.loads(response)
    except Exception as e:
        print(e)
        print('请检查输入Key与Secret值,或重新执行')


if __name__ == '__main__':
    AccessKeyID = config.AccessKeyID
    AccessKeySecret = config.AccessKeySecret
    if not AccessKeyID:
        AccessKeyID = input("please input AccessKeyID:")
    if not AccessKeySecret:
        AccessKeySecret = input("please input AccessKeySecret:")
    result = DescribeDB(AccessKeyID, AccessKeySecret, config.RegionIds)
    print(result)
