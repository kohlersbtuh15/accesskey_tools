import config
import boto3
import json
from enumerate_iam.main import enumerate_iam
from enumerate_iam.main import get_client

# import socket, socks
# default_socket = socket.socket
# socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_PROXY_HOST, config.SOCKS5_PROXY_PORT)
# socket.socket = socks.socksocket

def user_info(iam_resource):
    current_user = iam_resource.CurrentUser()
    print("\nUserInfo:")
    print("\tuser_id:\t\t", current_user.user_id)
    global user_name
    user_name = current_user.user_name
    print("\tuser_name:\t\t", user_name)
    print("\tThe username is also the accountID.")
    print("\tcreate_date:\t\t", current_user.create_date)
    arn = current_user.arn
    print("\tarn:\t\t\t", arn)
    print("\tpath:\t\t\t", current_user.path)
    print("\tpermissions_boundary:\t", current_user.permissions_boundary)
    print("\ttags:\t\t\t", current_user.tags)
    print("\tpassword_last_used:\t", current_user.password_last_used)
    return arn

def get_attached_policies(iam_client, iam_resource):
    attached_response = iam_client.list_attached_user_policies(UserName=user_name, PathPrefix='/', MaxItems=123)
    attached_policy_lst = attached_response.get("AttachedPolicies")
    for p_dic in attached_policy_lst:
        arn = p_dic.get("PolicyArn")
        name = p_dic.get("PolicyName")
        policy = iam_resource.Policy(arn)
        v_id = policy.default_version_id
        policy_version = iam_resource.PolicyVersion(arn, v_id)
        document = json.dumps(policy_version.document, indent=2)
        print(f"\naws托管策略: {name}\n{document}")

def get_inline_policies(iam_client):
    response = iam_client.list_user_policies(UserName=user_name)
    policy_lst = response.get("PolicyNames")
    for p in policy_lst:
                user_policy_response = iam_client.get_user_policy(
                    UserName=user_name, PolicyName=p)
                policy_document = json.dumps(
                    user_policy_response.get("PolicyDocument"), indent=2)
                print(f"内联策略: {p}\n{policy_document}")

if __name__ == '__main__':
    AccessKeyID = config.AccessKeyID
    AccessKeySecret = config.AccessKeySecret
    if not AccessKeyID:
        AccessKeyID = input("请输入AccessKeyID: ")
    if not AccessKeySecret:
        AccessKeySecret = input("请输入AccessKeySecret: ")

    iam_client = get_client(access_key=AccessKeyID, secret_key=AccessKeySecret, service_name='iam', session_token=None,
                          region=None)
    iam_resource = boto3.resource('iam', aws_access_key_id=AccessKeyID, aws_secret_access_key=AccessKeySecret)
    userinfo = user_info(iam_resource)
    if "root" in userinfo:
        print("\tYou are already root, no need to do a permission query")
    else:
        get_attached_policies(iam_client, iam_resource)
        get_inline_policies(iam_client)
    enum_select = input("输入\"enum\" 通过api枚举具体权限情况:")
    if enum_select == "enum":
        enumerate_iam(access_key=AccessKeyID,
                          secret_key=AccessKeySecret,
                          session_token=None,
                          region=None)
    else:
        pass