from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.CreateCommandRequest import CreateCommandRequest
from aliyunsdkecs.request.v20140526.InvokeCommandRequest import InvokeCommandRequest
from aliyunsdkecs.request.v20140526.DescribeCloudAssistantStatusRequest import DescribeCloudAssistantStatusRequest
from aliyunsdkecs.request.v20140526.DescribeInvocationResultsRequest import DescribeInvocationResultsRequest

import json, base64, random, time, config

# import socket, socks
#
# default_socket = socket.socket
# socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_PROXY_HOST, config.SOCKS5_PROXY_PORT)
# socket.socket = socks.socksocket


def DescribeCloudAssistantStatus(AccessKeyID, AccessKeySecret, ZoneId, InstanceId):
    client = AcsClient(AccessKeyID, AccessKeySecret, ZoneId)
    request = DescribeCloudAssistantStatusRequest()
    request.set_accept_format('json')

    request.set_InstanceIds([InstanceId])

    response = client.do_action_with_exception(request)
    return json.loads(response)


def CreateCommand(AccessKeyID, AccessKeySecret, com_type, command, ZoneId, InstanceId):
    client = AcsClient(AccessKeyID, AccessKeySecret, ZoneId)

    request = CreateCommandRequest()
    request.set_accept_format('json')
    name = ''.join(random.sample(
        ['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f', 'e',
         'd', 'c', 'b', 'a'], 5))
    try:
        CloudAssistantStatus = DescribeCloudAssistantStatus(AccessKeyID, AccessKeySecret, ZoneId, InstanceId)
        Status = CloudAssistantStatus['InstanceCloudAssistantStatusSet']['InstanceCloudAssistantStatus'][0][
            'CloudAssistantStatus']
        if Status == 'false':
            print('no InstanceCloudAssistant,can not execute command!')
            return
        request.set_Name(name)
        request.set_Type(com_type)
        request.set_connect_timeout(60)
        command = base64.b64encode(command.encode()).decode()

        request.set_CommandContent(command)

        response = client.do_action_with_exception(request)
        return json.loads(response)['CommandId']
    except Exception as e:
        print(e)
        print('command create faild!')


def InvokeCommand(AccessKeyID, AccessKeySecret, ZoneId, InstanceId, CommandId):
    client = AcsClient(AccessKeyID, AccessKeySecret, ZoneId)

    try:
        request = InvokeCommandRequest()
        request.set_accept_format('json')

        request.set_CommandId(CommandId)
        request.set_InstanceIds([InstanceId])

        response = client.do_action_with_exception(request)
        if json.loads(response)['InvokeId'] == '':
            print('execute command error!')
        else:
            return json.loads(response)['InvokeId']
    except Exception as e:
        print(e)
        print('execute command error!')


def DescribeInvocationResults(AccessKeyID, AccessKeySecret, ZoneId, InvokeID):
    client = AcsClient(AccessKeyID, AccessKeySecret, ZoneId)

    request = DescribeInvocationResultsRequest()
    request.set_accept_format('json')

    request.set_InvokeId(InvokeID)

    response = client.do_action_with_exception(request)
    return json.loads(response)


def DescribeInstances(AccessKeyID, AccessKeySecret):
    ecs_info = {}
    for RegionId in config.RegionIds:
        print('searching -------' + RegionId)
        client = AcsClient(AccessKeyID, AccessKeySecret, RegionId)
        try:
            request = DescribeInstancesRequest()
            request.set_accept_format('json')
            request.set_PageNumber(1)
            request.set_PageSize(100)
            response = client.do_action_with_exception(request)
        except Exception as e:
            print(e)
            print('please check AccessKey and AccessKeySecret')
            continue
        for each in json.loads(response)['Instances']['Instance']:
            InstanceId = each["InstanceId"]
            ecs_info[InstanceId] = each
    return ecs_info


def commad_check_input(AccessKeyID, AccessKeySecret, InstanceId, cmd, com_type, ecs_info):
    if cmd == '':
        cmd = input("please input cmd:")
    if com_type == None:
        com_type = input('please input command type:'
                         '0:RunShellScript'
                         '1:RunBatScript'
                         '2:RunPowerShellScript'
                         ':')
    if com_type == '0':
        com_type = 'RunShellScript'
    elif com_type == '1':
        com_type = 'RunBatScript'
    elif com_type == '2':
        com_type = 'RunPowerShellScript'
    Status = ecs_info[InstanceId]['Status']
    ZoneId = ecs_info[InstanceId]['RegionId']
    if Status == 'Stopped':
        print('instance is stopped!')
        return
    if InstanceId not in ecs_info.keys():
        print('instance is not exist!')
        return
    command_ID = CreateCommand(AccessKeyID, AccessKeySecret, com_type, cmd, ZoneId, InstanceId)
    InvokeID = InvokeCommand(AccessKeyID, AccessKeySecret, ZoneId, InstanceId, command_ID)
    time.sleep(1)
    Result = DescribeInvocationResults(AccessKeyID, AccessKeySecret, ZoneId, InvokeID)
    try:
        output = Result['Invocation']['InvocationResults']['InvocationResult'][0]['Output']
        print("command result:" + base64.b64decode(output).decode())
    except:
        print("command result error!")
        pass
    return 0


if __name__ == '__main__':
    AccessKeyID = config.AccessKeyID
    AccessKeySecret = config.AccessKeySecret
    if not AccessKeyID:
        AccessKeyID = input("please input AccessKeyID:")
    if not AccessKeySecret:
        AccessKeySecret = input("please input AccessKeySecret:")
    ecs_info = DescribeInstances(AccessKeyID, AccessKeySecret)
    if not ecs_info:
        print("no result")
        exit(0)
    for each in ecs_info:
        print(each)
        print(ecs_info[each])
    InstanceId = input("please input instanceId:")
    com_type = None
    while True:
        if com_type is None:
            com_type = input('please input command type:'
                             '0:RunShellScript'
                             '1:RunBatScript'
                             '2:RunPowerShellScript'
                             ':')
        cmd = ''
        commad_check_input(AccessKeyID, AccessKeySecret, InstanceId, cmd, com_type, ecs_info)
        flag = input("input q quit,other key continue:")
        if flag == 'q':
            break
        is_continue = input("input yes to select other Instance:")
        if is_continue == 'yes':
            com_type = None
            InstanceId = input("please input instanceId:")
