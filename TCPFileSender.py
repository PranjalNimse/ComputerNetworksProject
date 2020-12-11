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
        self.file = FileHandler.FileHandler(input_file, mode)
        self.socket = RawSocketHandler.RawSocketHandler(self.destination_ip, mode)


    def sendData(self):
        print("\n\nInside sendData of TCPFileSender")
        self.configure()
        print("Done configuring")

        while self.file.dataToSend():
            print("More data to send")
            self.socket.sendData(self.file.readNextData())
            print("Data sent")
            self.socket.waitForAck()
            print("ACK received.")

        print("Cleaning up before closing the application.")
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
        self.socket.close()