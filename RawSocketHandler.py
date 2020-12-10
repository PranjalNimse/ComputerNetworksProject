import sys
import socket
import signal
import ip, tcp

class RawSocketHandler:
    def __init__(self, destination_ip, mode):
        self.socket = None
        self.destinationIp = destination_ip
        self.sourceIp = None
        self.mode = mode
        self.port_8080 = 8080
        self.port_8081 = 8081
        self.sourcePort = None
        self.destinationPort = None
        self.data = None
        self.packet = None
        self.header = None
        self.ipHeader = None
        self.tcpHeader = None
        self.sequenceNum = -1
        self.ackSeqNum = -1
        self.response = None


    def extractHeader(self):
        return
    def extractData(self):
        return
    def calculateChecksum(self):
        return
    def verifyPacket(self):
        return

    def configure(self):
        try:
            self.sourceIp =  socket.gethostbyname(socket.gethostname())
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)

            if self.mode == 'send':
                self.destinationPort = self.port_8081
                self.sourcePort = self.port_8080
            elif self.mode == 'receive':
                self.destinationPort = self.port_8080
                self.sourcePort = self.port_8081

            self.connectToTarget()

        except socket.error as msg:
            print('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

    def sendAck(self, sequence, acknowledgement, pkt_type):
        ip_header = ip.construct_ip_header(self.sourceIp, self.destinationIp)
        tcp_header = tcp.construct_tcp_header(self.sourceIp, self.destinationIp, self.sourcePort,
                                              sequence, acknowledgement, pkt_type, '',
                                              4000)
        packet = ip_header + tcp_header
        self.socket.sendto(packet, (self.destinationIp, self.destinationPort))


    def close(self):
        if self.socket:
            self.socket.close()


    # checksum functions needed for calculation checksum
    def checksum(self, msg):
        s = 0

        # loop taking 2 characters at a time
        for i in range(0, len(msg), 2):
            w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
            s = s + w

        s = (s>>16) + (s & 0xffff);
        s = s + (s >> 16);

        #complement and mask to 4 byte short
        s = ~s & 0xffff

        return s

    def createIPHeader(self):
        # ip header fields
        ip_ihl = 5
        ip_ver = 4
        ip_tos = 0
        ip_tot_len = 0  # kernel will fill the correct total length
        ip_id = 54321  # Id of this packet
        ip_frag_off = 0
        ip_ttl = 255
        ip_proto = socket.IPPROTO_TCP
        ip_check = 0  # kernel will fill the correct checksum
        ip_saddr = socket.inet_aton(self.sourceIp)  # Spoof the source ip address if you want to
        ip_daddr = socket.inet_aton(self.destinationIp)

        ip_ihl_ver = (ip_ver << 4) + ip_ihl

        # the ! in the pack format string means network order
        ip_header = pack('!BBHHHBBH4s4s', ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto,
                         ip_check, ip_saddr, ip_daddr)
        return


    def createTCPHeader(self):
        # tcp header fields
        tcp_source = 1234  # source port
        tcp_dest = 80  # destination port
        tcp_seq = 454
        tcp_ack_seq = 0
        tcp_doff = 5  # 4 bit field, size of tcp header, 5 * 4 = 20 bytes
        # tcp flags
        tcp_fin = 0
        tcp_syn = 1
        tcp_rst = 0
        tcp_psh = 0
        tcp_ack = 0
        tcp_urg = 0
        tcp_window = socket.htons(5840)  # maximum allowed window size
        tcp_check = 0
        tcp_urg_ptr = 0

        tcp_offset_res = (tcp_doff << 4) + 0
        tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)

        # the ! in the pack format string means network order
        tcp_header = pack('!HHLLBBHHH', tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,
                          tcp_window, tcp_check, tcp_urg_ptr)
        return


    def createHeaders(self):
        self.createIPHeader()
        self.createTCPHeader()

        self.header = self.ipHeader + self.tcpHeader


    def createPacket(self):
        # Packet Header is ready
        # Recalculate the checksum with Data

        # pseudo header fields
        sourceAddress = socket.inet_aton(self.sourceIp)
        destAddress = socket.inet_aton(self.destinationIp)
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        tcpLength = len(self.tcpHeader) + len(self.data)

        pseudoHeader = pack('!4s4sBBH', sourceAddress, destAddress, placeholder, protocol, tcpLength);
        pseudoHeader = pseudoHeader + self.tcpHeader + self.data;

        tcpCheck = self.checksum(pseudoHeader)
        # print tcp_checksum

        # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
        self.tcpHeader = pack('!HHLLBBH', self.sourceIp, self.destinationIp, self.sequenceNum, self.ackSeqNum, tcp_offset_res, tcp_flags,
                          tcp_window) + pack('H', tcpCheck) + pack('!H', tcp_urg_ptr)

        # final full packet - syn packets dont have any data
        self.packet = self.ipHeader + self.tcpHeader + self.data

        return


    def reset(self):
        self.data = None
        self.packet = None
        self.header = None
        self.ipHeader = None
        self.tcpHeader = None
        self.response = None
        return


    def sendData(self, data):
        try:
            self.data = data

            self.createHeaders()
            self.createPacket()

            self.socket.sendto(self.packet, (self.destinationIp, self.destinationPort))

            self.reset()
        except Exception as msg:
            print("Error sending data to destination: ", str(msg))
        return


    def signalHandler(self, signum, frame):
        raise Exception("Timed out!")


    def verifyPacket(self):
        return


    def decryptPacket(self):
        # packet string from tuple
        self.packet = self.packet[0]
        # take first 20 characters for the ip header
        self.ipHeader = self.packet[0:20]
        # now unpack them
        iph = unpack('!BBHHHBBH4s4s', self.ipHeader)
        version_ihl = iph[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0xF
        iph_length = ihl * 4
        ttl = iph[5]
        protocol = iph[6]
        s_addr = socket.inet_ntoa(iph[8]);
        d_addr = socket.inet_ntoa(iph[9]);
        # ip checksum to verify it
        ip.checksum(self.ipHeader)

        # print 'Version : ' + str(version) + ' IP Header Length : ' + str(ihl) + ' TTL : ' + str(ttl) + ' Protocol : ' + str(protocol) + ' Source Address : ' + str(s_addr) + ' Destination Address : ' + str(d_addr)
        # take the next 20 characters for tcp header
        tcp_header = self.packet[iph_length:iph_length + 20]
        # now unpack them
        tcph = unpack('!HHLLBBHHH', tcp_header)
        source_port = tcph[0]
        dest_port = tcph[1]
        sequence = tcph[2]
        acknowledgement = tcph[3]
        doff_reserved = tcph[4]
        tcph_length = doff_reserved >> 4
        # print 'Source Port : ' + str(source_port) + ' Dest Port : ' + str(dest_port) + ' Sequence Number : ' + str(sequence) + ' Acknowledgement : ' + str(acknowledgement) + ' TCP header length : ' + str(tcph_length)
        h_size = iph_length + tcph_length * 4
        data_size = len(self.packet) - h_size
        # get data from the packet
        data = self.packet[h_size:]

        # for verifying tcp checksum
        # constructing the pseudo header
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        pseudo_header = pack('!4s4sBBH', s_addr, d_addr, placeholder, protocol, tcph_length * 4 + len(data))
        # calculating the tcp checksum
        tcp.checksum(pseudo_header + tcp_header + data)

        return [tcph, version, ihl, ttl, protocol, s_addr, d_addr, source_port, dest_port, sequence,
                acknowledgement, tcph_length, data]


    def validAck(self):
        return


    def waitForAck(self):
        '''
        This is a sample code from the reference. Need to implement functionality to wait for an ACK packet from
        destination for the most recently sent data.
        Once ACK is received, next data packet can be sent.
        '''
        while True:
            signal.signal(signal.SIGALRM, self.signalHandler)
            signal.alarm(180)  # 180 seconds
            try:
                self.response = self.socket.recvfrom(65565)
            except Exception as msg:
                print("Timed out on receiving ACK for the data sent: ", str(msg))
                # sys.exit(0)
            print(self.response)

            self.verifyPacket()
            self.decryptPacket()

            if self.validAck():
                return

        return