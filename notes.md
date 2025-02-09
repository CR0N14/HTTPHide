Misc notes. TODO: delete this on project completion

# TODO
- Handle cd
- Ensure that client connection is uniquely identified (random requests wont throw off two-way connection)
- Handle CTRL+C
- Client: what happens if listener isn't up
- Client: split data across multiple requests so it's not so big
- Encryption (without increasing data size). RC4
## Others
- client: get_random_url() and server: basic webpages
- server: image steganoraphy
- testing with IDS

# steganography
- different steganography methods can be enabled/disabled?

Hide data where?
- image steganography (website icon)
- custom header
- custom MIME type

# misc ideas
- STRETCH: listener serves as proxy webserver to actual website? less suspicious

# Useful Resources
https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/
- pty python module is good, but only for Linux

## Libraries Used (NOT FINALISED)
socket: low-level networking for establishing connection
requests: handle HTTP request and responses
http.server: setup HTTP server
urllib: URL parsing/encoding
base64: base64 encoding
zlib: data compression