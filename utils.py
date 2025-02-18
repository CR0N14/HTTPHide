'''
Contains common functionalities required by both the client and listener scripts.
'''

'''
CONSTANTS
'''
LISTENER_IP = '127.0.0.1'
LISTENER_PORT = 80
# The name of the HTTP header to hide data in
# 'X-Request-ID' is an optional and unofficial header used by some web servers for logging purposes.
STEGO_HEADER_NAME = 'X-Request-ID'