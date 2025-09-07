#!/usr/bin/env python3
"""
Simple test server that mimics the Hatagawa service for testing
"""

import socket
import threading
import time

def handle_client(client_socket):
    """Handle a client connection"""
    try:
        # Send initial greeting
        greeting = """
|  Menu:
|    [S]tay a while...
|    [W]alk away
|
|  > """
        client_socket.send(greeting.encode())
        
        while True:
            # Receive command
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                    
                command = data.decode().strip().lower()
                
                if command == 's':
                    # Send flag response with hex
                    flag_response = """
|  [~] Look! Is that a flag floating by?
|   ~~~ 320af2e7ceeea34cfeae586183f96deecb6f999ce53ce37bec ~
|
|  Menu:
|    [S]tay a while...
|    [W]alk away
|
|  > """
                    client_socket.send(flag_response.encode())
                    
                elif command == 'w':
                    client_socket.send(b"|  [~] You turn your back to the river...\n")
                    break
                else:
                    client_socket.send(b"|  [!] Invalid choice.\n|  > ")
                    
            except socket.timeout:
                break
            except Exception as e:
                print(f"Error handling client: {e}")
                break
    
    except Exception as e:
        print(f"Client handler error: {e}")
    finally:
        client_socket.close()

def start_test_server(port=9999):
    """Start the test server"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('localhost', port))
        server_socket.listen(5)
        print(f"Test server started on port {port}")
        
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Client connected from {addr}")
            
            # Handle client in a new thread
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
            
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_test_server()