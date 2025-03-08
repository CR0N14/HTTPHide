# HTTPHide: A Reverse Shell using Header Steganography

## Introduction
Reverse shells are commonly used by pentesters to maintain remote control over compromised machines. However, the network traffic they generate can be easily flagged as suspicious, alerting network administrators. 

HTTPHide is a reverse shell that aims to be stealthy and evade detection. It communicates over HTTP/1.x to disguise itself as standard web traffic and uses packet header steganography to render itself undetectable by traditional security measures. 

Packet header steganography is the technique whereby data is stored not in the packet’s payload where it is easily scrutinised but instead hidden in the packet’s headers.

## Design
HTTPHide consists of three Python scripts: client.py, listener.py, and utils.py.

### client.py
- Run this on the compromised target machine.
- A reverse shell that communicates with the listener via HTTP requests.
- Data is hidden in the 'X-Request-ID' HTTP header. The data is AES-128-CFB encrypted, DEFLATE compressed, and Base64 encoded.

### listener.py
- Run this on your C2 server.
- Starts and maintain an HTTP server. Communicates with the client via HTTP responses.
- Data is hidden in the website's favicon image, via image steganography.

### utils.py
- A common module containing constants/functionality that both listener and client require.

### web
- This directory contains the website files for the listener's HTTP server.

### secret_web
- This directory contains the image files used for steganographic communication. 
- 'secret.ico' is stored on the listener, 'client_secret.ico' is a copy stored on the client.

## Usage
1. Run listener.py and client.py
2. client.py will automatically send the first request to the listener (displaying the pwd)
3. Enter your commands into the listener.py

## Development
```
# Activate virtual environment (requires a virtual environment setup).
.venv/scripts/activate

# Install required dependencies.
pip install -r requirements.txt

# Save required dependencies.
pip freeze > requirements.txt
```