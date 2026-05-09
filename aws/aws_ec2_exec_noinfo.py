# 从本地文件中获取ec2信息并执行命令
import boto3
import config
import time
import json, os
import urllib3
import aws_select_iam

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# import socket, socks
# default_socket = socket.socket
# socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_PROXY_HOST, config.SOCKS5_PROXY_PORT)
# socket.socket = socks.socksocket


def create_instance_profile(iam_client):
    with open("amazon_ssm_managed_instance_core.json",
              mode="r",
              encoding="utf-8") as f:
        json2 = f.read()
    iam_client.create_policy(
        PolicyName='ssm_policy',
        Path='/',
        PolicyDocument=json2,
    )
    with open("ec2_role_trust_policy.json", mode="r",
              encoding="utf-8") as f:
        json1 = f.read()
    iam_client.create_role(
        Path='/',
        RoleName='AmazonSSMManagedInstance',
        AssumeRolePolicyDocument=json1,
        Description=
        'Allows EC2 instances to call AWS services on your behalf.',
    )
    iam_client.put_role_policy(RoleName='AmazonSSMManagedInstance',
                               PolicyName='ssm_policy',
                               PolicyDocument=json2)
    instance_profile_name = "SSMFullAccessProfile"
    response3 = iam_client.create_instance_profile(
        InstanceProfileName=instance_profile_name)
    instance_profile_arn = response3.get("InstanceProfile").get("Arn")
    iam_client.add_role_to_instance_profile(
        InstanceProfileName=instance_profile_name,
        RoleName='AmazonSSMManagedInstance')
    return instance_profile_arn, instance_profile_name


def delete_instance_profile(AccessKeyID, AccessKeySecret):
    iam_client = boto3.client('iam', aws_access_key_id=AccessKeyID, aws_secret_access_key=AccessKeySecret)
    response = iam_client.list_users()
    usernames = [user['UserName'] for user in response['Users']]
    instance_profile_name = "SSMFullAccessProfile"
    try:
        response1 = iam_client.remove_role_from_instance_profile(
            InstanceProfileName=instance_profile_name,
            RoleName='AmazonSSMManagedInstance'
        )
        response2 = iam_client.delete_instance_profile(
            InstanceProfileName=instance_profile_name
        )
        response3 = iam_client.delete_role_policy(
            RoleName='AmazonSSMManagedInstance',
            PolicyName='ssm_policy'
        )
        response4 = iam_client.delete_role(
            RoleName='AmazonSSMManagedInstance'
        )
        iam_resource = boto3.resource('iam', aws_access_key_id=AccessKeyID, aws_secret_access_key=AccessKeySecret)
        userinfos = aws_select_iam.user_info(iam_resource)
        policy_arn = ":".join(userinfos.split(":")[:-1])
        arn = str(policy_arn) + ":policy/ssm_policy"
        response5 = iam_client.delete_policy(
            PolicyArn=arn
        )
        print("已删除 HTTPStatusCode：" + "{}".format(response5['ResponseMetadata']['HTTPStatusCode']))
        exit(0)
    except Exception as err:
        print(err)


def associate_iam_add(RegionId, AccessKeyID, AccessKeySecret, InstanceId):
    instance_profile_arn, instance_profile_name = get_instance_profile(AccessKeyID, AccessKeySecret)
    print(instance_profile_arn)
    try:
        client_ec2 = boto3.client('ec2', region_name=RegionId, aws_access_key_id=AccessKeyID,
                                  aws_secret_access_key=AccessKeySecret)
        response = client_ec2.associate_iam_instance_profile(
            IamInstanceProfile={
                'Arn': instance_profile_arn,
                'Name': instance_profile_name,
            },
            InstanceId=InstanceId)
        if response.get("ResponseMetadata").get("HTTPStatusCode") == 200:
            print(
                "实例配置文件关联成功，但是生效需要一定的等待时间，一般10分钟左右，请稍后再执行命令"
            )
        else:
            print("ec2实例配置文件关联失败")
    except Exception:
        print("实例配置文件创建成功,但是关联失败，请重新执行")
    return True


def associate_iam_delete(RegionId, AccessKeyID, AccessKeySecret, InstanceId):
    client_ec2 = boto3.client('ec2', region_name=RegionId, aws_access_key_id=AccessKeyID,
                              aws_secret_access_key=AccessKeySecret)
    responses = client_ec2.describe_iam_instance_profile_associations()
    for response in responses['IamInstanceProfileAssociations']:
        if InstanceId == response['InstanceId']:
            AssociationId = response['AssociationId']
            response = client_ec2.disassociate_iam_instance_profile(
                AssociationId=AssociationId,
            )
        time.sleep(1)


