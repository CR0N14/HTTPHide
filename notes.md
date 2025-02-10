Misc notes. TODO: delete this on project completion

# TODO
## aaron
- Handle cd
- Ensure that client connection is uniquely identified (random requests wont throw off two-way connection)
- Handle CTRL+C
- Client: what happens if listener isn't up
- Client: split data across multiple requests so it's not so big
- Encryption (without increasing data size). RC4
## others
- client: get_random_url() and server: basic webpages
- server: image steganoraphy
- testing with IDS


# Steganography (hide data where)
Request (from client)
- Custom header with compressed b64 data
Response (from listener)
- Website icon image steganography