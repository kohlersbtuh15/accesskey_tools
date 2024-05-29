[English](./README.md) | 中文

# 需要python版本>=3.7

# 文件说明
## aws_download_s3.py
用于查询aws各个地区的s3存储桶的详情信息，可下载所有存储桶的文件，也可指定存储桶以及文件夹。

## aws_ec2_exec.py
用于查询aws各个地区的ec2机器实例详情，以及agent信息详情。可指定ec2实例id进行执行命令。
注意：脚本会自动创建角色和策略，将iam策略绑定到ec2实例上。使用完毕后，可使用脚本进行删除相关信息。

## aws_select_iam.py
用于查询aws当前aksk的权限，可输入enum进行爆破权限。

## aws_select_rds.py
用于查询aws各个地区的rds数据库实例及快照信息。

## aws_select_route53.py
用于查询aws各个地区的域名信息，会输出域名(.com等)以及详细的DNS配置信息(A,MX等记录)。

## aws_url_console.py
使用aksk做联邦令牌，然后生成的临时链接，有效期15分钟。

# 工具使用
```
git clone https://github.com/kohlersbtuh15/accesskey_tools

cd aws

pip3 install -r requirements.txt

python3 aws_ec2_exec.py

```
