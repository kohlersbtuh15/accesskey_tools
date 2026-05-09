[English](./README.en.md) | 中文

# 需要python版本>=3.7

# 文件说明
## aws_list_ec2.py
用于查询账户中所有ec2信息，以及各ec2 amazon ssm agent信息。

## aws_download_s3.py
用于查询aws各个地区的s3存储桶的详情信息，可下载所有存储桶的文件，也可指定存储桶以及文件夹。

## aws_ec2_exec.py
用于查询aws各个地区的ec2机器实例详情，以及agent信息详情。并指定ec2实例id进行执行命令。
注意：脚本会自动创建角色和策略，将iam策略绑定到ec2实例上。使用完毕后，可使用脚本进行删除相关信息。

## aws_ec2_exec_noinfo.py
和aws_ec2_exec.py相比去掉了查询ec2信息的步骤，如果近期运行过aws_ec2_exec.py或aws_list_ec2.py，就不用重复去查询ec2信息

## aws_security_ingress_add.py
用于查询aws指定安全组信息，并添加或删除入站规则。

## aws_push_sshpub.py
用于向指定ec2实例写入为期60秒的临时公钥，若ssh端口被安全组限制，可结合aws_security_ingress_add.py使用

## aws_select_rds.py
用于查询aws各个地区的rds数据库实例及快照信息。

## aws_select_route53.py
用于查询aws各个地区的域名信息，会输出域名(.com等)以及详细的DNS配置信息(A,MX等记录)。

## aws_url_console.py
使用aksk做联邦令牌，然后生成的临时链接，有效期15分钟。

# 使用说明
使用前，请运行 `pip3 install -r requirements.txt` 安装所需依赖项，然后在 config.py 文件中填写相应的值，直接运行相应的 py 脚本，并根据提示输入相应的值。

# 代理
代码中已提供 socks 代理。需要使用时，请在 config.py 文件中填写 IP 地址和端口号，然后删除代码中相应的注释部分。

# 工具使用
```
git clone https://github.com/kohlersbtuh15/accesskey_tools

cd aws

修改config.py，填写AccessKeyID和AccessKeyID

pip3 install -r requirements.txt

python3 aws_ec2_exec.py

```
