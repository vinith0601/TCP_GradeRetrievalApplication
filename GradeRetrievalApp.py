"""
Grade Retrieval Application (Client and Server Classes)

Siddharth Bedekar - 400073781
Noubar Nakhnikian - 400052226
Hamzah Muhammad - 400104737
Vinith Rajaretnam - 400070849

to create a Client: "python GradeRetrievalApp.py -r client" 
to create a Server: "python GradeRetrievalApp.py -r server" 
"""

import socket
import argparse
import sys
import hashlib
from constants import *
from getpass import getpass
import csv


########################################################################
# Echo Server class
########################################################################

class Server:
    # Set the server hostname used to define the server socket address
    # binding. Note that 0.0.0.0 or "" serves as INADDR_ANY. i.e.,
    # bind to all local network interface addresses.
    HOSTNAME = "0.0.0.0"

    # Set the server port to bind the listen socket to.
    PORT = 50000

    RECV_BUFFER_SIZE = 1024
    MAX_CONNECTION_BACKLOG = 10

    # Create server socket address. It is a tuple containing
    # address/hostname and port.
    SOCKET_ADDRESS = (HOSTNAME, PORT)

    def __init__(self):
        self.authorizing = False
        self.db = Server.getFileData("course_grades_2021.csv")
        self.printDB()
        self.db_len = len(self.db)
        self.create_listen_socket()
        self.process_connections_forever()

    #-------------------NON TCP METHODS---------------------

    def printDB(self):
        print("Data read from CSV file:")
        for i in (self.db):
            print(i)

    def getFileData(filename):
        '''
        returns 2D array of csv without header coloums
        '''
        try:
            f = open(filename, 'r')
        except FileNotFoundError:
            print("Could not find file with name", filename);
            sys.exit()
        
        result = []
        temp = f.readlines()    
        for i in range(1, len(temp)):
            result.append(temp[i].strip("\n").split(","))

        #some random spaces in csv that need to be removed
        for i in range(len(result)):
            for j in range(len(result[i])):
                result[i][j] = result[i][j].strip()

        f.close()
        return result

    def encrypt(user, pw):
        m = hashlib.sha256()
        m.update(user.encode(MSG_ENCODING))
        m.update(pw.encode(MSG_ENCODING))
        return m.digest()

    def get_mt_avg(self):
        return self.db[self.db_len-1][MT_I]
 
    def get_l1_avg(self):
        return self.db[self.db_len-1][L1_I]

    def get_l2_avg(self):
        return self.db[self.db_len-1][L2_I]

    def get_l3_avg(self):
        return self.db[self.db_len-1][L3_I]

    def get_l4_avg(self):
        return self.db[self.db_len-1][L4_I]

    def get_grades(self, input_hash):
        for i in range(self.db_len-1):   # -1 so we dont include the averages row
            hash_i = Server.encrypt(self.db[i][ID_I], self.db[i][PW_I])
            if (input_hash == hash_i):
                #return grades
                return  ','.join([self.db[i][MT_I],
                         self.db[i][L1_I],
                         self.db[i][L2_I],
                         self.db[i][L3_I],
                         self.db[i][L4_I]]) #return string comma separated
        return ''

    def decodeCommand(self, str):
        if (str == "GMA"):
            return self.get_mt_avg()
        elif (str == "GL1A"):
            return self.get_l1_avg()
        elif (str == "GL2A"):
            return self.get_l2_avg()
        elif (str == "GL3A"):
            return self.get_l3_avg()
        elif (str == "GL4A"):
            return self.get_l4_avg()
        else:    # (str == "GG"):
            return self.prompt_auth() # auth through GG or something other than above

    def prompt_auth(self):
        self.authorizing = True
        return "Enter Username and Password:"


    #------------------------TCP METHODS-----------------------


    def create_listen_socket(self):
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Set socket layer socket options. This allows us to reuse
            # the socket without waiting for any timeouts.
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind socket to socket address, i.e., IP address and port.
            self.socket.bind(Server.SOCKET_ADDRESS)

            # Set socket to listen state.
            self.socket.listen(Server.MAX_CONNECTION_BACKLOG)
            print("Listening on port {} ...".format(Server.PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def process_connections_forever(self):
        try:
            while True:
                # Block while waiting for accepting incoming
                # connections. When one is accepted, pass the new
                # (cloned) socket reference to the connection handler
                # function.
                self.connection_handler(self.socket.accept())
        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            self.socket.close()
            sys.exit(1)

    def connection_handler(self, client):
        connection, address_port = client
        print("-" * 72)
        print("Connection received from {}.".format(address_port))

        while True:
            try:
                # Receive bytes over the TCP connection. This will block
                # until "at least 1 byte or more" is available.
                recvd_bytes = connection.recv(Server.RECV_BUFFER_SIZE)
            
                # If recv returns with zero bytes, the other end of the
                # TCP connection has closed (The other end is probably in
                # FIN WAIT 2 and we are in CLOSE WAIT.). If so, close the
                # server end of the connection and get the next client
                # connection.
                if len(recvd_bytes) == 0:
                    print("Closing client connection ... ")
                    connection.close()
                    break
                
                # Decode the received bytes back into strings. Then output
                # them.
                
                if (self.authorizing):
                    recvd_str = recvd_bytes
                    print("\nID/pass hash recieved from server")
                    output = self.get_grades(recvd_str).encode(MSG_ENCODING)
                    
                    if (len(output) == 0):
                        print("ID/Password Failure. Aborting Fetch.".encode(MSG_ENCODING))
                        output = ("Incorrect Credentials".encode(MSG_ENCODING))
                    else:
                        print("Correct Password, Record Found".encode(MSG_ENCODING))

                    self.authorizing = False

                else:
                    recvd_str = recvd_bytes.decode(MSG_ENCODING)
                    print("\nReceived: ", recvd_str, "Command from Client")
                    output = (self.decodeCommand(recvd_str)).encode(MSG_ENCODING)
                # Send the received bytes back to the client.
                connection.sendall(output)
                print("Sent: ", output)

            except KeyboardInterrupt:
                print()
                print("Closing client connection ... ")
                connection.close()
                break

########################################################################
# Echo Client class
########################################################################

class Client:

    # Set the server hostname to connect to. If the server and client
    # are running on the same machine, we can use the current
    # hostname.
    SERVER_HOSTNAME = socket.gethostbyname('localhost')
    MSG_ENCODING = "utf-8"
    SERVER_PORT = 50000
    RECV_BUFFER_SIZE = 1024

    def __init__(self):
        self.authorizing = False
        self.get_socket()
        self.connect_to_server()
        self.send_console_input_forever()

#-------------------NON TCP METHODS --------------------------------

    def encrypt():
        user = input("ID: ")
        pw = getpass(prompt="Password: ")
        m = hashlib.sha256()
        m.update(user.encode(MSG_ENCODING))
        m.update(pw.encode(MSG_ENCODING))
        return m.digest()




#-------------------TCP METHODS --------------------------------

    def get_socket(self):
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as msg:
            print(msg)
            sys.exit(1)


    def connect_to_server(self):
        try:
            # Connect to the server using its socket address tuple.
            self.socket.connect((Client.SERVER_HOSTNAME, self.SERVER_PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def get_console_input(self):
        # In this version we keep prompting the user until a non-blank
        # line is entered.
        while True:
            self.input_text = input("Enter Command: ")
            if self.input_text != "":
                print("Command Entered:", self.input_text)
                print(self.fetchingStatement())
                break
    
    def fetchingStatement(self):
        str = self.input_text
        if (str == "GMA"):
            return "Fetching Midterm Average"
        elif (str == "GL1A"):
            return "Fetching Lab 1 Average"
        elif (str == "GL2A"):
            return "Fetching Lab 2 Average"
        elif (str == "GL3A"):
            return "Fetching Lab 3 Average"
        elif (str == "GL4A"):
            return "Fetching Lab 4 Average"
        else:    # (str == "GG"):
            return "Login Required to Fetch Grades"
        
    def send_console_input_forever(self):
        while True:
            try:
                if (self.authorizing == False): #get credentials from connection_send directly - no input command
                    self.get_console_input()
                self.connection_send()
                self.connection_receive()
            except (KeyboardInterrupt, EOFError):
                print()
                print("Closing server connection ...")
                self.socket.close()
                sys.exit(1)
                
    def connection_send(self):
        try:
            # Send string objects over the connection. The string must
            # be encoded into bytes objects first.
            if (self.authorizing):
                input_text_secure = Client.encrypt()
                print("ID/pass hash sent to server")
                self.socket.sendall(input_text_secure) # already bytes object - no encode
                self.authorizing = False
            else:
                self.socket.sendall(self.input_text.encode(MSG_ENCODING))
            
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connection_receive(self):
        try:
            # Receive and print out text. The received bytes objects
            # must be decoded into string objects.
            recvd_bytes = self.socket.recv(Client.RECV_BUFFER_SIZE)

            # recv will block if nothing is available. If we receive
            # zero bytes, the connection has been closed from the
            # other end. In that case, close the connection on this
            # end and exit.
            if len(recvd_bytes) == 0:
                print("Closing server connection ... ")
                self.socket.close()
                sys.exit(1)

            print("Received: ", recvd_bytes.decode(MSG_ENCODING), "\n")

            #GG has been sent
            if (recvd_bytes.decode(MSG_ENCODING) == "Enter Username and Password:"):
                self.authorizing = True

        except Exception as msg:
            print(msg)
            sys.exit(1)

########################################################################
# Process command line arguments if this module is run directly.
########################################################################

# When the python interpreter runs this module directly (rather than
# importing it into another file) it sets the __name__ variable to a
# value of "__main__". If this file is imported from another module,
# then __name__ will be set to that module's name.

if __name__ == '__main__':
    roles = {'client': Client,'server': Server}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='server or client role',
                        required=True, type=str)

    args = parser.parse_args()
    roles[args.role]()

########################################################################






