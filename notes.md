Misc notes. TODO: delete this on project completion


# TODO
## main
- Client: send request with fields expected of by a browser
- Hide request flags DONE
- Encryption (without increasing data size). AES in CFB mode DONE
- Stretch:
    - Handle long-running commands, and sending SIGINT
    - Test on live webserver
## others
- client: get_random_url() DONE 
- server: very basic html pages
- server: image steganoraphy
- testing with IDS


# Steganography (hide data where)
Request (from client)
- Custom header with compressed b64 data
Response (from listener)
- Website icon image steganography


# Sending message
1. Encrypt
2. Compress
3. b64 encode
4. Split
5. Append flags

# Receiving message
1. Get request data
2. Combine
3. b64 decode
4. Uncompress
5. Unencrypt