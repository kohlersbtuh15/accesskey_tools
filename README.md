[English](./README.en.md) | 中文
# accesskey_tools
阿里云aliyun/腾讯云tencentcloud/华为云huaweicloud/aws等各种云厂商的accesskey自动化运维工具,accesskey利用工具，包括但不限于创建ecs、ecs查询和命令执行、oss查询和批量下载等各种功能，后续会持续添加各种功能

# 工具下载
```
git clone https://github.com/kohlersbtuh15/accesskey_tools.git
```
# 使用说明
```
cd aws/aliyun/tencentcloud #进入相应的云服务平台
pip3 install -r requirements.txt
vi config.py #填写AccessKeyID和AccessKeySecret，按需填写SOCKS5_PROXY_HOST和SOCKS5_PROXY_PORT
python3 aws_ec2_exec.py
```
# 功能描述
* IAM 查询当前aksk的用户权限，输入"enum"可进行接口服务爆破。
* EC2 查询aws各地区的ec2机器实例的详情信息，指定实例可执行系统命令，痕迹清理：删除创建的策略和绑定的iam。
* RDS 查询aws所有rds详情信息，以及IP白名单限制信息。
* S3 查询所有s3 bucket存储桶信息，可指定bucket以及bucket的文件夹。
* ROUTE53 查询aws所有地区创建的域名DNS记录。
* URL_CONSOLE 使用aksk申请联邦令牌，获取控制台权限(有效时间：15分钟)
# 快速上手
### 1、ec2机器实例查询并执行命令
执行脚本后会自动检索各个地区的ec2机器实例情况以及agent情况，并返回json。
![Img](./FILES/1.awebp)
![Img](./FILES/2.awebp)

输入机器实例，进行执行命令。会根据json中的数据自动选择执行命令的类型：
```
"Linux": "AWS-RunShellScript",
"windows": "AWS-RunPowerShellScript",
```
![Img](./FILES/3.awebp)

### 2、RDS查询
aws所有rds详情信息、快照详情、IP白名单限制信息。
![Img](./FILES/4.awebp)

### 3、S3 查询所有s3 bucket存储桶信息
all模式下载所有桶子中的所有文件。
可指定bucket以及bucket的文件夹。
![Img](./FILES/5.awebp)

### 4、ROUTE53
查询aws所有地区创建的域名DNS记录。
![Img](./FILES/6.awebp)

### 5、URL_CONSOLE
使用aksk申请联邦令牌，获取控制台权限(有效时间：15分钟)
![Img](./FILES/7.awebp)


关于工具使用方式可参考文章：

[accesskey_tools：一款针对云环境的多功能利用脚本工具](https://blog.csdn.net/saygoodbyeyo/article/details/132347160)
  

[accesskey_tools: 阿里云运维工具：自动化运维的利器](https://www.freebuf.com/sectool/377068.html)

[accesskey_tools: aws accesskey利用工具](https://www.freebuf.com/sectool/377988.html)

# 免责声明
该工具仅用于运维人员管理云上业务及安全测试，不得用于任何非法攻击。

# TODO

* 华为云huaweicloud accesskey相关功能
* 七牛云qiniuyun accesskey相关功能
