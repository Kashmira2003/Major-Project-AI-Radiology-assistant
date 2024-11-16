# import socket

# # Model server setup
# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.bind(('127.0.0.1', 5061))  # Make sure the IP and port match the client
# server.listen(5)
# print("Model server is running on port 5061...")

# while True:
#     client_socket, addr = server.accept()
#     print(f"Connection from {addr}")
#     # Handle prediction logic here (call your model and return results)
#     client_socket.close()


import socket
import pickle  # For serializing the result data
import time

def run_model(image_data):
    # This function processes the received image data and returns the prediction result.
    # Replace this with your actual model code
    print("Running model...")
    time.sleep(2)  # Simulate model processing time
    result = ["Disease: Fracture", "Disease: Pneumothorax"]
    return result  # Return the predicted results (modify according to your model)

def bytes_to_number(b):
    """Converts a byte array to a number."""
    res = 0
    for i in range(4):
        res += b[i] << (i * 8)
    return res

def start_model_server():
    """Starts the model server that listens for incoming connections."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 5061))  # Bind to the correct address and port
        s.listen(5)
        print("Model server listening on port 5061...")

        while True:
            conn, addr = s.accept()  # Accept a new client connection
            with conn:
                print(f"Connected by {addr}")
                # Receive the image length (4 bytes) and then the image data
                length = conn.recv(4)
                file_size = bytes_to_number(length)
                data = conn.recv(file_size)

                # Process the image data (in this example, we simply simulate it)
                result = run_model(data)  # Replace this with your actual model function

                # Serialize the result data to send back to the client (Flask app)
                result_data = pickle.dumps(result)
                conn.sendall(result_data)  # Send the result to the client

if __name__ == '__main__':
    start_model_server()  # Start the model server

