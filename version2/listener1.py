import socket
import time

def connect_to_cdc_stream(host='127.0.0.1', port=4001):
    count = 0
    while count < 10:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                print("Connected to MaxScale CDC at {}:{}".format(host, port))
                while True:
                    data = s.recv(1024)
                    if not data:
                        print("No data received. count:",count)
                        count+=1
                        break  # Reconnect if connection is broken
                    # Process the data here
                    print(data)
                    # Process and print out the CDC data here
                    hex_data = data.hex()
                    print(f"Received (hex): {hex_data}")
                    try:
                        str_data = data.decode('utf-8')
                        print(f"Received (str): {str_data}")
                    except UnicodeDecodeError:
                        print("Data received is not a valid UTF-8 string")
                    count += 1
                    if count > 10: break
                    time.sleep(1)
        except socket.error as e:
            print(f"Socket error: {e}")
            time.sleep(5)  # Wait before trying to reconnect
        except Exception as e:
            print(f"Error: {e}")
            break  # Exit the loop if an unexpected error occurs
        time.sleep(1)  # Wait before trying to reconnect

if __name__ == '__main__':
    connect_to_cdc_stream()

# def connect_to_cdc_stream(host='127.0.0.1', port=4001):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         print(f"Attempting to connect to MaxScale CDC at {host}:{port}")
#         s.connect((host, port))  # Connect to the server
#         print(f"Connected to MaxScale CDC at {host}:{port}")
#         count = 0
#         while True:
#             data = s.recv(1024)  # Receive data from MaxScale
#             if not data:
#                 print("No more data received.")
#             # Process and print out the CDC data here
#             hex_data = data.hex()
#             print(f"Received (hex): {hex_data}")
#             try:
#                 str_data = data.decode('utf-8')
#                 print(f"Received (str): {str_data}")
#             except UnicodeDecodeError:
#                 print("Data received is not a valid UTF-8 string")
#             count += 1
#             if count > 10: break
#             time.sleep(1)
# if __name__ == '__main__':
#     connect_to_cdc_stream()
