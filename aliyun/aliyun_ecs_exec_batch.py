from aliyunsdkcore.client import AcsClient

from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.RunCommandRequest import RunCommandRequest
from aliyunsdkecs.request.v20140526.DescribeInvocationsRequest import DescribeInvocationsRequest

import json, base64, random, time, config, datetime

# import socket, socks

# default_socket = socket.socket
# socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_PROXY_HOST, config.SOCKS5_PROXY_PORT)
# socket.socket = socks.socksocket
headers = {"User-Agent": random.choice(config.user_agents)
           }


def DescribeInstances(AccessKeyID, AccessKeySecret):
    ecs_info = {}
    for RegionId in config.RegionIds:
        print('检索中-------' + RegionId)
        client = AcsClient(AccessKeyID, AccessKeySecret, RegionId)
        try:
            request = DescribeInstancesRequest()
            request.set_accept_format('json')
            request.set_PageNumber(1)
            request.set_PageSize(100)
            request.set_headers(headers)
            response = client.do_action_with_exception(request)
        except Exception as e:
            print(e)
            print('请检查输入Key与Secret值,或重新执行')
            continue
        for each in json.loads(response)['Instances']['Instance']:
            InstanceId = each["InstanceId"]
            ecs_info[InstanceId] = each
    return ecs_info


def DescribeInvocation(AccessKeyID, AccessKeySecret, RegionId, InvokeId):
    client = AcsClient(AccessKeyID, AccessKeySecret, RegionId)
    request = DescribeInvocationsRequest()
    request.set_headers(headers)
    request.set_InvokeId(InvokeId)
    request.set_IncludeOutput(True)
    request.set_PageSize(20)
    request.set_PageNumber(1)

    response = client.do_action_with_exception(request)
    return json.loads(response)


def RunCommand(AccessKeyID, AccessKeySecret, RegionId, command_type, commandContent, InstanceIds):
    client = AcsClient(AccessKeyID, AccessKeySecret, RegionId)
    request = RunCommandRequest()
    request.set_InstanceIds(InstanceIds)
    request.set_CommandContent(commandContent)
    request.set_Type(command_type)

    # 命令执行模式，默认立即执行命令，可填以下选项
    # Once: 立即执行命令
    # Period: 定时执行命令，当该参数取值为Period时，必须同时指定Frequency参数
    # NextRebootOnly: 当实例下一次启动时，自动执行命令
    # EveryReboot: 实例每一次启动都将自动执行命令
    # request.set_RepeatMode('Once')

    # 定时执行命令的执行时间
    # 固定时间间隔执行: rate(<执行间隔数值><执行间隔单位>),如5分钟执行一次，设置为rate(5m)
    # 仅在指定时间执行一次: at(yyyy-MM-dd HH:mm:ss <时区>),如指定在中国/上海时间2022年06月06日13时15分30秒执行一次，设置为at(2022-06-06 13:15:30 GMT-7:00)
    # 定时任务表达式： <Cron表达式> <时区>,如在中国/上海时间，2022年每天上午10:15执行一次命令，格式为0 15 10 ? * * 2022 Asia/Shanghai
    # request.set_Frequency("rate(5m)")

    # 在实例中执行命令的用户名称
    # request.set_Username("root")

    request.set_ContentEncoding('base64')
    request.set_Name("cmd_" + str(datetime.date.today()) + "_" + datetime.datetime.now().strftime("%H-%M-%S"))
    request.set_headers(headers)

    response = client.do_action_with_exception(request)
    return json.loads(response)


def commad_check_input(AccessKeyID, AccessKeySecret, InstanceIds, cmd, com_type, ecs_info):
    if cmd == '':
        cmd = input("please input cmd:")
    cmd = base64.b64encode(cmd.encode('utf-8'))
    com_types = {'0': 'RunShellScript', '1': 'RunBatScript', '2': 'RunPowerShellScript'}
    instances = {}
    for each in InstanceIds:
        if each not in ecs_info.keys():
            print(each + '实例不存在，请检查实例ID')
            continue
        Status = ecs_info[each]['Status']
        ZoneId = ecs_info[each]['RegionId']
        if Status == 'Stopped':
            print(each + '实例未运行,请选择运行状态实例执行命令')
            continue
        if ZoneId not in instances.keys():
            instances[ZoneId] = [each]
        else:
            instances[ZoneId].append(each)

    for ZoneId in instances.keys():
        result = RunCommand(AccessKeyID, AccessKeySecret, ZoneId, com_types[com_type], cmd, instances[ZoneId])
        time.sleep(2)
        run_result = DescribeInvocation(AccessKeyID, AccessKeySecret, ZoneId, result["InvokeId"])
        for InvokeInstance in run_result['Invocations']['Invocation'][0]['InvokeInstances']['InvokeInstance']:
            print(InvokeInstance['InstanceId'] + '执行结果：' + base64.b64decode(InvokeInstance['Output']).decode())


def main():
    ecs_info = DescribeInstances(config.AccessKeyID, config.AccessKeySecret)
    if not ecs_info:
        print("no result")
        exit(0)
    for each in ecs_info:
        print(each)
        print(ecs_info[each])
    InstanceIds = None
    while True:
        if InstanceIds is None:
            InstanceIds = input("请输入需要批量执行的instanceId，以逗号分隔,若要对所有机器执行命令，则输入all:")
            if InstanceIds == 'all':
                InstanceIds = list(ecs_info.keys())
            else:
                try:
                    InstanceIds = InstanceIds.replace('，', ',').replace(' ', '').split(',')
                except Exception as e:
                    print(e)
                    print("重新输入instanceId")
                    continue
        com_type = input('请输入执行命令类型:'
                         '0:RunShellScript'
                         '1:RunBatScript'
                         '2:RunPowerShellScript'
                         ':')
        if com_type not in ['0', '1', '2']:
            continue
        cmd = ''
        commad_check_input(config.AccessKeyID, config.AccessKeySecret, InstanceIds, cmd, com_type, ecs_info)
        flag = input("输入q退出，其他字符继续:")
        if flag == 'q':
            break
        is_continue = input("需要重新输入InstanceId请输入yes：")
        if is_continue == 'yes':
            InstanceIds = None


if __name__ == '__main__':
    main()
