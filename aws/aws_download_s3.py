import boto3
import queue
import threading
import os
import aws_select_iam
from concurrent.futures import ThreadPoolExecutor
import config
from enumerate_iam.main import get_client

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

def root_directory_list(prefix, bucket_name, flag=True):
    MAX_RETRIES = 10
    retry_count = 0
    s3_dir = []
    delimiter = ""
    if flag == False:
        delimiter = "/"
    try:
        retry_count += 1
        paginator = s3.get_paginator("list_objects_v2")
        get_object_iter = paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter=delimiter)

        for page in get_object_iter:
            commonprefix = page.get('CommonPrefixes')
            for obj in page['Contents']:
                if str(obj['Key'])[-1] == '/':
                    pass
                elif flag:
                    print(str(obj['Key']))
                    workqueue.put(str(obj['Key']))
            if commonprefix is not None:
                for cos_dir1 in commonprefix:
                    s3_dir.append(cos_dir1['Prefix'])
    except Exception:
        if retry_count >= MAX_RETRIES:
            raise
    return s3_dir

def download_to_local(object_name):
    url = "./" + bucket_name + "/" + object_name
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
                s3.download_file(bucket_name, object_name, url)
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

    s3 = get_client(access_key=AccessKeyID, secret_key=AccessKeySecret, service_name='s3', session_token=None,
                          region=None)
    buckets = [bucket['Name'] for bucket in s3.list_buckets()['Buckets']]
    print("Bucket List: %s" % buckets)

    BucketName = input("指定BucketName进行下载 或 all下载所有:")
    if BucketName == 'all':
        for bucket_name in buckets:
            thread = threading.Thread(target=root_directory_list, args=("", bucket_name))
            thread.start()
            workqueue_get()
    else:
        print(root_directory_list("", BucketName, False))
        oss_dir = input("指定存储桶文件夹 不指定则为根目录:")
        if BucketName:
            bucket_name = BucketName
            thread = threading.Thread(target=root_directory_list, args=(oss_dir, bucket_name))
            thread.start()
            workqueue_get()