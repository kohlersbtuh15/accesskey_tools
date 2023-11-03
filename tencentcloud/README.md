English | [中文](./README.zh-CN.md)
## File description

#### tencentcloud_cvm_exec.py
Used to query detailed information of cvm instances in various regions of Tencent Cloud and specify cvm instances to execute commands.
#### tencentcloud_download_cos.py
Used to query the cos storage instances of Tencent Cloud in various regions and download the files in the cos storage instances.
#### config.py
Configuration information required to run the code, including accesskey, accesskeysecret, proxy IP and port and other parameters

## Instructions for use
To install the required dependencies before use, run `pip install -r requirements.txt`, fill in the corresponding values ​​​​in config.py, run the corresponding py script directly, and enter the corresponding values ​​​​as prompted.

## proxy

The socks proxy is provided in the code. When you need to use it, fill in the ip and port values ​​​​in config.py, and then remove the corresponding comment part in the code.
