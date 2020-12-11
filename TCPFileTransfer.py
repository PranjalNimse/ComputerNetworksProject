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
        sender = TCPFileSender.TCPFileSender(ip_address, filename, mode)
        print("Starting to send data.")
        sender.sendData()
    elif mode == 'receive':
        receiver = TCPFileReceiver.TCPFileReceiver(ip_address, filename, mode)
        print("Ready to receive data.")
        receiver.receiveData()
    else:
        print("Specify mode : [send, receive]")
        sys.exit()

main()