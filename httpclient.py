#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
from urllib.parse import urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        hostname = urllib.parse.urlparse(url).hostname
        port = urllib.parse.urlparse(url).port
        if port == None:
            port = 80
        path = urllib.parse.urlparse(url).path
        if path == '':
            path = "/"
        return hostname, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        data_list = data.split(' ')
        str_code = data_list[1]
        int_code = int(str_code)
        return int_code

    def get_headers(self,data):
        data_list = data.split('\r\n\r\n')
        headers = data_list[0]
        return headers

    def get_body(self, data):
        data_list = data.split("\r\n\r\n")
        body = data_list[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host,port,path = self.get_host_port(url)
        self.connect(host,port)
        agent =  "User-Agent: curl/7.64.1\r\n"
        accept = "Accept: */*\r\n"
        status_code = "GET {} HTTP/1.1\r\n".format(path)
        host_n = "Host: {}\r\n".format(host)
        connection = "Connection: close\r\n\r\n"
        payload = status_code + agent + host_n + accept + connection
        self.sendall(payload)
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host,port,path = self.get_host_port(url)
        self.connect(host, port)
        agent =  "User-Agent: curl/7.64.1\r\n"
        status_code = "POST {} HTTP/1.1\r\n".format(path)
        host_n = "Host: {}\r\n".format(host)
        connection = "Connection: close\r\n\r\n"
        content_type="Content-Type: application/x-www-form-urlencoded\r\n"
        if args != None:
            parameters = urllib.parse.urlencode(args)
            content_length = "Content-Length: {}\r\n".format(str(len(parameters)))
        else:
            parameters = ''
            content_length="Content-Length:{}\r\n".format(str(0))
            
        payload = status_code + agent + host_n + content_type + content_length + connection + parameters
        self.sendall(payload)
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()



        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
