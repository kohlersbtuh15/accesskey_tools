English | [中文](./README.zh-CN.md)

# require >= python3.7

# File description
## aws_download_s3.py
Used to query the detailed information of S3 buckets in various AWS regions. You can download the files of all buckets, and you can also specify buckets and folders.

## aws_ec2_exec.py
Used to query the details of ec2 machine instances in various AWS regions, as well as agent information details. You can specify the ec2 instance id to execute the command.
Note: The script will automatically create roles and policies and bind the iam policy to the ec2 instance. After use, you can use a script to delete relevant information.

## aws_select_iam.py
Used to query the current aksk permissions of AWS. You can enter enum to blast the permissions.

## aws_select_rds.py
Used to query rds database instances and snapshot information in various AWS regions.

## aws_select_route53.py
Used to query domain name information in various AWS regions, it will output domain names (.com, etc.) and detailed DNS configuration information (A, MX, etc. records).

## aws_url_console.py
Use aksk to create a federation token, and then generate a temporary link, which is valid for 15 minutes.

# Instructions for use
To install the required dependencies before use, run `pip3 install -r requirements.txt`, fill in the corresponding values ​​​​in config.py, run the corresponding py script directly, and enter the corresponding values ​​​​as prompted.

# proxy
The socks proxy is provided in the code. When you need to use it, fill in the ip and port values ​​​​in config.py, and then remove the corresponding comment part in the code.

# tools usage
```
git clone https://github.com/kohlersbtuh15/accesskey_tools

cd aws

pip3 install -r requirements.txt

python3 aws_ec2_exec.py

```
