from socket import *
import os
import sys
import time
import FileHandler
import RawSocketHandler

class TCPFileSender:
    def __init__(self, destination_ip, input_file, mode):
        self.destination_ip = destination_ip
        self.inputFileName = input_file
        self.file = FileHandler(input_file, mode)
        self.file.open()
        self.socket = RawSocketHandler(self.destination_ip, mode)


    def sendData(self):
        self.configure()

        while self.file.dataToSend():
            self.socket.sendData(self.file.readNextData())
            self.waitForAck()

        self.cleanUp()


    def configure(self):
        try:
            self.file.open()
            self.socket.configure()

        except Exception as e:
            print("Error configuring sender!")
            print(str(e))
            sys.exit()

    def cleanup(self):
        self.file.close()
        self.socket.shutdown()
        self.socket.close()