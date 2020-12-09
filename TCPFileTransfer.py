import sys
import TCPFileSender
import TCPFileReceiver

def parseArgs(arguments):
    mode = arguments[1]
    ip_address = arguments[2]
    filename = arguments[3]
    return mode, ip_address, filename

def main():
    mode, ip_address, filename = parseArgs(sys.argv)

    if mode == 'send':
        sender = TCPFileSender(ip_address, filename)
        sender.sendData()
    elif mode == 'receive':
        receiver = TCPFileReceiver(ip_address, filename)
        receiver.receiveData()
    else:
        print("Specify mode : [send, receive]")
        sys.exit()

main()