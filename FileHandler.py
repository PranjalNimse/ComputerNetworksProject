import os
import sys
import TCPFileTransfer
import TCPFileReceiver
import TCPFileSender
import RawSocketHandler


class FileHandler:

    # receive 4096 bytes each time
    BUFFER_SIZE = 4096
    SEPARATOR = "<SEPARATOR>"

    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.fd = None
        self.fsize = 0
        self.offset = 0
        self.totalCount = 0
        self.currentCount = 0
        self.chunkSize = 512
        self.isLastPacketEmpty = False
        self.lastChunkSize = 0
        self.sender = None
        self.receiver = None
        self.BUFFER_SIZE = 4096
        self.SEPARATOR = "<SEPARATOR>"
        self.client_socket = None

    def open(self):
        if self.mode == 'send':
            if os.path.exists(self.filename):

                self.fsize = os.stat(self.filename).st_size
                self.totalCount = self.fsize // self.chunkSize

                if self.fsize % self.chunkSize == 0:
                    self.isLastPacketEmpty = True
                else:
                    self.lastChunkSize = self.fsize - \
                        (self.totalCount * self.chunkSize)
                    self.totalCount += 1

                try:
                    self.fd = open(self.filename, mode='rb')
                except OSError as e:
                    print("Could not open/read file:", self.filename)
                    print(str(e))
                    sys.exit()
            else:
                print(self.filename, " : File does not exist.")
                sys.exit()

        elif self.mode == 'receive':
            try:
                self.fd = open(self.filename, 'wb+')
            except OSError as e:
                print("Could not create file:", self.filename)
                print(str(e))
                sys.exit()

    def close(self):
        if self.fd:
            self.fd.close()

    def dataToSend(self):
        return self.currentCount <= self.totalCount

    def readNextData(self):
        self.currentCount += 1
        self.fd.seek(self.offset)
        if self.currentCount < self.totalCount:
            data = bytearray(self.fd.read(self.chunkSize))
        else:   # self.currentCount == self.totalCount
            data = bytearray(self.fd.read(self.lastChunkSize))

        self.offset += self.chunkSize

        return data

    def writeData(self):

        mode, ip_address, filename = TCPFileTransfer.parseArgs(sys.argv)

        if mode == 'send':
            self.sender = TCPFileSender(ip_address, filename)
            self.client_socket = self.sender.socket

        elif mode == 'receive':
            self.receiver = TCPFileReceiver(ip_address, filename)
            self.client_socket = self.receiver.socket

        else:
            print(f"Un-Supported mode: {mode}")
            sys.exit()

        with open(filename, "wb") as f:
            bytes_read = self.client_socket.recv(self.BUFFER_SIZE)

            if not bytes_read:
                # nothing is received
                # file transmitting is done
                pass
            # write to the file the bytes we just received
            f.write(bytes_read)

        self.client_socket.close()
