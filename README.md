# Computer Networks Project
# File Transfer Using TCP/IP Protocol Implementation with Raw Sockets

Reference Link: https://www.binarytides.com/raw-socket-programming-in-python-linux/https://medium.com/@yoursproductly/tcp-vs-udp-38b10bb1bbf3

# Why use TCP ?
TCP i s a highly efficient and reliable protocol designed for end-to-end transmission
over an unreliable network. It i s connection-oriented and provides error checking and
recovery mechanisms for data transfer. Transferring a file over TCP will also guarantee
in-order delivery of data packets.

# Overview
This project i s an application to transfer data files between network connected hosts.
The core functionality of the application i .e. data transfer will be i mplemented using Unix raw
sockets. The application would build each packet to be sent using the data and building the
TCP and IP headers. The application running on the receiving host needs to run an i nstance
of the application. At receiver, the application would accept the data packets, extract the
TCP and IP headers and then process the data packet as needed.

# Inputs
The application would accept the file to be transferred and IP of the host as i nputs.
The application program needs to be deployed and running on both the sender and receiver
of the data.

# Execution Modes
The file transfer application could be run i n two modes: Sender and Receiver.
## Sender:
- In Sender mode, the application will need the name of the file to be transferred as
well as the IP address of the Receiver host.
- The application will use the Unix raw sockets to connect with the receiver by doing
the TCP handshake.
- Once the TCP connection i s established, the Sender will read the data file i n fixed
size chunks and each chunk will be sent as an i ndependent packet.
- The application will wrap the data bits with TCP and IP header generated.
- For each packet to be sent, the Sender will calculate the checksum to be added to
the TCP header and i t will be sent as part of the packet.
- The Sender would then wait for an acknowledgement from the Receiver.
- Once an acknowledgement for the sent packet i s received, the application would
continue with the next packet and so on.
- The application will close the TCP connection by sending a FIN packet after all of the
data read from the file i s transferred and end the application.

## Receiver:
- In Receiver mode, the application will need the name of the output file to write data to
as well as the IP address of the Sender host.
- The application will use the Unix raw sockets to communicate with the Sender
application and wait for the Sender to establish the connection with TCP handshake.
- Once the TCP connection i s established, the Receiver would start accepting the data
packets.
- As the data packet i s received, the Receiver application would extract the TCP and
IP headers.
- The Receiver would then verify the i ntegrity of the data packet using checksum i n the
TCP header.
- If all the bits i n the packet are correct, then the Receiver would write the data bits to
the output file provided as i nput.
- The Receiver would send an acknowledgement back to the Sender application for
each data packet written to the file.
- The Receiver would wrap the acknowledgement with TCP and IP header generated.
- For each acknowledgement packet to be sent, the Receiver will calculate the
checksum to be added to the TCP header and i t will be sent as part of the packet.
- The Receiver would then wait for the next data packet from the Sender.
- Once an acknowledgement i s sent, the Receiver would continue with the next packet
and so on.
- When a FIN packet i s received, the Receiver would close the output file and close
the connection.
