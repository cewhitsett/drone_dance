# Code adapted from https://github.com/dji-sdk/Tello-Python/tree/master/Single_Tello_Test

import socket
import threading
import time

class Tello:
    def __init__(self):
        self.local_ip = ''
        self.local_port = 8889
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        self.socket.bind((self.local_ip, self.local_port))

        # thread for receiving cmd ack
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        self.tello_ip = '192.168.10.1'
        self.tello_port = 8889
        self.tello_adderss = (self.tello_ip, self.tello_port)

    def send_command(self, command):
        """
        Send a command to the ip address. Usually will wait until it receives
        an okay from drone, but that functionality was removed for now.
        :param command: (str) the command to send
        :param ip: (str) the ip of Tello
        """

        self.socket.sendto(command.encode('utf-8'), self.tello_adderss)

    def _receive_thread(self):
        """Listen to responses from the Tello.

        Runs as a thread, sets self.response to whatever the Tello last returned.
        """
        pass

    def on_close(self):
        for ip in self.tello_ip_list:
            self.socket.sendto('land'.encode('utf-8'), (ip, 8889))
        self.socket.close()

