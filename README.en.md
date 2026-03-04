English | [中文](./README.md)
# accesskey_tools
The accesskey automated operation and maintenance tools and accesskey utilization tools of various cloud vendors such as alicloud/tencentcloud/huaweicloud/aws, including but not limited to various functions such as creating ecs, ecs query and command execution, oss query and batch download, will continue to be added in the future. Various functions.

## Function description
* IAM queries the current user permissions of aksk. Enter "enum" to perform interface service blasting.

* EC2 Query the detailed information of EC2 machine instances in various AWS regions. The specified instance can execute system commands. Trace cleaning: delete the created policy and bound IAM.

* RDS queries all rds details of AWS, as well as IP whitelist restriction information.

* S3 queries all s3 bucket bucket information, and you can specify the bucket and bucket folder.

* ROUTE53 queries the domain name DNS records created by AWS in all regions.

* URL_CONSOLE Use aksk to apply for a federation token and obtain console permissions (valid time: 15 minutes)

## Get started quickly

### Query and execute commands on the ec2 machine instance. 
After executing the script, the ec2 machine instance status in each region will be automatically retrieved and json will be returned.
![Img](./FILES/1.awebp)
![Img](./FILES/2.awebp)

You can choose whether to delete the created roles and policies.

You can also delete the iam bound to the ec2 machine.

Enter the machine instance to execute the command. The type of command to be executed will be automatically selected based on the data in json:
```
"Linux": "AWS-RunShellScript",
"windows": "AWS-RunPowerShellScript"
```
![Img](./FILES/3.awebp)
### RDS queries all rds details of AWS, 
as well as IP whitelist restriction information.
![Img](./FILES/4.awebp)
### S3 queries all s3 bucket bucket information 
all mode downloads all files in all buckets.
You can specify the bucket and bucket folder.
![Img](./FILES/5.awebp)
### ROUTE53 
Query the domain name DNS records created by AWS in all regions.
![Img](./FILES/6.awebp)
### URL_CONSOLE 
Use aksk to apply for a federation token and obtain console permissions (valid time: 15 minutes)
![Img](./FILES/7.awebp)


For information on how to use the tool, please refer to the article：

[accesskey_tools: An Alibaba Cloud operations and maintenance tool for automation](https://kohlersbtuh15s-organization.gitbook.io/alibabacloud_accesskey_tools/)

[AWS AccessKey Tools: Powerful Security Assessment and Penetration Testing Tools](https://kohlersbtuh15s-organization.gitbook.io/aws_accesskey_tools/)
# Disclaimer
This tool is only used by operation and maintenance personnel to manage cloud business and security testing, and may not be used for any illegal attacks.

# TODO

* huaweicloud accesskey related functions
* qiniuyun accesskey related functions
