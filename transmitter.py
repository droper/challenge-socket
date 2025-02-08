# transmitter.py
"""
This script implements a TCP file sender and receiver.
It can either send a file to a specified receiver or listen for incoming file transfers.

Usage:
    python transmitter.py send <filename> <ip> <port>
    python transmitter.py recv <ip> <port>
"""

import socket
import os
import argparse
import logging


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BUFFER_SIZE = 4096  # Size of each data chunk
SEPARATOR = "<SEPARATOR>"  # Separator for filename and filesize


def send_file(filename, host, port):
    """
    Sends a file over a TCP connection to the specified host and port.

    Args:
        filename (str): Path of the file to be sent.
        host (str): Destination IP address.
        port (int): Destination port number.
    """
    filesize = os.path.getsize(filename)  # Get file size in bytes

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))  # Establish connection to receiver

        logging.info(f"Sending {filename} ({filesize} bytes) to {host}:{port}...")

        # Send filename and filesize metadata
        s.send(f"{os.path.basename(filename)}{SEPARATOR}{filesize}".encode())
        s.recv(1)

        # Open and send the file in chunks
        with open(filename, "rb") as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                s.sendall(chunk)

        logging.info("File sent successfully.")


def receive_file(host, port):
    """
    Receives a file over a TCP connection.

    Args:
        host (str): IP address to listen on.
        port (int): Port number to listen on.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)

        logging.info(f"Listening on {host}:{port}...")
        conn, addr = s.accept()

        with conn:
            logging.info(f"Connection from {addr}")
            metadata_bytes = b""
            while SEPARATOR.encode() not in metadata_bytes:
                metadata_bytes += conn.recv(BUFFER_SIZE)
            received = metadata_bytes.decode()
            conn.send(b'1')
            filename, filesize = received.split(SEPARATOR, 1)
            filename = os.path.basename(filename)
            filesize = int(filesize)

            logging.info(f"Receiving {filename} ({filesize} bytes)...")

            with open(filename+"_", "wb") as f:
                received_size = 0
                while received_size < filesize:
                    chunk = conn.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    received_size += len(chunk)

            logging.info("File received successfully.")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="TCP File Transmitter")
    parser.add_argument("command", choices=["send", "recv"],
                        help="Specify 'send' to send a file or 'recv' to receive a file")
    parser.add_argument("filename", nargs="?", help="Filename to send (required for send mode)")
    parser.add_argument("host", help="Target IP address (send mode) or IP to listen on (recv mode)")
    parser.add_argument("port", type=int, help="Port number")

    args = parser.parse_args()

    if args.command == "send":
        if not args.filename:
            parser.error("The 'send' command requires a filename")
        send_file(args.filename, args.host, args.port)
    elif args.command == "recv":
        receive_file(args.host, args.port)
