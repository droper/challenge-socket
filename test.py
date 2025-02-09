import unittest
import socket
import asyncio
import threading
import os
from transmitter import send_file, receive_file, DATA_DIR

event_server_started = threading.Event()
event_send_completed = threading.Event()


class TestFileTransfer(unittest.TestCase):
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5001
    TEST_FILE = "testfile.txt"
    RECEIVED_FILE = os.path.join(DATA_DIR, "testfile.txt")

    @classmethod
    def setUpClass(cls):
        """Set up the test environment by creating a test file."""
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(cls.TEST_FILE, "w") as f:
            f.write("This is a test file for transmission.")

    @classmethod
    def tearDownClass(cls):
        """Clean up test files after tests are done."""
        if os.path.exists(cls.TEST_FILE):
            os.remove(cls.TEST_FILE)
        if os.path.exists(cls.RECEIVED_FILE):
            os.remove(cls.RECEIVED_FILE)

    def start_receiver(self):
        """Start the receiver and signal when ready."""
        event_server_started.set()
        receive_file(self.SERVER_HOST, self.SERVER_PORT)

    async def async_test_file_transfer(self):
        """Test sending and receiving a file over a TCP connection asynchronously."""
        # Start receiver in a separate thread
        server_thread = threading.Thread(target=self.start_receiver, daemon=True)
        server_thread.start()

        # Wait for server to be ready
        event_server_started.wait()

        # Send the file
        await asyncio.to_thread(send_file, self.TEST_FILE, self.SERVER_HOST, self.SERVER_PORT)
        event_send_completed.set()

        # Wait for file transfer completion
        event_send_completed.wait()

        # Check if the received file exists
        self.assertTrue(os.path.exists(self.RECEIVED_FILE))

        # Compare contents of original and received file
        with open(self.TEST_FILE, "r") as f1, open(self.RECEIVED_FILE, "r") as f2:
            self.assertEqual(f1.read(), f2.read())

    def test_file_transfer(self):
        """Run the async test synchronously."""
        asyncio.run(self.async_test_file_transfer())


if __name__ == "__main__":
    unittest.main()
