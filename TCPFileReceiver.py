from socket import *
import os
import sys
import time
import FileHandler
import RawSocketHandler

class TCPFileReceiver:
    def __init__(self, source_ip, output_file, mode):
        self.source_ip = source_ip
        self.inputFileName = output_file
        self.file = FileHandler(output_file, mode)
        self.file.open()
        self.socket = RawSocketHandler(self.source_ip, mode)


    def receiveData(self):
        self.configure()

        while True:
            data = self.socket.receiveData()
            if self.socket.isConnectionClosed():
                break

            self.file.writeData(data)
            self.socket.sendAck()

        print("Done receiving")
        self.cleanUp()


    def configure(self):
        try:
            self.file.open()
            self.socket.configure()

        except Exception as e:
            print("Error configuring receiver!")
            print(str(e))
            sys.exit()


    def cleanUp(self):
        self.file.close()
        self.socket.close()