
from tencentcloud.common.exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models
from tencentcloud.common import credential
from tencentcloud.tat.v20201028 import tat_client, models as tat_models
import json, base64, random, socket, socks, config
import time


# default_socket = socket.socket
# socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_PROXY_HOST, config.SOCKS5_PROXY_PORT)
# socket.socket = socks.socksocket


def DescribeAutomationAgentStatus(AccessKeyID, AccessKeySecret, ZoneId, InstanceId):
    cred = credential.Credential(AccessKeyID, AccessKeySecret)
    client = tat_client.TatClient(cred, ZoneId)
    req = tat_models.DescribeAutomationAgentStatusRequest()
    req.InstanceIds = InstanceId
    resp = client.DescribeAutomationAgentStatus(req)
    return resp


def CreateCommand(cred, com_type, command, ZoneId, InstanceId):
    client = tat_client.TatClient(cred, ZoneId)
    req = tat_models.CreateCommandRequest()

    name = ''.join(random.sample(
        ['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f', 'e',
         'd', 'c', 'b', 'a'], 5))
    try:
        InstanceIds = []
        InstanceIds.append(InstanceId)
        CloudAssistantStatus = DescribeAutomationAgentStatus(AccessKeyID, AccessKeySecret, ZoneId, InstanceIds)
        Status = CloudAssistantStatus.AutomationAgentSet[0].AgentStatus
        if Status == 'Offline':
            print('未安装自动化助手，不能执行命令。')
            return
        req.CommandName = name
        command = base64.b64encode(command.encode()).decode()
        req.Content = command
        req.CommandType = com_type
        response = client.CreateCommand(req)
        return response.CommandId
    except Exception as e:
        print(e)
        print('命令创建失败')


def InvokeCommand(cred, ZoneId, InstanceId, command_ID):
    client = tat_client.TatClient(cred, ZoneId)
    try:
        req = tat_models.InvokeCommandRequest()
        InstanceIds = []
        InstanceIds.append(InstanceId)
        req.InstanceIds = InstanceIds
        req.CommandId = command_ID
        resp = client.InvokeCommand(req)
        if resp.InvocationId == '':
            print('命令执行错误')
        else:
            return resp.InvocationId
    except Exception as e:
        print(e)
        print('命令执行失败')


def InvocationTaskIdTasks(cred, ZoneId, InvokeID):
    client = tat_client.TatClient(cred, ZoneId)
    req = tat_models.DescribeInvocationTasksRequest()
    InvocationTaskIds = []
    InvocationTaskIds.append(InvokeID)
    params = {
        "Filters": [{
            "Name": "invocation-id",
            "Values": InvocationTaskIds
        }],
        "HideOutput": False
    }
    req.from_json_string(json.dumps(params))
    resp = client.DescribeInvocationTasks(req)
    return resp


def DeleteCommand(cred, ZoneId, command_ID):
    client = tat_client.TatClient(cred, ZoneId)
    req = tat_models.DeleteCommandRequest()
    req.CommandId = command_ID
    resp = client.DeleteCommand(req)


def commad_check_input(cred, InstanceId, cmd, com_type, cvm_info):
    if cmd == '':
        cmd = input("please input cmd:")
    if com_type == None:
        com_type = input('请输入执行命令类型:'
                         '0:SHELL'
                         '1:POWERSHELL'
                         ':')
    if com_type == '0':
        com_type = 'SHELL'
    elif com_type == '1':
        com_type = 'POWERSHELL'

    Status = None
    ZoneId = None
    for instances in cvm_info:
        for instance in instances:
            if instance.InstanceId == InstanceId:
                Status = instance.InstanceState
                ZoneId = instance.Placement.Zone.rsplit("-", 1)[0]
                break
    if Status == 'STOPPED':
        print('实例未运行,请选择运行状态实例执行命令')
        return
    command_ID = CreateCommand(cred, com_type, cmd, ZoneId, InstanceId)
    InvokeID = InvokeCommand(cred, ZoneId, InstanceId, command_ID)
    time.sleep(1)
    Result = InvocationTaskIdTasks(cred, ZoneId, InvokeID)
    try:
        TaskStatus = Result.InvocationTaskSet[0].TaskStatus
        if TaskStatus == "SUCCESS":
            output = Result.InvocationTaskSet[0].TaskResult.Output
            print("命令执行结果：" + base64.b64decode(output).decode('utf-8', 'ignore'))
            DeleteCommand(cred, ZoneId, command_ID)
    except:
        pass
    return 0


def query_cvm_instances(cred):
    instance_list = []
    for RegionId in config.RegionIds:
        print('检索中-------' + RegionId)
        client = cvm_client.CvmClient(cred, RegionId)

        try:
            req = models.DescribeInstancesRequest()
            resp = client.DescribeInstances(req)
        except Exception as e:
            print(e)
            print('请检查输入Key与Secret值,或重新执行')
            continue
        instance_list.append(resp.InstanceSet)
    return instance_list


if __name__ == '__main__':
    AccessKeyID = config.AccessKeyID
    AccessKeySecret = config.AccessKeySecret
    if not AccessKeyID:
        AccessKeyID = input("请输入AccessKeyID:")
    if not AccessKeySecret:
        AccessKeySecret = input("请输入AccessKeySecret:")

    cred = None
    try:
        cred = credential.Credential(AccessKeyID, AccessKeySecret)
    except TencentCloudSDKException:
        print("AK或SK不正确，请输入正确的AKSK")
        exit(0)

    cvm_info = query_cvm_instances(cred)
    print(cvm_info)
    print("提示： 使用自动化助手在实例上执行命令，指定的实例需要处于 VPC 网络。json中参数为：VirtualPrivateCloud")
    if not cvm_info:
        print("no result")
        exit(0)
    InstanceId = input("请输入选择的instanceId:")
    com_type = None
    while True:
        if com_type is None:
            com_type = input('请输入执行命令类型:'
                             '0:SHELL'
                             '1:POWERSHELL'
                             ':')
        cmd = ''
        commad_check_input(cred, InstanceId, cmd, com_type, cvm_info)
        flag = input("输入q退出，其他字符继续:")
        if flag == 'q':
            break
        is_continue = input("重新选择InstanceId请输入yes:")
        if is_continue == 'yes':
            print(cvm_info)
            com_type = None
            InstanceId = input("请输入选择的instanceId:")