Misc notes. TODO: delete this on project completion

# TODO
## aaron
- Handle cd DONE
- Handle normal web traffic DONE
- Handle long-running commands, and sending SIGINT
- Client keeps attempting requests even if listener isn't up DONE
- Client: split data across multiple requests so it's not so big
- Encryption (without increasing data size). RC4
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