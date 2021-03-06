import sys
import socket
import signal
# import ip, tcp
import struct

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
        self.tcpFlags = None
        self.ipSeq = -1
        self.sequenceNum = -1
        self.ackNum = -1
        self.response = None
        self.isFin = False
        self.isErrorPacket = True
        self.sourceAddress = None
        self.destinationAddress = None


    def configure(self):
        try:
            print("\nConfiguring socket")
            self.sourceIp = socket.gethostbyname("127.0.0.1")      # "127.0.0.1"         #
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            print(type(self.sourceIp))
            print(self.sourceIp)
            print(type(self.destinationIp))
            print(self.destinationIp)
            print("Created raw socket")
            self.sourceAddress = socket.inet_aton(self.sourceIp)
            self.destinationAddress = socket.inet_aton(self.destinationIp)
            print("Translated addresses")
            print("Socket created")

            if self.mode == 'send':
                print("Configuring sender")
                self.destinationPort = self.port_8081
                self.sourcePort = self.port_8080
                # self.socket.connect((self.destinationIp, self.destinationPort))
                print("Connection established")
            elif self.mode == 'receive':
                print("Configuring receiver")
                self.destinationPort = self.port_8080
                self.sourcePort = self.port_8081
                self.socket.bind((self.sourceIp, self.sourcePort))
                print("Bound to host")

            self.ipSeq = 0
            self.sequenceNum = 0
            self.ackNum = 0

        except socket.error as msg:
            print('Socket could not be created. Error Code : ' + str(msg))


    def close(self):
        if self.socket:
            self.sendFIN()
            self.socket.close()


    # checksum functions needed for calculation checksum
    def checksum(self, msg):
        s = 0

        # # loop taking 2 characters at a time
        # for i in range(0, len(msg), 2):
        #     w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        #     s = s + w
        #
        # s = (s >> 16) + (s & 0xffff)
        # s = s + (s >> 16)
        #
        # #complement and mask to 4 byte short
        # s = ~s & 0xffff
        #
        # return s

        for i in range(0, len(msg), 2):
            # print("length ---",len(msg))
            # print(i)
            # print(i+1)
            # print("msg[i]",msg[i])
            # print("msg[i+1]",msg[i+1])
            # print("ord(msg[i])", ord(msg[i]))
            # print("ord(msg[i+1])", ord(msg[i + 1]))

            # w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
            w = ord(msg[i])
            if i + 1 < len(msg):
                w = w + (ord(msg[i + 1]) << 8)
            s = s + w

        s = (s >> 16) + (s & 0xffff)
        s = s + (s >> 16)

        # complement and mask to 4 byte short
        s = ~s & 0xffff

        return s


    def createIPHeader(self):
        # ip header fields
        ip_ihl = 5
        ip_ver = 4
        ip_tos = 0
        ip_tot_len = 0  # kernel will fill the correct total length
        self.ipSeq += 1
        ip_id = self.ipSeq  # Id of this packet
        ip_frag_off = 0
        ip_ttl = 255
        ip_proto = socket.IPPROTO_TCP
        ip_check = 0  # kernel will fill the correct checksum
        ip_saddr = socket.inet_aton((self.sourceIp))  # Spoof the source ip address if you want to
        ip_daddr = socket.inet_aton((self.destinationIp))

        ip_ihl_ver = (ip_ver << 4) + ip_ihl

        # the ! in the pack format string means network order
        ip_header = struct.pack('!BBHHHBBH4s4s', ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto,
                         ip_check, ip_saddr, ip_daddr)

        ip_check = self.checksum(ip_header)
        # print "ip_check checksum", ip_check

        self.ipHeader = struct.pack('!BBHHHBB', ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto) + struct.pack('H',
                            ip_check) + struct.pack('!4s4s', ip_saddr, ip_daddr)
        print(self.ipHeader)



    def createTCPHeader(self, flag_type):
        print("Building TCP header")
        print("SourcePort: ", self.sourcePort)
        print("DestinationPort: ", self.destinationPort)
        # tcp header fields
        tcp_source = self.sourcePort  # source port
        tcp_dest = self.destinationPort  # destination port
        self.sequenceNum += 1
        print("SeqNum: ", str(self.sequenceNum))
        tcp_seq = self.sequenceNum
        self.ackNum += 1
        print("AckNum: ", str(self.ackNum))
        tcp_ack_seq = self.ackNum
        tcp_doff = 5  # 4 bit field, size of tcp header, 5 * 4 = 20 bytes
        # tcp flags
        tcp_fin = 0
        tcp_syn = 0
        tcp_rst = 0
        tcp_psh = 0
        tcp_ack = 0
        tcp_urg = 0

        if flag_type == "FIN":
            print("FIN packet")
            tcp_fin = 1
        elif flag_type == "ACK":
            print("ACK packet")
            tcp_ack = 1

        tcp_window = socket.htons(5840)  # maximum allowed window size
        tcp_check = 0
        tcp_urg_ptr = 0

        tcp_offset_res = (tcp_doff << 4) + 0
        tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)
        self.tcpFlags = tcp_flags

        # the ! in the pack format string means network order
        tcp_header = struct.pack('!HHLLBBHHH', tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags, tcp_window,
                          tcp_check, tcp_urg_ptr)
        print("Created dummy packet:")
        print(tcp_header)

        # pseudo header fields
        source_address = socket.inet_aton(self.sourceIp)
        dest_address = socket.inet_aton(self.destinationIp)
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        tcp_length = len(self.ipHeader) + len(tcp_header) + len(self.data)

        psh = struct.pack('!4s4sBBH', source_address, dest_address, placeholder, protocol, tcp_length)
        print(psh)

        psh = psh + tcp_header + self.data
        # psh = tcp_header + self.data

        print(psh)
        tcp_check = self.checksum(psh)
        print(tcp_check)

        # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
        self.tcpHeader = struct.pack('!HHLLBBH', tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,
                                        tcp_window) + struct.pack('H', tcp_check) + struct.pack('!H', tcp_urg_ptr)
        print("TCP header:")
        print(self.tcpHeader)
        self.packet = self.ipHeader + self.tcpHeader + self.data
        print("Packet: ")
        print(self.packet)


    def createPacket(self):
        # Packet Header is ready
        # Recalculate the checksum with Data

        print("Creating data packet.")
        # pseudo header fields
        sourceAddress = socket.inet_aton(self.sourceIp)
        destAddress = socket.inet_aton(self.destinationIp)
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        print("1")
        tcpLength = len(self.tcpHeader) + len(self.data)
        tcp_doff = 5  # 4 bit field, size of tcp header, 5 * 4 = 20 bytes
        tcp_offset_res = (tcp_doff << 4) + 0
        tcp_flags = self.tcpFlags
        print("2")

        tcp_window = socket.htons(5840)  # maximum allowed window size
        tcp_urg_ptr = 0

        print("3")
        pseudoHeader = struct.pack('!4s4sBBH', sourceAddress, destAddress, placeholder, protocol, tcpLength)
        pseudoHeader = pseudoHeader + self.tcpHeader + self.data

        tcpCheck = self.checksum(pseudoHeader)
        print(tcpCheck)
        tcpCheck = 0
        print("4")

        # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
        # self.tcpHeader = struct.pack('!HHLLBBH', self.sourceIp, self.destinationIp, self.sequenceNum, self.ackNum, tcp_offset_res, tcp_flags,
        #                              tcp_window) + struct.pack('H', tcpCheck) + struct.pack('!H', tcp_urg_ptr)
        print("5")
        print(self.tcpHeader)

        # final full packet - syn packets dont have any data
        self.tcpFlags = None
        self.packet = self.ipHeader + self.tcpHeader + self.data
        print("Created the packet")


    def createHeaders(self, flag_type=""):
        self.createIPHeader()
        print("Created IP header")
        self.createTCPHeader(flag_type)
        print("Created TCP header")

        self.header = self.ipHeader + self.tcpHeader

    def reset(self):
        self.data = None
        self.packet = None
        self.header = None
        self.ipHeader = None
        self.tcpHeader = None
        self.response = None
        return


    def sendAck(self):
        self.createHeaders("ACK")
        # self.createPacket()
        self.socket.sendto(self.packet, (self.destinationIp, self.destinationPort))


    def sendFIN(self):
        self.createHeaders("FIN")
        # self.createPacket()
        self.socket.sendto(self.packet, (self.destinationIp, self.destinationPort))


    def sendData(self, dataFormat):
        try:
            (data, isLastChunk) = dataFormat
            self.data = data

            self.createHeaders()
            print("Created headers")
            # self.createPacket()
            print("Created packet")

            print("Sending data")
            self.socket.sendto(self.packet, (self.destinationIp, self.destinationPort))

            self.reset()

            if isLastChunk:
                print("Last chunk")
                self.isFin = True
                self.data = None
                self.sendFIN()
                self.reset()
        except Exception as msg:
            print("Error sending data to destination: ", str(msg))
        return


    def signalHandler(self, signum, frame):
        raise Exception("Timed out!")


    def decryptPacket(self):
        print("\n\nDecrypting packet")
        print(self.response)
        self.packet = self.response
        # packet string from tuple
        self.packet = self.packet[0]
        # take first 20 characters for the ip header
        self.ipHeader = self.packet[0:20]
        print("ip")
        print(self.ipHeader)
        # now unpack them
        iph = struct.unpack('!BBHHHBBH4s4s', self.ipHeader)
        # iph = struct.unpack('!BBHHHBB', self.ipHeader)

        version_ihl = iph[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0xF
        iph_length = ihl * 4
        ttl = iph[5]
        protocol = iph[6]
        chkSum = iph[7]
        s_addr = socket.inet_ntoa(iph[8])
        d_addr = socket.inet_ntoa(iph[9])
        # ip checksum to verify it
        # checkSum = self.checksum(self.ipHeader)

        # if chkSum != checkSum:
        #     self.isErrorPacket = True

        # print 'Version : ' + str(version) + ' IP Header Length : ' + str(ihl) + ' TTL : ' + str(ttl) + ' Protocol : ' + str(protocol) + ' Source Address : ' + str(s_addr) + ' Destination Address : ' + str(d_addr)
        # take the next 20 characters for tcp header
        tcp_header = self.packet[iph_length:iph_length + 20]
        print("\ntcp")
        print(tcp_header)
        # now unpack them
        tcph = struct.unpack('!HHLLBBHHH', tcp_header)
        # tcph = struct.unpack('!HHLLBBH', tcp_header)

        source_port = tcph[0]
        dest_port = tcph[1]
        print("SourcePort: ", source_port, "DestPort: ", dest_port)
        if source_port != self.sourcePort and dest_port != self.destinationPort:
            self.isErrorPacket = True

        self.sequenceNum = tcph[2]
        self.ackNum = tcph[3]
        print("SeqNum: ", str(self.sequenceNum), " AckNum: ", str(self.ackNum))
        doff_reserved = tcph[4]
        print("doff")
        print(doff_reserved)
        tcp_flags = tcph[6]
        tcph_length = doff_reserved >> 4
        print("tcph_length")
        print(tcph_length)
        # print 'Source Port : ' + str(source_port) + ' Dest Port : ' + str(dest_port) + ' Sequence Number : ' + str(sequence) + ' Acknowledgement : ' + str(acknowledgement) + ' TCP header length : ' + str(tcph_length)
        h_size = iph_length + tcph_length * 4
        # h_size = iph_length + tcph_length * 6
        data_size = len(self.packet) - h_size
        # get data from the packet
        self.data = self.packet[h_size:]
        print(self.data)

        '''
        Here, extract the TCP flags and check if the packet has any flags set.
        - ACK = 1 when packet sent is an ACK
        - FIN = 1 when packet sent is to terminate connection
        '''
        if tcp_flags == 1:
            print("\nReceived FIN")
            self.isFin = True
        elif tcp_flags == 16:
            print("\nReceived ACK")
            self.isAckPacket = True

        # for verifying tcp checksum
        # constructing the pseudo header
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        pseudo_header = struct.pack('!4s4sBBH', s_addr, d_addr, placeholder, protocol, tcph_length * 4 + len(self.data))
        # calculating the tcp checksum
        # self.checksum(pseudo_header + tcp_header + self.data)


        # return [tcph, version, ihl, ttl, protocol, s_addr, d_addr, source_port, dest_port, sequence,
        #         acknowledgement, tcph_length, self.data]


    def isValidPacket(self):
        # return not self.isErrorPacket
        return True


    def isValidAck(self):
        return self.isAckPacket


    def waitForAck(self):
        while True:
            print("Waiting for ACK.")
            signal.signal(signal.SIGALRM, self.signalHandler)
            signal.alarm(180)  # 180 seconds
            try:
                self.response = self.socket.recvfrom(1024)
            except Exception as msg:
                print("Timed out on receiving ACK for the data sent: ", str(msg))
                # sys.exit(0)
            print(self.response)

            self.decryptPacket()

            if self.isValidPacket() and self.isValidAck():
                break

        return


    def receiveData(self):
        while True:
            print("Waiting to receive data.")
            signal.signal(signal.SIGALRM, self.signalHandler)
            signal.alarm(180)  # 180 seconds
            try:
                self.response = self.socket.recvfrom(1024)
            except Exception as msg:
                print("Timed out on receiving the data from sender: ", str(msg))
                # sys.exit(0)
            print(self.response)

            self.decryptPacket()

            if self.isValidPacket():
                return self.data

        return None


    def isConnectionClosed(self):
        return self.isFin