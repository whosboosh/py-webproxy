import socket
import os
import threading

class WebProxy:

    MAX_CONNECTIONS = 5

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def handleRequest(self, client, address):
        data = client.recv(1024).decode()

        # Get hostname from request
        try:
            requestName = data.split(' ')[1].split("http://")[1]
        except:
            print("Only http requests can be made")
            client.close()
            return

        # Remove trailing / on hostname
        if (requestName[len(requestName)-1] == "/"):
            requestName = requestName[:-1]

        # Get port from host
        try:
            requestPort = requestName.split(":")[1].split("/")[0]
        except:
            requestPort = 80

        # Get the file requested from host
        # Check if on base directory, if so make file requested simply 'index.html'
        try:
            fileToServe = requestName.split("/")[1]
        except:
            fileToServe = "index.html"

        # Remove the file ending, just the hostname and/or port
        host = requestName.split("/")[0]
        # Remove port from host
        requestName = host.split(":")[0]

        print(requestName)

        # Convert to IP
        requestAddress = socket.gethostbyname(requestName)
        requestMethod = data.split(' ')[0]
        
        print("Method: {requestMethod}".format(requestMethod=requestMethod))
        print("Host: {requestName} - ({requestAddress})".format(requestName=requestName, requestAddress=requestAddress))
        print("Port: {port}".format(port=requestPort))
        print("File: {file}".format(file=fileToServe))
        
        cache = requestName+"/"+fileToServe+".html"
        # Try to open cache, if exists use that, otherwise fetch new data
        try:
            print("Attepting to open from cache: '"+cache+"'")
            file = open(cache,"rb")
            response = file.read()
            file.close()             
        except:
            print("No cache found for: '"+cache+"'. Creating...")
            try:
                os.mkdir(requestName) # Try to create folder for site
            except:
                print("Folder already exists: "+requestName+". Creating cache file for "+fileToServe+".html")
            cacheFile = open(cache, "wb") # Create the file

            # Use temporary socket to get data from host
            tempSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tempSocket.connect((requestAddress, int(requestPort))) # Connect to requested host
            tempSocket.sendall(data.encode()) # Forward data from client to host

            response = tempSocket.recv(1024) # Get data from host

            cacheFile.write(response)

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

proxy = WebProxy("localhost", 3002)
proxy.startProxy()