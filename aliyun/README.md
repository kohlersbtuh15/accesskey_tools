English | [中文](./README.zh-CN.md)
## File description

#### aliyun_ecs_exec.py
Used to query the detailed information of ecs instances in various regions of Alibaba Cloud and specify the ecs instance to execute commands.
#### aliyun_ecs_exec_batch.py
Used to query the detailed information of ecs instances in various regions of Alibaba Cloud and execute ecs instance commands in batches
#### aliyun_create_ecs.py
Used to create Alibaba Cloud instances in batches
#### aliyun_getall_rds.py
Used to query all Alibaba Cloud RDS details and their IP restrictions
#### oss_download.py
Used to download all files in oss, and can also specify a bucket for download.
#### config.py
Configuration information required to run the code, including accesskey, accesskeysecret, proxy IP and port and other parameters

## Instructions for use
To install the required dependencies before use, run `pip install -r requirements.txt`, fill in the corresponding values ​​​​in config.py, run the corresponding py script directly, and enter the corresponding values ​​​​as prompted.

## proxy
The socks proxy is provided in the code. When you need to use it, fill in the ip and port values ​​​​in config.py, and then remove the corresponding comment part in the code.
