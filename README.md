# File Transfer Utility

This project implements a simple file transfer utility using Python's built-in socket library. It supports sending and receiving files over a TCP connection.

## Features
- Send files over a network using TCP sockets.
- Receive files and store them in a designated data directory.
- Uses buffered file transfer to handle large files efficiently.
- Includes unit tests to verify correct transmission and reception.

## Requirements
- Python 3.x

## Usage

### Receiving a File
To receive a file, run:
```sh
python transmitter.py recv <ip> <port>
```
Example:
```sh
python transmitter.py recv 127.0.0.1 5001
```

### Sending a File
To send a file, run:
```sh
python transmitter.py send <filename> <ip> <port>
```
Example:
```sh
python transmitter.py send example.txt 127.0.0.1 5001
```

## Running Tests
Unit tests are included in `test_transmitter.py`. To run them, use:
```sh
python test.py
```

## File Structure
```
.
├── transmitter.py        # Main script for sending/receiving files
├── test_.py   # Unit tests for file transfer
├── data/                 # Directory where received files are stored
├── README.md             # Project documentation
```
