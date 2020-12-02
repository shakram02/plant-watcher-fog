from typing import List, Tuple, Union
import uuid
import struct
import select
import socket
from datetime import datetime

NAMESPACE = uuid.uuid4()
NOLINGER = struct.pack('ii', 1, 0)
TIMEOUT_VAL = struct.pack('ll', 5, 0)


def _read_data(client: socket.socket):
    data = b''
    buf_size = 256
    try:
        while True:
            buf = client.recv(buf_size)
            data += buf
            if b"\r\n" in data:
                break
    except BlockingIOError:
        pass

    return data


def read_chunkable_message(client_buffer: bytes):
    splits = client_buffer.split(b'\r\n')
    if not splits:
        return None

    return splits


class EdgeServer(object):
    def __init__(self, ip, port):
        """
        Initializes a new EdgeServer
        """
        self.addr = (ip, port)
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_LINGER, NOLINGER)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_RCVTIMEO, TIMEOUT_VAL)
        self.server_sock.setblocking(0)

        self.message_buffers = {}
        self.heartbeats = {}
        self.outputs = []

    def loop_forever(self):
        self.server_sock.bind(self.addr)
        self.inputs = [self.server_sock]
        print("Bound to:", self.addr)
        while True:
            self._loop()

    def _loop(self):
        """
            Runs select() and handles readble/writable/errornous sockets.
            After each select loop, idle clients are closed and removed.
        """
        readable, _, exceptional = select.select(
            self.inputs, self.outputs, self.inputs)

        client_messages = self._read_sockets(readable)
        if client_messages:
            print(*client_messages.values())
        self._clean_idle()
        if exceptional:
            print("EXCEPTION:", exceptional)

    def _read_sockets(self, readable):
        """
            Reads server socket that has available data,
            then welcome those new clients by giving
            them a UUID if it's their first time connecting.

            Otherwise, read their data and extract complete
            messages.
        """
        if not readable:
            return

        client_messages = {}
        data, address = self.server_sock.recvfrom(1024)
        msg_type = data[0]
        msg = data[1:]
        if msg_type == 0x01:
            secret = str(msg, "UTF-8")
            client_uuid = self._initialize_new_client(secret, address)
            print(f"[{secret}] Connected as: {client_uuid}")
        else:
            msg = str(msg, "UTF-8")
            print("DATA:", msg)
            # msgs = self._read_client_messages(msg)
            # client_messages[address] = msgs

        return client_messages

    def _initialize_new_client(self, secret: str, address: Tuple[str, int]) -> str:
        device_uuid = str(uuid.uuid3(NAMESPACE, str(secret)))

        self.server_sock.sendto(bytes(device_uuid, "UTF-8"), address)

        self.message_buffers[address] = b''
        self.heartbeats[address] = datetime.now()
        return device_uuid

    def _read_client_messages(self, client) -> Union[None, List]:
        data = _read_data(client)
        if not data:
            return None

        self.message_buffers[client] += data
        msgs = read_chunkable_message(self.message_buffers[client])
        if not msgs:
            return []
        else:
            *full, rem = msgs
            # Re-append unparsed messages
            self.message_buffers[client] = rem
        return full

    def _clean_idle(self):
        now = datetime.now()
        for client in tuple(self.heartbeats):
            client: socket.socket = client
            last_heartbeat_timestamp = self.heartbeats[client]
            idle = (now - last_heartbeat_timestamp)
            idle_minutes = idle.total_seconds() // 60
            if idle_minutes > 0:
                print(client.getpeername(), "Idle for:",
                      idle_minutes, "minutes [{} s]".format(idle.total_seconds()))

                # Remove client data
                self.heartbeats.pop(client)
                self.inputs.remove(client)
                client.close()
