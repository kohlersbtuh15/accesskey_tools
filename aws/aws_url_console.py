from aws_consoler.cli import main
import config

#import socket, socks
#default_socket = socket.socket
#socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_PROXY_HOST, config.SOCKS5_PROXY_PORT)
#socket.socket = socks.socksocket

if __name__ == '__main__':
    region = "us-east-1"
    main(["-a", config.AccessKeyID, "-s", config.AccessKeySecret, "-R", region])