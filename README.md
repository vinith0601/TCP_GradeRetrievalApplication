# TCP_GradeRetrievalApplication

Code that consists of both the client side and the server side of a grade retrieval application. 
The client side would be opened in Command Prompt or Terminal using “python 
GradeRetrievalApp.py -r client” and the server side would be opened similarly using “python
GradeRetrievalApp.py -r server”. The server should be opened first, so that it’s able to listen
for the connection requests and then the client code can be opened to establish the connection.
The client can enter commands to retrieve the class averages for various assignments, but to
access their own grades they’ll need to login with an ID and password which will be
authenticated by the server.

The default host address is set to an IN_ADDR_ANY address which would allow for this TCP connection to be established between 2 ports onthe same machine and network. Changing these addresses to IP addresses of different machines on different machines will allow the TCP connection to be established between those 2 machines as long as both are connected to the internet. However the demonstration in the Lab report is done with both the client and server being on the same machine.
