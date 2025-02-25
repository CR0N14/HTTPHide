Misc notes. TODO: delete this on project completion

# TODO
## aaron
- Handle cd DONE
- Handle normal web traffic DONE
- Client keeps attempting requests even if listener isn't up DONE
- Client: split data across multiple requests so it's not so big
- Client: send request with fields expected of by a browser
- Client: send uncompressed if smaller
- Handle long-running commands, and sending SIGINT
- Encryption (without increasing data size). AES in CFB mode
    - Symmetric encryption
    - You need a stream cipher, not a block cipher
- Test on live webserver
## others
- client: get_random_url() and server: basic webpages
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
3. Split
4. Append flags
5. b64 encode
# Receiving message
1. b64 decode
2. get request bytes
3. combine
4. decompress
5. unencrypt


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