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
# The max no. of chars a message from the client can be (after compression) for one request.
# If exceed, the message will be split into multiple requests.
CLIENT_MAX_MESSAGE_LENGTH = 200

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