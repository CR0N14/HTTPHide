# HTTPHide: A Reverse Shell using Header Steganography

## Development
```
# Activate virtual environment (requires a virtual environment setup).
.venv/scripts/activate

# Install required dependencies.
pip install -r requirements.txt

# Save required dependencies.
pip freeze > requirements.txt
```

## Usage
TODO

## Introduction
Reverse shells are commonly used by pentesters to maintain remote control over compromised machines. However, the network traffic they generate can be easily flagged as suspicious, alerting network administrators. 

HTTPHide is a reverse shell that aims to be stealthy and evade detection. It communicates over HTTP/1.x to disguise itself as standard web traffic and uses packet header steganography to render itself undetectable by traditional security measures. 

Packet header steganography is the technique whereby data is stored not in the packet’s payload where it is easily scrutinised but instead hidden in the packet’s headers. For HTTP, fields such as Accept, User-Agent and others can be abused for this purpose.

## Design
HTTPHide consists of three components: listener.py, client.py and utils.py. 

The listener starts and maintain an HTTP server, while the client spawns a reverse shell that communicates with the listener via HTTP packets. Meanwhile, utils.py is a common module containing functionality that both scripts require (i.e. parsing, encoding and sending HTTP packets). 

## Libraries Used (NOT FINALISED)
socket: low-level networking for establishing connection
requests: handle HTTP request and responses
http.server: setup HTTP server
urllib: URL parsing/encoding
base64: base64 encoding
zlib: data compression