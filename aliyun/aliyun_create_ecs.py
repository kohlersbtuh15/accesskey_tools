# -*- coding: utf-8 -*-
from typing import List
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_ecs20140526.client import Client as EcsClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_vpc20160428 import models as vpc_models
from alibabacloud_vpc20160428.client import Client as VpcClient
from alibabacloud_ecs20140526 import models as ecs_models
from alibabacloud_darabonba_array.client import Client as ArrayClient

import config
# import socket, socks

# default_socket = socket.socket
# socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_PROXY_HOST, config.SOCKS5_PROXY_PORT)
# socket.socket = socks.socksocket


class Create_instances:
    def __init__(self):
        pass

    @staticmethod
    def main(
            access_key_id: str, access_key_secret: str, region_id: str, instance_type: str, image_id: str,
            security_group_id: str,
            zone_id: str, v_switch_id: str, password: str, autorelease_time: str,
            security_enhancement_strategy: str, dry_run: bool
    ):
        access_key_id = access_key_id
        access_key_secret = access_key_secret
        period = None
        period_unit = None
        auto_renew_period = None
        auto_renew = None
        available_info = {}
        if not region_id:
            for region in config.RegionIds:
                print(f'地区代码：{region}  对应地区: {config.RegionIds[region]}')
            region_id = input("请输入要创建的实例地区代码，如cn-hangzhou: ").replace(' ', '')
        config_client = Create_instances.create_client(access_key_id, access_key_secret, region_id)

        while True:
            if not zone_id:
                available_info = Create_instances.describe_zones(config_client, region_id)
                zone_id = input("请输入可用区ID: ").replace(' ', '')

            vpc_id = None
            if not v_switch_id or not vpc_id:
                vpcs = Create_instances.describe_vswitches(region_id, zone_id)
                if not vpcs:
                    print(f'[error] 所选可用区{zone_id}无可用虚拟交换机，请重新选择可用区或先创建虚拟交换机。')
                    zone_id = None
                    continue
                v_switch_id = input("请输入虚拟交换机ID: ").replace(' ', '')
                if v_switch_id not in vpcs.keys():
                    print(f'请输入正确的虚拟交换机ID: ')
                    continue
                else:
                    vpc_id = vpcs[v_switch_id]
                break

        if not instance_type:
            while True:
                cpucore_num = int(input("请输入要创建实例的CPU核数：").replace(' ', ''))
                memory_size = int(input("请输入要创建实例的内存大小(GB)：").replace(' ', ''))
                has_instancetypes = Create_instances.describe_instancetype(config_client, cpucore_num, memory_size,
                                                                           available_info[zone_id]['instance_types'])
                if not has_instancetypes:
                    print(f'[error] 可用区{zone_id}无符合要求的实例规格，请重新选择')
                else:
                    instance_type = input("请输入选择的实例类型ID: ").replace(' ', '')
                    break

        if not image_id:
            Create_instances.describe_images(config_client, region_id)
            image_id = input("请输入镜像ID：").replace(' ', '')

        if not security_group_id:
            Create_instances.describe_security_group(config_client, region_id, vpc_id)
            security_group_id = input("请输入安全组ID：").replace(' ', '')

        if not password:
            password = input(
                "请输入实例密码,长度为8至30个字符，必须同时包含大小写英文字母、数字和特殊符号中的三类字符，Windows实例不能以正斜线（/）为密码首字符： ").replace(
                ' ', '')
            print(f'以设定实例密码为: {password}')

        internet_charge_type = 'PayByBandwidth' if input(
            "请选择宽带付费方式, PayByBandwidth：按固定带宽计费；PayByTraffic：按使用流量计费。默认为按量计费: ") == 'PayByBandwidth' else 'PayByTraffic'
        internet_maxband_widthout = int(input("请输入公网出宽带最大值，范围为0 - 100Mbit / s: ").replace(' ', ''))
        internet_maxband_widthin = int(
            input("请输入公网如宽带最大值，范围为0 - internet_maxband_widthout Mbit / s: ").replace(' ', ''))
        systemdisk_size = int(input("请输入云盘大小，范围为 20-500 : ").replace(' ', ''))
        while True:
            systemdisk_category = input(
                "请输入云盘类型：cloud_efficiency：高效云盘，cloud_ssd：SSD云盘，cloud_essd：ESSD云盘，cloud：普通云盘，cloud_auto：ESSD AutoPL云盘: ").replace(
                ' ', '')
            if systemdisk_category not in available_info[zone_id]['diskcategory']:
                print(f'所选云盘类型{systemdisk_category}不支持，请重新选择: ')
            else:
                break
        amount = int(input("请输入要开启的实例数量 1-100 : ").replace(' ', ''))
        instance_charge_type = 'PrePaid' if input(
            "请输入实例付费方式，PrePaid：包年包月。PostPaid：按量付费, 默认为按量付费: ").replace(' ',
                                                                                               '') == 'PrePaid' else 'PostPaid'
        auto_pay = True if input(
            "创建实例时是否自动付费，设置True时若账户余额不足，会生成作废订单，只能重新创建；设置为False时，会在控制台生成待支付订单，可自行支付，默认不自动付费，请输入 T 或者 F: ").replace(
            ' ', '') == 'T' else False
        if instance_charge_type == 'PostPaid':
            autorelease_time = input("请输入自动施放时间，如2018-01-01T12:05:00Z，默认不自动释放: ").replace(' ', '')
            auto_pay = True
        if instance_charge_type == 'PrePaid':
            period_unit = input("请输入包年包月计费时长单位，取值范围：Week和Month: ").replace(' ', '')
            period = int(input("请输入购买资源时长，如 1 : ").replace(' ', ''))
            auto_renew = True if input("是否自动续费，如需自动续费请输入Y: ").replace(' ', '') == 'Y' else False
            if auto_renew:
                auto_renew_period = int(input("请输入自动续费时长，单位为包年包月计费单位,如 1 : ").replace(' ', ''))

        # 创建并与运行实例
        print(f'[info] --------开始创建实例-----------')
        responces = config_client.run_instances(ecs_models.RunInstancesRequest(
            region_id=region_id,
            instance_type=instance_type,
            image_id=image_id,
            security_group_id=security_group_id,
            zone_id=zone_id,
            v_switch_id=v_switch_id,
            amount=amount,
            password=password,
            internet_max_bandwidth_in=internet_maxband_widthin,
            internet_max_bandwidth_out=internet_maxband_widthout,
            internet_charge_type=internet_charge_type,
            auto_release_time=autorelease_time,
            security_enhancement_strategy=security_enhancement_strategy,
            period=period,
            period_unit=period_unit,
            auto_renew_period=auto_renew_period,
            instance_charge_type=instance_charge_type,
            auto_renew=auto_renew,
            auto_pay=auto_pay,
            dry_run=dry_run,
            system_disk=ecs_models.RunInstancesRequestSystemDisk(
                size=systemdisk_size,
                category=systemdisk_category
            )
        ))
        print(
            f'[info]-----------创建实例成功，实例ID:{UtilClient.to_jsonstring(responces.body.instance_id_sets.instance_id_set)}--------------')

    @staticmethod
    def describe_instancetype(
            client: EcsClient,
            cupcore_num: int,
            memory_size: int,
            available_types: List[str]

    ):
        describe_instance_types_request = ecs_models.DescribeInstanceTypesRequest(
            minimum_cpu_core_count=cupcore_num,
            maximum_cpu_core_count=cupcore_num,
            minimum_memory_size=memory_size,
            maximum_memory_size=memory_size
        )
        flag = False
        try:
            response = client.describe_instance_types(describe_instance_types_request)
            for instance_type in response.body.instance_types.instance_type:
                if instance_type.instance_type_id in available_types:
                    print(
                        f'实例类型ID: {instance_type.instance_type_id} 实例规格分类：{instance_type.instance_category} 系统架构：{instance_type.cpu_architecture} 处理器型号：{instance_type.physical_processor_model}')
                    flag = True
            return flag
        except Exception as error:
            # 如有需要，请打印 error
            print(error)

    @staticmethod
    def describe_images(
            client: EcsClient,
            region_id: str
    ):
        os_type = 'windows' if input('请输入镜像操作系统类型（linux或windows）,默认为linux：') == 'windows' else 'linux'
        page = 1
        while True:
            describe_images_request = ecs_models.DescribeImagesRequest(
                region_id=region_id,
                status='Available',
                ostype=os_type,
                page_size=50,
                page_number=page
            )
            response = client.describe_images(describe_images_request)
            for image in response.body.images.image:
                print(f'镜像ID:{image.image_id}{" " * (60 - len(image.image_id))}镜像名称：{image.osname}')
            if page * 50 > response.body.total_count:
                break
            page = page + 1

    @staticmethod
    def describe_vswitches(
            region_id: str,
            zone_id: str
    ):
        vswitches = {}
        describe_vswitch_request = vpc_models.DescribeVSwitchesRequest(
            region_id=region_id,
            zone_id=zone_id
        )
        response = VpcClient(open_api_models.Config(config.AccessKeyID, config.AccessKeySecret,
                                                    endpoint=f'vpc.aliyuncs.com')).describe_vswitches(
            describe_vswitch_request)
        for vswitch in response.body.v_switches.v_switch:
            vswitches[vswitch.v_switch_id] = vswitch.vpc_id
            print(
                f'虚拟交换机ID: {vswitch.v_switch_id}    虚拟网络ID: {vswitch.vpc_id}    虚拟交换机名称: {vswitch.v_switch_name}    虚拟网络段: {vswitch.cidr_block}')
        return vswitches

    @staticmethod
    def describe_security_group(
            client: EcsClient,
            region_id: str,
            vpc_id: str
    ):
        describe_security_request = ecs_models.DescribeSecurityGroupsRequest(
            region_id=region_id,
            vpc_id=vpc_id
        )
        response = client.describe_security_groups(describe_security_request)
        for security_group in response.body.security_groups.security_group:
            print(f'安全组ID: {security_group.security_group_id}    安全组名称: {security_group.security_group_name}')

    @staticmethod
    def describe_zones(
            client: EcsClient,
            region_id: str
    ):
        describe_zones_request = ecs_models.DescribeZonesRequest(
            region_id=region_id
        )
        response = client.describe_zones(describe_zones_request)
        available = {}
        for zone in response.body.zones.zone:
            print(f'zone_id: {zone.zone_id}')
            available[zone.zone_id] = {}
            available[zone.zone_id]['instance_types'] = zone.available_instance_types.instance_types
            available[zone.zone_id]['diskcategory'] = zone.available_disk_categories.disk_categories
        return available

    @staticmethod
    def create_client(
            access_key_id: str,
            access_key_secret: str,
            region_id: str,
    ) -> EcsClient:
        client_config = open_api_models.Config()
        client_config.access_key_id = access_key_id
        client_config.access_key_secret = access_key_secret
        client_config.region_id = region_id
        return EcsClient(client_config)


