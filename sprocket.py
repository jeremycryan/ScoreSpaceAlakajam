import socket
import threading
import pickle
import struct
import time


__all__ = ["Packet", "Servo", "Sprocket"]


class Packet:
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    def __str__(self):
        title = [f"Packet at {id(self)}:"]
        lines = [f"  {item}: {self.__dict__[item]}" for item in self.__dict__]
        return "\n".join(title + lines)

    def __repr__(self):
        return self.__str__(self)

    def add(self, **kwargs):
        """ Add an arbitrary number of keyword arguments to the Packet's dictionary. """
        self.__dict__.update(kwargs)

    def has(self, index):
        """ Returns true if the specified index exists in the packet dictionary. """
        return index in self.__dict__

    def get(self, index, default=None):
        """ Return an item from the Packet's dictionary via index (probably a string). If it doesn't
            exist, instead return the default value.
        """
        if not self.has(index):
            return default
        return self.__dict__[index]

    def to_bytes(self):
        """ Convert the packet to bytes via pickle. """
        return pickle.dumps(self)

    @staticmethod
    def from_bytes(data):
        """ Construct and return a new packet from a pickle output. """
        return pickle.loads(data)


class Sprocket:
    def __init__(self, host, port=41398):

        # Establish socket connection and empty message queue
        self.sock = socket.socket(type=socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.queue = []
        self.queue_mutex = threading.Lock()

        # Run thread to receive messages
        self.receive_thread = threading.Thread(target=self.continuously_receive_packets, daemon=True)
        self.receive_thread.start()

    def get(self):
        """ Returns the list of packets currently in the queue. """
        with self.queue_mutex:
            response = self.queue[:]
            self.queue = []
        return response

    def receive_packet(self):
        """ Receives a message from the socket, then appends it to the queue. This method is blocking,
            but only acquires the queue mutex to add the new message.
        """

        header = receive_exactly(self.sock, 8)
        size = struct.unpack("!Q", header)[0]
        data = receive_exactly(self.sock, size)
        new_packet = Packet.from_bytes(data)

        with self.queue_mutex:
            self.queue.append(new_packet)

    def continuously_receive_packets(self):
        """ Calls receive continuously. Wouldn't recommend calling, unless using threading. """
        while True:
            self.receive_packet()

    def send_packet(self, packet_object):
        serialized = packet_object.to_bytes()
        size = len(serialized)
        header = struct.pack("!Q", size)

        self.sock.sendall(header)
        self.sock.sendall(serialized)

    def send(self, **kwargs):
        self.send_packet(Packet(**kwargs))

    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()


class Client:
    def __init__(self, conn, address, servo):
        self.start_time = time.time()
        self.conn = conn
        self.ip, self.port = address
        self.servo = servo
        self.client_id = servo.new_client_id()
        self.servo.id_to_client[self.client_id] = self

    def receive_packet(self):
        """ Receives a message from the socket, then appends it to the queue. This method is blocking,
            but only acquires the queue mutex to add the new message.

            Returns the message (bytes object).
        """

        header = receive_exactly(self.conn, 8)
        size = struct.unpack("!Q", header)[0]
        data = receive_exactly(self.conn, size)
        new_packet = Packet.from_bytes(data)
        new_packet.client_id = self.client_id

        with self.servo.queue_mutex:
            self.servo.queue.append(new_packet)

    def continuously_receive_packets(self):
        while True:
            try:
                self.receive_packet()
            except ConnectionResetError:
                self.servo.remove_client(self.client_id)

    def send_packet(self, packet_object):
        serialized = packet_object.to_bytes()
        size = len(serialized)
        header = struct.pack("!Q", size)
        self.conn.sendall(header)
        self.conn.sendall(serialized)


class Servo:
    def __init__(self, host="", port=41398):
        self.sock = socket.socket()
        self.sock.bind((host, port))
        self.sock.listen()
        self.clients = []
        self.id_to_client = {}
        self.queue = []

        self.queue_mutex = threading.Lock()
        self.client_mutex = threading.Lock()

        self.client_id_count = 0

        print("Server initialized.")
        accept_thread = threading.Thread(target=self.accept_connection, daemon=True)
        accept_thread.start()

    def new_client_id(self):
        new = self.client_id_count
        self.client_id_count += 1
        return new

    def accept_connection(self):
        print("Listening for connections...")
        while True:
            self.sock.listen()
            conn, address = self.sock.accept()
            with self.client_mutex:
                new_client = Client(conn, address, self)
                self.clients.append(new_client)
                #print(f"Client {new_client.client_id} joined with ip {new_client.ip}")
            client_thread = threading.Thread(target=new_client.continuously_receive_packets, daemon=True)
            client_thread.start()

    def get(self):
        """ Returns the list of packets currently in the queue. """
        with self.queue_mutex:
            response = self.queue[:]
            self.queue = []
        return response

    def remove_client(self, client_id):
        with self.client_mutex:
            self.remove_client_no_mutex(client_id)

    def remove_client_no_mutex(self, client_id):
        if client_id not in self.id_to_client:
            return
        removed_client = self.id_to_client.pop(client_id)
        self.clients.remove(removed_client)
        #print(f"Client {client_id} at ip {removed_client.ip} disconnected.")

    def send(self, *client_ids, **kwargs):
        """ Sends a packet consisting of the information in kwargs to each client id specified. """
        with self.client_mutex:
            for client_id in client_ids:
                client = self.id_to_client[client_id]
                try:
                    client.send_packet(Packet(**kwargs))
                except ConnectionResetError:
                    self.remove_client_no_mutex(client.client_id)

    def send_all(self, **kwargs):
        """ Sends a packet consisting of the information in kwargs to all clients."""
        with self.client_mutex:
            client_ids = [key for key in self.id_to_client]
        self.send(*client_ids, **kwargs)

    def send_all_but(self, *client_ids, **kwargs):
        """ Sends a packet consisting of the information in kwargs to each client id except those specified. """

        # Get list of all clients
        with self.client_mutex:
            all_client_ids = [key for key in self.id_to_client]

        # Exclude specified clients
        for client_id in client_ids:
            if client_id in all_client_ids:
                all_client_ids.remove(client_id)

        # Send packet
        self.send(*all_client_ids, **kwargs)


def receive_exactly(sock, n):
    """ Receive exactly n bytes from the socket, then returns them. """
    data = b''
    while n > 0:
        chunk = sock.recv(n)
        n -= len(chunk)
        data += chunk
    return data
