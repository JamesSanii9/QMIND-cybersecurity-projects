import threading
import socket
import argparse
import os
import sys

#model depandancies
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
import pandas as pd
from official.nlp import optimization

# Path to the directory containing the saved model files
model_path = "C:/Users/17jcs9/Downloads/spam_classifier_bert (adam) (1)/spam_classifier_bert copy"

# Load the model
loaded_model = tf.keras.models.load_model(model_path, compile=False)


class Server(threading.Thread):
    #initialize server
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port

    def run(self):

        # Create a new socket object using IPv4 address family (AF_INET) and TCP protocol (SOCK_STREAM).
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set socket option to allow reusing the address/port even if it's already in use.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the socket to the specified host and port.
        sock.bind((self.host, self.port))
        # Start listening for incoming connections.
        sock.listen(1)
        print("listening at", sock.getsockname())

        while True:
            # accepting a new connection
            sc, sockname = sock.accept()
            print(f"Accepted a new connection from {sc.getpeername()} to {sc.getsockname()}")

            # Create new thread
            server_socket = ServerSocket(sc, sockname, self)

            # start new thread
            server_socket.start()

            # Add thread at active connection
            self.connections.append(server_socket)
            print("Ready to receive message from", sc.getpeername())

    def broadcast(self, message, source):
        #send message to all active connections
        for connection in self.connections:
            if connection.sockname != source:
                connection.send(message)

    def remove_connection(self, connection):
        #remove connection
        self.connections.remove(connection)


class ServerSocket(threading.Thread):
    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server

    def run(self):
        #loop to handle messages being recieved
        while True:
            try:
                #recieve message from client
                message = self.sc.recv(1024).decode("ascii")
                if message:
                    #if there is a message, format to insert into BERT model
                    d = {'message': [message]}
                    df = pd.DataFrame(data=d)
                    prediction = loaded_model.predict(df)[0][0]
                    prediction = tf.sigmoid(prediction).numpy()

                    #print prediction and message to verify everything is working properly
                    print(prediction)
                    print(f"{self.sockname} says {message}")
                    #Send message if not spam, otherwise do not send
                    if prediction < 0.5:
                        self.server.broadcast(message, self.sockname)
                    else:
                        print("spam detected: message not sent")
                else:
                    #connection was severed, close the connection and remove it
                    print(f"{self.sockname} has closed the connection")
                    self.sc.close()
                    server.remove_connection(self)
                    return
            except:
                #if something goes wrong kill the connection and remove client
                print(f"{self.sockname} has closed the connection")
                self.sc.close()
                server.remove_connection(self)
                return

    def send(self, message):
        #send message to all
        self.sc.sendall(message.encode('ascii'))


def exit_func(server):
    #kill the server
    while True:
        ipt = input("")
        if ipt == "q":
            #close all connections
            print("Close all connections...")
            for connection in server.connections:
                connection.sc.close()
            #shut down server
            print("shutting down server")
            os._exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chatroom Server")
    #first arguement is the host the server listens at
    parser.add_argument("host", help="Interface the server listens at")
    #optional arguements, run as default for demo
    parser.add_argument("-p", metavar="PORT", type=int, default=1060, help="TCP port(default 1060)")

    args = parser.parse_args()

    # create server
    server = Server(args.host, args.p)
    server.start()

    exit_f = threading.Thread(target=exit_func, args=(server,))
    exit_f.start()