if __name__ == '__main__':
    access_key_id = config.AccessKeyID
    access_key_secret = config.AccessKeySecret
    # 地区
    region_id = ''
    # 实例规格
    instance_type = ''
    # 镜像id
    image_id = ''
    # 安全组id
    security_group_id = ''
    # 可用区id
    zone_id = ''
    # 交换机id
    v_switch_id = ''
    # 实例密码,长度为8至30个字符，必须同时包含大小写英文字母、数字和特殊符号中的三类字符，Windows实例不能以正斜线（/）为密码首字符。
    password = ''
    # 公网出宽带最大值，范围为0-100Mbit/s
    internet_maxband_widthout = 100
    # 公网入带宽最大值。最小为10Mbit/s, 最大为internet_maxband_widthout值
    internet_maxband_widthin = internet_maxband_widthout
    # 按量付费自动施放时间，按照ISO8601标准表示，使用UTC+0时间。格式为：yyyy-MM-ddTHH:mm:ssZ。如2018-01-01T12:05:00Z
    autorelease_time = ''
    # 是否开启安全加固
    security_enhancement_strategy = 'Active'
    # 预检请求
    # true：发送检查请求，不会创建实例。检查项包括是否填写了必需参数、请求格式、业务限制和ECS库存。如果检查不通过，则返回对应错误。如果检查通过，则返回DryRunOperation错误。
    # false：发送正常请求，通过检查后直接创建实例。
    dry_run = False
    if not access_key_id or not access_key_secret:
        print("请在config.py中设置accesskeyID和accesskeysecret")
        exit()
    try:
        Create_instances.main(access_key_id=config.AccessKeyID, access_key_secret=config.AccessKeySecret,
                              region_id=region_id, instance_type=instance_type, image_id=image_id,
                              security_group_id=security_group_id, zone_id=zone_id, v_switch_id=v_switch_id,
                              password=password, autorelease_time=autorelease_time,
                              security_enhancement_strategy=security_enhancement_strategy, dry_run=dry_run
                              )
    except Exception as e:
        print('[error] ---------实例创建失败---------')
        print(e)
