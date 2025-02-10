import unittest
import socket
import asyncio
import threading
import os
from transmitter import send_file, receive_file, DATA_DIR, BUFFER_SIZE

event_server_started = threading.Event()


class TestFileTransfer(unittest.TestCase):
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5001
    TEST_FILE = "testfile.bin"  # Using a binary file for robust testing
    RECEIVED_FILE = os.path.join(DATA_DIR, "testfile.bin")

    @classmethod
    def setUpClass(cls):
        """Set up the test environment by creating a test file."""
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(cls.TEST_FILE, "wb") as f:
            f.write(os.urandom(BUFFER_SIZE*2))  # Create a random binary file of 1KB

    @classmethod
    def tearDownClass(cls):
        """Clean up test files after tests are done."""
        for file in [cls.TEST_FILE, cls.RECEIVED_FILE]:
            if os.path.exists(file):
                os.remove(file)

    def start_receiver(self):
        """Start the receiver and signal when ready."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.SERVER_HOST, self.SERVER_PORT))
            s.listen(1)
            event_server_started.set()  # Signal that receiver is ready
        receive_file(self.SERVER_HOST, self.SERVER_PORT)

    async def async_test_file_transfer(self):
        """Test sending and receiving a file over a TCP connection asynchronously."""
        # Start receiver in a separate thread
        server_thread = threading.Thread(target=self.start_receiver, daemon=True)
        server_thread.start()

        # Wait for server to be ready
        event_server_started.wait()

        # Send the file asynchronously
        await asyncio.to_thread(send_file, self.TEST_FILE, self.SERVER_HOST, self.SERVER_PORT)

        # Ensure the received file exists
        self.assertTrue(os.path.exists(self.RECEIVED_FILE))

        # Compare contents of original and received file
        with open(self.TEST_FILE, "rb") as f1, open(self.RECEIVED_FILE, "rb") as f2:
            self.assertEqual(f1.read(), f2.read())

    def test_file_transfer(self):
        """Run the async test synchronously."""
        asyncio.run(self.async_test_file_transfer())


if __name__ == "__main__":
    unittest.main()
