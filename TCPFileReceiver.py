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
        self.file = FileHandler.FileHandler(output_file, mode)
        self.file.open()
        self.socket = RawSocketHandler.RawSocketHandler(self.source_ip, mode)


    def receiveData(self):
        print("\n\nInside receiveData of TCPFileReceiver")
        self.configure()
        print("Done configuring")

        while True:
            data = self.socket.receiveData()
            print("Data received: \n", data)
            if self.socket.isConnectionClosed():
                print("Closing connection.")
                break

            self.file.writeData(data)
            print("Wrote data to file.")
            self.socket.sendAck()
            print("Sent back ACK.")

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
