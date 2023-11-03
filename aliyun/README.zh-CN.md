[English](./README.md) | 中文
## 文件说明

#### aliyun_ecs_exec.py
用于查询阿里云各地区ecs实例的详细信息，并可指定ecs实例执行命令
#### aliyun_ecs_exec_batch.py
用于查询阿里云各地区ecs实例的详细信息，并可批量执行ecs实例命令
#### aliyun_create_ecs.py
用于批量创建阿里云实例
#### aliyun_getall_rds.py
用于查询阿里云所有rds详细信息和其ip限制
#### oss_download.py
用于下载所有oss中的文件，也可指定bucket下载
#### config.py
代码运行所需的配置信息，包括accesskey、accesskeysecret、代理的ip和端口等参数

## 使用说明
使用前安装所需的依赖，运行pip install -r requirements.txt即可，填好config.py中对应的值，直接运行对应的py脚本，按照提示输入对应的值

## 代理
代码中提供了socks代理，需要使用时在config.py中填好ip和port值，然后去掉代码中对应的注释部分即可
