import socket
import os
import threading

class WebProxy:

    MAX_CONNECTIONS = 5

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def handleRequest(self, client, address):
        #TODO: Caching
        data = client.recv(1024).decode()

        # Get hostname from request
        requestName = data.split(' ')[1].split("http://")[1]

        # Remove trailing / on hostname
        if (requestName[len(requestName)-1] == "/"):
            requestName = requestName[:-1]
        
        # Convert to IP
        requestAddress = socket.gethostbyname(requestName)
        requestMethod = data.split(' ')[0]

        print("Method: {requestMethod}".format(requestMethod=requestMethod))
        print("Host: {requestName} - ({requestAddress})".format(requestName=requestName, requestAddress=requestAddress))
        
        # Use temporary socket to get data from host
        tempSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tempSocket.connect((requestAddress, 80)) # Connect to requested host
        tempSocket.sendall(data.encode()) # Forward data from client to host

        response = ""
        if requestMethod == "GET":
            while True:
                response = tempSocket.recv(1024) # Get data from host
                if not response: break
                client.send(response) # Send data back to client
        client.close() # Close socket connection

    def startProxy(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create socket object

        # Attempt to bind to address and port
        try:
            self.server.bind((self.host, self.port))
            print("Started server on port: {port}".format(port=self.port))
        except:
            print("Failed to bind to port {port}".format(port=self.port))
            self.server.close()

        self.server.listen(self.MAX_CONNECTIONS)

        # Indefinetly listen for any new incoming connections
        while True:
            print("Waiting for connections...")
            (client, address) = self.server.accept()
            client.settimeout(60) # 60s timeout
            print("Received connection from {addr}".format(addr=address))
            # Create a thread for this connection
            threading.Thread(target=self.handleRequest, args=(client, address)).start()

proxy = WebProxy("localhost", 3001)
proxy.startProxy()