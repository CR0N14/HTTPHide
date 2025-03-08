'''
Contains common functionalities required by both the client and listener scripts.
'''

from enum import IntFlag, auto

'''
CONSTANTS
'''
LISTENER_IP = '127.0.0.1'
LISTENER_PORT = 80
# The name of the HTTP header to hide data in
# 'X-Request-ID' is an optional and unofficial header used by some web servers for logging purposes.
STEGO_HEADER_NAME = 'X-Request-ID'
# Fake user agent (pretend to be a browser)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
# The max no. of chars a message from the client can be (after compression) for one request.
# If exceed, the message will be split into multiple requests.
CLIENT_MAX_MESSAGE_LENGTH = 200
# To keep things simple, key and iv are constants for now.
AES_KEY = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10'  # 16 bytes for AES-128
AES_IV = b'\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa\xbb\xcc\xdd\xee\xff'  # 16 bytes IV for CFB mode

class RequestFlags(IntFlag):
    IS_NOT_COMPRESSED = auto()
    IS_END_OF_MESSAGE = auto()

    def get_flags_char(self):
        if RequestFlags.IS_NOT_COMPRESSED in self and RequestFlags.IS_END_OF_MESSAGE in self:
            return "y"
        elif RequestFlags.IS_NOT_COMPRESSED in self:
            return "g"
        elif RequestFlags.IS_END_OF_MESSAGE in self:
            return "v"
        else:
            return "k"
    
    @staticmethod
    def get_flags_from_char(char):
        if char == "y":
            return RequestFlags.IS_NOT_COMPRESSED | RequestFlags.IS_END_OF_MESSAGE
        elif char == "g":
            return RequestFlags.IS_NOT_COMPRESSED
        elif char == "v":
            return RequestFlags.IS_END_OF_MESSAGE
        else:
            return RequestFlags(0)

