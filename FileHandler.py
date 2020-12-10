import os
import sys

class FileHandler:
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

    def open(self):
        if self.mode == 'send':
            if os.path.exists(self.filename):

                self.fsize = os.stat(self.filename).st_size
                self.totalCount = self.fsize // self.chunkSize

                if self.fsize % self.chunkSize == 0:
                    self.isLastPacketEmpty = True
                else:
                    self.lastChunkSize = self.fsize - (self.totalCount * self.chunkSize)
                    self.totalCount += 1

                try:
                    self.fd = open(self.filename, mode='r+b')
                except OSError as e:
                    print("Could not open/read file:", self.filename)
                    print(str(e))
                    sys.exit()
            else:
                print(self.filename, " : File does not exist.")
                sys.exit()

        elif self.mode == 'receive':
            try:
                self.fd = open(self.filename, mode='r+b')
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
            isLastChunk = False
        else:   # self.currentCount == self.totalCount
            data = bytearray(self.fd.read(self.lastChunkSize))
            isLastChunk = True

        self.offset += self.chunkSize

        return (data, isLastChunk)

    def writeData(self, data):
        self.fd.seek(self.offset)
        self.fd.write(data)
        self.offset += sys.getsizeof(data)
