# -*- coding: utf-8 -*-
"""
Demo code for connection between Python and FlexSim

FlexSim version: 2022.0.0
Python version: v3.8.10

Contact: Jonas Fuentes Leon (jofule8@uoc.es)
"""

import subprocess
import socket
import random


class FlexSimConnection():
    """
    Class for handling connection between Python and FLexSim
    """
    def __init__(self, flexsimPath, modelPath, address='localhost', port=5005, verbose=False, visible=False):
        self.flexsimPath = flexsimPath
        self.modelPath = modelPath
        self.address = address
        self.port = port
        self.verbose = verbose
        self.visible = visible

        # self._launch_flexsim()

    def _launch_flexsim(self):
        """
        Function for launching FlexSim
        """
        if self.verbose:
            print("Launching " + self.flexsimPath + " " + self.modelPath)

        args = [self.flexsimPath, self.modelPath]
        if self.visible is False:
            args.append("-maintenance")
            args.append("nogui")
        self.flexsimProcess = subprocess.Popen(args)

        self._socket_init(self.address, self.port)

    def _close_flexsim(self):
        """
        Function for closing FlexSim
        """
        self.flexsimProcess.kill()
        self._socket_end(self.address, self.port)
        if self.verbose:
            print("FlexSim closed. Ready to re-connect.")


    def _socket_init(self, host, port):
        """
        Function for initializing socket connection
        """
        if self.verbose:
            print("Waiting for FlexSim to connect to socket on " + self.address + ":" + str(self.port))

        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((host, port))
        self.serversocket.listen()

        (self.clientsocket, self.socketaddress) = self.serversocket.accept()
        if self.verbose:
            print("Socket connected")

        if self.verbose:
            print("Waiting for READY message")
        message = self._socket_recv()
        if self.verbose:
            print(message.decode('utf-8'))
        if message != b"READY":
            raise RuntimeError("Did not receive READY! message")

    def _socket_end(self, host, port):
        """
        Function for closing socket connection
        """
        if self.verbose:
            print("Closing socket")
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((host, port))
        self.serversocket.close()

    def _socket_send(self, msg):
        """
        Function for sending data through socket connection
        """
        totalsent = 0
        while totalsent < len(msg):
            sent = self.clientsocket.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            totalsent = totalsent + sent

    def _socket_recv(self):
        """
        Function for receiving data through socket connection
        """
        chunks = []
        while 1:
            chunk = self.clientsocket.recv(2048)
            if chunk == b'':
                raise RuntimeError("Socket connection broken")
            if chunk[-1] == ord('!'):
                chunks.append(chunk[:-1])
                break
            else:
                chunks.append(chunk)
        return b''.join(chunks)

def main():
    """
    Main function
    """

    FS = FlexSimConnection(
        flexsimPath = "C:/Program Files/FlexSim 2022/program/flexsim.exe",
        modelPath = "C:/Users/.../connection_demo.fsm",
        verbose = True,
        visible = True
        )

    # Launch:
    FS._launch_flexsim()

    # Set up simulation:
    SIM_SPED = 4 # simulation speed
    msg_recv = FS._socket_recv().decode('utf-8')
    print("Recv: {0}".format(msg_recv))
    FS._socket_send(str(SIM_SPED).encode())
    print("Sent: {0}".format(str(SIM_SPED)))

    MAX_PROD = 15 # max. number of products

    # Running simulation:
    info_req = "ireq"
    done = False
    i=1
    while not done:
        try:
            msg_recv = FS._socket_recv().decode('utf-8')
            print("Recv: {0}".format(msg_recv))

            if msg_recv == "maxprod":
                FS._socket_send(str(MAX_PROD).encode())
                print("Sent: {0}".format(str(MAX_PROD)))

            elif msg_recv == "product":
                label_s = "ID_"+str(i)
                FS._socket_send(label_s.encode())
                print("Sent: {0}".format(label_s))
                i+=1

            elif msg_recv == "type":
                type_s = random.choice(["A","B","C","D"])
                FS._socket_send(type_s.encode())
                print("Sent: {0}".format(type_s))

            elif msg_recv == "rack":
                FS._socket_send(info_req.encode())
                prod_type = FS._socket_recv().decode('utf-8')
                print("Recv: {0}".format(prod_type))
                rack_dict = {"A":"1","B":"1","C":"2","D":"2"}
                rack = rack_dict[prod_type]
                FS._socket_send(rack.encode())
                print("Sent: {0}".format(rack))

            elif msg_recv == "slot":
                FS._socket_send(info_req.encode())
                prod_type = FS._socket_recv().decode('utf-8')
                print("Recv: {0}".format(prod_type))
                rack_dict = {"A":"1","B":"1","C":"2","D":"2"}
                slot_dict = {"A":"1","B":"2","C":"1","D":"2"}
                rack = str(rack_dict[prod_type])
                slot = str(slot_dict[prod_type])
                address = "1-{}-{}-2-1".format(rack,slot)
                FS._socket_send(address.encode())
                print("Sent: {0}".format(address))

            elif msg_recv == "done":
                FS._socket_send(info_req.encode())
                trav_dist = FS._socket_recv().decode('utf-8')
                print("Total Distance: {0}".format(trav_dist))
                done = True
        except:
            done = True
            FS._close_flexsim()

    FS._close_flexsim()


if __name__ == "__main__":
    main()
