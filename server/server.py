#!/usr/bin/env python3

from http.server import *
from threading import *
import functools
from os.path import expanduser

SERVER_IP = ("",80)
SERVER_DIR = expanduser(".")

class no_cache_handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_my_headers()
        SimpleHTTPRequestHandler.end_headers(self)

    def send_my_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")

def new_server(server_ip, server_dir):
    handler=functools.partial(no_cache_handler, directory=server_dir)
    server=ThreadingHTTPServer(server_ip,handler)
    server.serve_forever()

print("Local http server")
print("=================")
print(f" - {SERVER_IP}")

Thread(target=new_server, args=[SERVER_IP, SERVER_DIR]).start()
