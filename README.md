# HTTPHide: A Reverse Shell using Header Steganography

## Introduction
Reverse shells are commonly used by pentesters to maintain remote control over compromised machines. However, the network traffic they generate can be easily flagged as suspicious, alerting network administrators. 

HTTPHide is a reverse shell that aims to be stealthy and evade detection. It communicates over HTTP/1.x to disguise itself as standard web traffic and uses packet header steganography to render itself undetectable by traditional security measures. 

Packet header steganography is the technique whereby data is stored not in the packet’s payload where it is easily scrutinised but instead hidden in the packet’s headers. For HTTP, fields such as Accept, User-Agent and others can be abused for this purpose.

## Design
HTTPHide consists of three Python scripts: listener.py, client.py and utils.py.

### listener.py 
- Starts and maintain an HTTP server. Communicates with the client via HTTP responses.
- Data is hidden in the website logo via image steganography.

### client.py
- A reverse shell that communicates with the listener via HTTP requests.
- Data is hidden in the packet header.

### utils.py
- A common module containing functionality that both listener and client require (i.e. parsing, encoding and sending HTTP packets).

### web
- This directory contains website files for the listener's HTTP server
to give it the appearance of a normal website to browsers.

### secret_web
- This directory contains website files for the listener's HTTP server
that can only be requested from the client, used for steganographic communication.

## Usage
1. Run listener.py first, then client.py
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