import json, base64, random, config
import qcloud_cos
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import queue
import threading
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# import socket, socks
# default_socket = socket.socket
# socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_PROXY_HOST, config.SOCKS5_PROXY_PORT)
# socket.socket = socks.socksocket

workqueue = queue.Queue()
lock = threading.Lock()


def workqueue_get():
    while True:
        if workqueue.qsize() > 50:
            keys = []
            for i in range(50):
                keys.append(workqueue.get())
            with ThreadPoolExecutor(max_workers=15) as executor:
                future_list = [executor.map(download_to_local, keys)]
        elif workqueue.qsize() < 50 and not thread.is_alive():
            keys1 = []
            for i in range(workqueue.qsize()):
                keys1.append(workqueue.get())
            with ThreadPoolExecutor(max_workers=15) as executor:
                future_list = [executor.map(download_to_local, keys1)]
            break


def root_directory_list(prefix, bucket_name, client, flag=True):
    MAX_RETRIES = 10
    retry_count = 0
    marker = ""
    cos_dir = []
    delimiter = ""
    if flag == False:
        delimiter = "/"
    while True:
        try:
            retry_count += 1
            response = client.list_objects(
                Bucket=bucket_name,
                Prefix=prefix,
                Marker=marker,
                Delimiter=delimiter,
            )
            marker = response.get('NextMarker')
            commonprefix = response.get('CommonPrefixes')
            for obj in (response['Contents']):
                if str(obj['Key'])[-1] == '/':
                    pass
                elif flag:
                    # print(str(obj['Key']))
                    workqueue.put(str(obj['Key']))
            if commonprefix is not None:
                for cos_dir1 in commonprefix:
                    cos_dir.append(cos_dir1['Prefix'])
            if marker is None:
                break
        except Exception as e:
            print(e)
            if retry_count >= MAX_RETRIES:
                raise
    return cos_dir


def download_to_local(object_name):
    url = "./" + name + "/" + object_name
    file_name = url[url.rindex("/") + 1:]
    file_path_prefix = url.replace(file_name, "")
    lock.acquire()
    if not os.path.exists(file_path_prefix):
        os.makedirs(file_path_prefix)
    lock.release()
    if not os.path.exists(url):
        MAX_RETRIES = 10
        retry_count = 0
        while True:
            try:
                retry_count += 1
                print("开始下载：" + object_name)
                response = client.get_object(Bucket=name, Key=object_name)
                response['Body'].get_stream_to_file(url)
                print("下载完毕" + url)
                break
            except Exception as e:
                print(e)
                if retry_count >= MAX_RETRIES:
                    raise


if __name__ == '__main__':
    AccessKeyID = config.AccessKeyID
    AccessKeySecret = config.AccessKeySecret
    if not AccessKeyID:
        AccessKeyID = input("请输入AccessKeyID:")
    if not AccessKeySecret:
        AccessKeySecret = input("请输入AccessKeySecret:")

    BucketName_all = {}
    token = None
    scheme = 'https'
    try:
        config = CosConfig(Region="ap-guangzhou", SecretId=AccessKeyID, SecretKey=AccessKeySecret, Token=token,
                           Scheme=scheme)
        client = CosS3Client(config)
        response = client.list_buckets()
        for bucket in response['Buckets']['Bucket']:
            BucketName_all[bucket['Name']] = bucket['Location']
            print("Bucket名称：" + bucket['Name'], "Bucket创建时间：" + bucket['CreationDate'],
                  "外网域名：" + bucket['Location'], "Bucket存储类型：" + bucket['BucketType'])
    except qcloud_cos.cos_exception.CosServiceError:
        print("AK或SK不正确，请输入正确的AKSK")
        exit(0)
    except qcloud_cos.cos_exception.CosClientError:
        print("网络异常，尝试切换代理")
        exit(0)

    BucketName = input("指定BucketName进行下载 或 all下载所有:")

    if BucketName == 'all':
        for name, region in BucketName_all.items():
            config = CosConfig(Region=region, SecretId=AccessKeyID, SecretKey=AccessKeySecret, Token=token,
                               Scheme=scheme)
            client = CosS3Client(config)
            thread = threading.Thread(target=root_directory_list, args=("", name, client))
            thread.start()
            workqueue_get()
    else:
        name = BucketName
        region = BucketName_all[BucketName]
        config = CosConfig(Region=region, SecretId=AccessKeyID, SecretKey=AccessKeySecret, Token=token,
                           Scheme=scheme)
        client = CosS3Client(config)
        print(root_directory_list("", BucketName, client, False))
        oss_dir = input("指定存储桶文件夹 不指定则为根目录:")
        if BucketName:
            thread = threading.Thread(target=root_directory_list, args=(oss_dir, BucketName, client))
            thread.start()
            workqueue_get()
