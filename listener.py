'''
Executes on the C2 server. Runs an HTTP server that listens for requests from the client.
'''

from http.server import SimpleHTTPRequestHandler, HTTPServer
# from urllib import request, parse
# import base64
from utils import SERVER_IP, SERVER_PORT

'''
CONSTANTS
'''

WEB_DIRECTORY = 'web' # Root directory of website files.

class RequestHandler(SimpleHTTPRequestHandler):
    '''
    Instantiated on each HTTP request to handle the request.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIRECTORY, **kwargs)

    def get_encoded_data(self):
        # Retrieve the encoded data from the HTTP header
        # encoded_data = self.headers.get('X-Stego-Data')
        
        # if encoded_data:
        #     decoded_data = base64.b64decode(encoded_data).decode()
        #     print("Received decoded data:", decoded_data)
        return

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
        self.serve_web_content()

def main():
    server_address = (SERVER_IP, SERVER_PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f'Server running on {SERVER_IP}:{SERVER_PORT}...')
    httpd.serve_forever()

if __name__ == '__main__':
    main()