def get_instance_profile(AccessKeyID, AccessKeySecret):
    iam_client = boto3.client('iam', aws_access_key_id=AccessKeyID, aws_secret_access_key=AccessKeySecret)
    response = iam_client.list_instance_profiles(PathPrefix='/', MaxItems=123)
    instance_profiles_lst = response.get("InstanceProfiles")
    for instance_profile in instance_profiles_lst:
        name = instance_profile.get("InstanceProfileName")
        if name == "SSMFullAccessProfile":
            instance_profile_arn = instance_profile.get("Arn")
            print("检测到已经创建过实例配置文件，正在关联...")
            return instance_profile_arn, name
    print("检测到没有创建实例配置文件，正在创建实例配置文件...")
    instance_profile_arn, name = create_instance_profile(iam_client)
    return instance_profile_arn, name


def commad_exec(AccessKeyID, AccessKeySecret, InstanceId, cmd, com_type, RegionId):
    if cmd == '':
        cmd = input("please input cmd:")
    ssm_client = boto3.client('ssm', region_name=RegionId, aws_access_key_id=AccessKeyID,
                              aws_secret_access_key=AccessKeySecret)
    print(InstanceId)
    print(com_type)
    if com_type is None:
        com_type = input("please input com_type AWS-RunShellScript or AWS-RunPowerShellScript: ")
    print(cmd)
    response = ssm_client.send_command(
        InstanceIds=[
            InstanceId,
        ],
        DocumentName=com_type,
        Parameters={'commands': [cmd]},
    )
    command_id = response['Command']['CommandId']
    time.sleep(1)

    i = 0
    while 1:
        output = ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=InstanceId,
        )
        if output.get("Status") == "Success" and output.get("StatusDetails") == "Success":
            break
        i += 1
        time.sleep(i)
        if i > 3:
            break

    cmd_output = output.get("StandardOutputContent") + output.get(
        "StandardErrorContent").strip()
    print(cmd_output)


if __name__ == '__main__':
    AccessKeyID = config.AccessKeyID
    AccessKeySecret = config.AccessKeySecret
    if not AccessKeyID:
        AccessKeyID = input("请输入AccessKeyID:")
    if not AccessKeySecret:
        AccessKeySecret = input("请输入AccessKeySecret:")
    if not os.path.exists(f"ec2_info_{AccessKeyID}.json"):
        print("请先运行aws_list_ec2.py获取ec2信息或直接使用aws_ec2_exec.py")
        exit(0)
    with open(f"ec2_info_{AccessKeyID}.json", "r") as f:
        ec2_info = json.load(f)
    # AWS-RunShellScript code
    platform_dic = {
        "Linux": "AWS-RunShellScript",
        "windows": "AWS-RunPowerShellScript",
    }
    com_type = None
    InstanceId = input("请输入选择的instanceId:")
    RegionId = ec2_info[InstanceId]['RegionId']
    while True:
        if "Linux" in ec2_info[InstanceId]['PlatformDetails']:
            com_type = platform_dic.get('Linux')
        elif "windows" in ec2_info[InstanceId]['PlatformDetails']:
            com_type = platform_dic.get('windows')
        else:
            com_type = input("无法判断机器平台，请手动输入'AWS-RunShellScript' 或 'AWS-RunPowerShellScript': ")

        if not ec2_info[InstanceId].get('IamInstanceProfile'):
            if associate_iam_add(RegionId, AccessKeyID, AccessKeySecret, InstanceId):
                time.sleep(2)
        cmd = ''
        if ec2_info[InstanceId].get('Agent'):
            try:
                commad_exec(AccessKeyID, AccessKeySecret, InstanceId, cmd, com_type, RegionId)
                if not ec2_info[InstanceId].get('IamInstanceProfile'):
                    associate_iam_delete(RegionId, AccessKeyID, AccessKeySecret, InstanceId)
                    delete_instance_profile(AccessKeyID, AccessKeySecret)
            except Exception as err:
                print("策略绑定可能未生效，请等待一会儿(大概10分钟)再执行该脚本。具体看SSM agent是否绑定。")
                print(err)
                continue
        else:
            print("该机器没有安装SSM agent，无法执行命令。")
        is_continue = input("重新选择InstanceId请输入yes，退出请输入q，任意输入继续执行其他命令:")
        if is_continue == 'q':
            break
        elif is_continue == 'yes':
            com_type = None
            InstanceId = input("请输入选择的instanceId:")
