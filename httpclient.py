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

from ast import arg
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.hostname
        path = parsed_url.path
        if path == '':
            path = '/'
        port = parsed_url.port
        if port is None:
            port = 80
        query = parsed_url.query
        return host, path, port, query

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return self.socket

    def get_code(self, data):
        return int(data.split()[1])

    def get_headers(self,data):
        split_data = data.split('\r\n\r\n')
        header = split_data[0]
        return header

    def get_body(self, data):
        split_data = data.split('\r\n\r\n')
        body = split_data[1]
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
        code = 0
        body = ""
        host, path, port, query = self.get_host_port(url)

        if query:
            request_body = f"GET {path}?{query} HTTP/1.1\r\nHost:{host}\r\nAccept: */*\r\nConnection: close\r\n\r\n"

        request_body = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nAccept: */*\r\nConnection: close\r\n\r\n"

        self.connect(host,port)
        self.sendall(request_body)

        new_data = self.recvall(self.socket)
        code = self.get_code(new_data)
        body = self.get_body(new_data)
        print(body)
        # print response
        #print(new_data)

        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        host, path, port, query = self.get_host_port(url)

        # get the content length
        args_content = ''
        if args is not None:
            for args_key in args:
                args_content = args_content + args_key
                argument = args[args_key]
                args_content += '=' + argument + '&'
            
            args_content = args_content[:-1]
            args_content_length = len(args_content)
            request_body = f"POST {path} HTTP/1.1\r\nHost:{host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-length:{args_content_length}\r\nConnection: close\r\n\r\n{args_content}"
            #request_body += args_content_length + '\r\n\r\n' + args_content
        elif query is not None:
            request_body = f"POST {path} HTTP/1.1\r\nHost:{host}\r\nContent-Type: application/x-www-form-urlencoded\r\n{query}Content-length:{len(query)}\r\nConnection: close\r\n\r\n"
        else:
            request_body = f"POST {path} HTTP/1.1\r\nHost:{host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-length:0\r\nConnection: close\r\n\r\n"

        self.connect(host,port)
        self.sendall(request_body)

        new_data = self.recvall(self.socket)
        code = self.get_code(new_data)
        body = self.get_body(new_data)
        print(body)
        # print response
        #print(new_data)
        
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
