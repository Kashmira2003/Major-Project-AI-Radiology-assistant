 # If there is an error, it will print the error message


import socket

host = '127.0.0.1'  # Localhost IP
port = 5061          # Port the model server is running on

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(10)  # Optional: Set timeout to wait for server response
        s.connect((host, port))  # Try connecting to model server
        print("Connection to model server successful!")
except Exception as e:
    print(f"Error: {e}")  # Error if unable to connect
