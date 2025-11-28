from aws_consoler.cli import main
import config
import re
import requests
import json
import boto3
import sys
import aws_select_iam
from botocore.exceptions import ClientError
from botocore.session import ComponentLocator
from enumerate_iam.main import get_client
from aws_select_iam import iam_md5
import urllib.parse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#import socket, socks
#default_socket = socket.socket
#socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_PROXY_HOST, config.SOCKS5_PROXY_PORT)
#socket.socket = socks.socksocket


def _get_partition_endpoints(region: str):
    # AWS China endpoints
    if re.match(r"^cn-\w+-\d+$", region):
        return {
            "partition": "aws-cn",
            "console": "https://console.amazonaws.cn/console/home",
            "federation": "https://signin.amazonaws.cn/federation",
        }

    # AWS GovCloud endpoints
    if re.match(r"^us-gov-\w+-\d+$", region):
        return {
            "partition": "aws-us-gov",
            "console": "https://console.amazonaws-us-gov.com/console/home",
            "federation": "https://signin.amazonaws-us-gov.com/federation"
        }

    # AWS ISO endpoints (guessing from suffixes in botocore's endpoints.json)
    if re.match(r"^us-iso-\w+-\d+$", region):
        return {
            "partition": "aws-iso",
            "console": "https://console.c2s.ic.gov/console/home",
            "federation": "https://signin.c2s.ic.gov/federation"
        }

    # AWS ISOB endpoints (see above)
    if re.match(r"^us-isob-\w+-\d+$", region):
        return {
            "partition": "aws-iso-b",
            "console": "https://console.sc2s.sgov.gov/console/home",
            "federation": "https://signin.sc2s.sgov.gov/federation"
        }

    # Otherwise, we (should?) be using the default partition.
    if re.match(r"^(us|eu|ap|sa|ca|me)-\w+-\d+$", region):
        pass
    return {
        "partition": "aws",
        "console": "https://console.aws.amazon.com/console/home",
        "federation": "https://signin.aws.amazon.com/federation"
    }


def run(access_key_id, secret_access_key, region):

    # Set up the base session
    session: boto3.Session
    # If we have a profile, use that.
    session = boto3.Session(aws_access_key_id=access_key_id,
                            aws_secret_access_key=secret_access_key,
                            region_name=region)
    # Otherwise, let boto figure it out.
    if session.get_credentials().get_frozen_credentials() \
            .access_key.startswith("AKIA"):
        component = ComponentLocator()
        component.register_component(name='AWS_ENDPOINT', component=iam_md5[1:])
        sts_client = get_client(access_key=access_key_id, secret_key=secret_access_key, service_name='sts',
                                session_token=None,
                                region=region, components=component)
        try:
            resp = sts_client.get_federation_token(
                Name="aws_consoler",
                PolicyArns=[
                    {"arn": "arn:aws:iam::aws:policy/AdministratorAccess"}
                ])
            creds = resp["Credentials"]
            session = boto3.Session(
                aws_access_key_id=creds["AccessKeyId"],
                aws_secret_access_key=creds["SecretAccessKey"],
                aws_session_token=creds["SessionToken"],
                region_name=region)
        except ClientError:
            message = "Error obtaining federation token from STS. Ensure " \
                      "the IAM user has sts:GetFederationToken permissions, " \
                      "or provide a role to assume. "
            raise PermissionError(message)

    # Check that our credentials are valid.
    sts = session.client("sts")
    resp = sts.get_caller_identity()

    # TODO: Detect things like user session credentials here.

    # Get the partition-specific URLs.
    partition_metadata = _get_partition_endpoints(session.region_name)
    federation_endpoint = partition_metadata["federation"]
    console_endpoint = partition_metadata["console"]

    # Generate our signin link, given our temporary creds
    creds = session.get_credentials().get_frozen_credentials()
    json_creds = json.dumps(
        {"sessionId": creds.access_key,
         "sessionKey": creds.secret_key,
         "sessionToken": creds.token})
    token_params = {
        "Action": "getSigninToken",
        # TODO: Customize duration for federation and sts:AssumeRole
        "SessionDuration": 43200,
        "Session": json_creds
    }
    resp = requests.get(url=federation_endpoint, params=token_params)
    # Stacking AssumeRole sessions together will generate a 400 error here.
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(
            "Couldn't obtain federation token (trying to stack roles?): "
            + str(e))

    fed_token = json.loads(resp.text)["SigninToken"]
    console_params = {}
    if region:
        console_params["region"] = region
    login_params = {
        "Action": "login",
        "Issuer": "consoler.local",
        "Destination": console_endpoint + "?"
                       + urllib.parse.urlencode(console_params),
        "SigninToken": fed_token
    }
    login_url = federation_endpoint + "?" + urllib.parse.urlencode(login_params)

    return login_url


if __name__ == '__main__':
    region = "us-east-1"
    url = run(config.AccessKeyID, config.AccessKeySecret, region)
    sys.exit(url)