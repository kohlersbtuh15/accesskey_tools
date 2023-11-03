[English](./README.md) | 中文
## 文件说明

#### tencentcloud_cvm_exec.py
用于查询腾讯云各地区cvm实例的详细信息，并可指定cvm实例执行命令
#### tencentcloud_download_cos.py
用于查询腾讯云各地区的cos存储实例，并对cos存储实例中的文件进行下载
#### config.py
代码运行所需的配置信息，包括accesskey、accesskeysecret、代理的ip和端口等参数

## 使用说明
使用前安装所需的依赖，运行pip install -r requirements.txt即可，填好config.py中对应的值，直接运行对应的py脚本，按照提示输入对应的值

## 代理
代码中提供了socks代理，需要使用时在config.py中填好ip和port值，然后去掉代码中对应的注释部分即可
