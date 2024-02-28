import threading
import socket
import argparse
import os

import sys
import tkinter as tk

class Send(threading.Thread):

    #listen for input from command line

    #socker the conneded sock object

    #name (str) : The username provided by user

    def __init__(self, sock, name):

        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):
        #Listen for user input from command line

        #send to server

        #Typing quit closes the connection

        while True:
            print("{}: ".format(self.name), end="")
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]

            #if QUIT leave

            if message == "QUIT":
                self.sock.sendall("Server: {} has left the chat.".format(self.name).encode("ascii"))
                break

            else: 
                self.sock.sendall("{}: {}".format(self.name, message).encode("ascii"))

        print("\n Quitting...")
        self.sock.close()

        os._exit(0)

class Receive(threading.Thread):

    def __init__(self, sock, name):

        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = None

    def run(self):

        while True:
            #recieve message
            message = self.sock.recv(1024).decode("ascii")
            if message:

                if self.messages:
                    #add message to end of tinker
                    self.messages.insert(tk.END, message)
                    print("\r{}\n{}: ".format(message, self.name), end="")
                else:
                    print("\r{}\n{}: ".format(message, self.name), end="")
            else:
                #if no message, quit since server dc
                print("\n Lost connection to server")
                print("Quitting ...")
                self.sock.close()
                os._exit()

class Client:

    #Manage client-server connection

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.message = None


    def start(self):
        #connect to host
        print("Try to connect to {}:{} ... ".format(self.host, self.port))
        self.sock.connect((self.host, self.port))

        print("Successfully connected to {} : {}".format(self.host, self.port))

        print()

        self.name = input("Your name: ")

        print()
        print("Welcome, {}!Getting ready to send and recieve messages".format(self.name))

        #create send and recieve threads

        send = Send(self.sock, self.name)
        receive = Receive(self.sock, self.name)

        #start threads
        send.start()
        receive.start()

        #message to all saying that a new person has joined the chat
        self.sock.sendall("Server: {} has joined the chat".format(self.name).encode("ascii"))

        print("\rReady leave chat by typing QUIT")
        print("{}: ".format(self.name), end="")

        return receive
    
    def send(self, textInput, window):
        #get message from textbox
        message = textInput.get()
        #clear textbox after send
        textInput.delete(0, tk.END)
        #add message to local messages
        self.messages.insert(tk.END, "{}: {}".format(self.name, message))

        #Type quit to close GUI
        if message == "QUIT":
            self.sock.sendall("Server: {} has left the chat".format(self.name).encode("ascii"))
            print("\n Quitting ...")
            self.sock.close()
            window.quit()
            os._exit(0)


        #SEND message to server
        else:
            self.sock.sendall("{}: {}".format(self.name, message).encode("ascii"))

def main(host, port):
    #initialize and run GUI
    #create client
    client = Client(host, port)
    receive = client.start()
    #create tinker window
    window = tk.Tk()
    window.title("Text Simulation")

    #define tinker components
    fromMessage = tk.Frame(master=window)
    scrollBar = tk.Scrollbar(master = fromMessage)
    messages = tk.Listbox(master=fromMessage, yscrollcommand=scrollBar.set)
    scrollBar.pack(side=tk.RIGHT, fill = tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    #assign message listbox to client and recieve objects
    client.messages = messages
    receive.messages = messages

    
    # Create a frame for the message input entry field.
    fromMessage.grid(row=0, column=0, columnspan=2, sticky="nsew")
    fromEntry = tk.Frame(master=window)
    textInput = tk.Entry(master=fromEntry)

    textInput.pack(fill=tk.BOTH, expand=True)

    # Bind the Return key event to send the message.
    textInput.bind("<Return>", lambda x: client.send(textInput, window))
    textInput.insert(0, "Write message here")

    # Create a button for sending messages.
    btnSend = tk.Button(
        master=window,
        text="Send",
        command=lambda:client.send(textInput, window)
    )
    # Place the message input frame and send button in the window.
    fromEntry.grid(row=1,column=0, padx=10, sticky="ew")
    btnSend.grid(row=1,column=1, pady=10, sticky="ew")

    # Configure row and column weights for resizing.
    window.rowconfigure(0,minsize=500, weight=1)
    window.rowconfigure(1,minsize=50, weight=0)
    window.columnconfigure(0,minsize=500, weight=1)
    window.columnconfigure(1,minsize=200, weight=0)

    window.mainloop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Chatroom Server")
    parser.add_argument("host", help="Interface the server listens at")
    parser.add_argument("-p", metavar = "PORT", type=int, default=1060, help="TCP port(default 1060)")

    args = parser.parse_args()

    main(args.host, args.p)


