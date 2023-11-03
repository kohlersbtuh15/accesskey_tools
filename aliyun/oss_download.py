import oss2
import os
import queue
import threading
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import json, base64, random, socket, socks, config


# default_socket = socket.socket
# socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_PROXY_HOST, config.SOCKS5_PROXY_PORT)
# socket.socket = socks.socksocket

workqueue = queue.Queue()
lock = threading.Lock()

def root_directory_list(prefix, bucket, flag=True):
    MAX_RETRIES = 10
    retry_count = 0
    cos_dir = []
    delimiter = ""
    if flag == False:
        delimiter = "/"
    while True:
        try:
            retry_count += 1
            get_object_iter = oss2.ObjectIterator(bucket, prefix=prefix, delimiter=delimiter)
            for obj in get_object_iter:
                if obj.is_prefix():
                    cos_dir.append(str(obj.key))
                elif flag:
                    workqueue.put(str(obj.key))
            break
        except Exception:
            if retry_count >= MAX_RETRIES:
                raise
    return cos_dir

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
                bucket.get_object_to_file(object_name, url)
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
    auth = None
    try:
        auth = oss2.Auth(AccessKeyID, AccessKeySecret)
        service = oss2.Service(auth, 'https://oss-cn-shenzhen.aliyuncs.com')
        for b in oss2.BucketIterator(service):
            BucketName_all[b.name] = b.extranet_endpoint
            print("Bucket名称：" + b.name, "Bucket创建时间：" + datetime.datetime.utcfromtimestamp(b.creation_date).strftime("%Y-%m-%d %H:%M:%S"), "外网域名：" + b.extranet_endpoint, "Bucket存储类型：" + b.storage_class)
    except oss2.exceptions.ServerError:
        print("AK或SK不正确，请输入正确的AKSK")
        exit(0)
    except oss2.exceptions.RequestError:
        print("网络异常，尝试切换代理")
        exit(0)

    BucketName = input("指定BucketName进行下载 或 all下载所有:")

    if BucketName == 'all':
        for name, endpoint in BucketName_all.items():
            bucket = oss2.Bucket(auth, endpoint, name)
            thread = threading.Thread(target=root_directory_list, args=("", bucket,))
            thread.start()
            workqueue_get()
    else:
        name = BucketName
        bucket = oss2.Bucket(auth, BucketName_all[BucketName], BucketName)
        print(root_directory_list("", bucket, False))
        oss_dir = input("指定存储桶文件夹 不指定则为根目录:")
        if BucketName:
            thread = threading.Thread(target=root_directory_list, args=(oss_dir, bucket,))
            thread.start()
            workqueue_get()
