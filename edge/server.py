from typing import List, Tuple, Union
import uuid
import struct
import select
import socket
import enum
import json
import logging
from edge import status
from datetime import datetime
from queue import Queue

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


class MessageType(enum.Enum):
    Hello = 0x1
    Data = 0x2
    Command = 0x3


class EdgeMessage(object):
    """
        An EdgeMessage is a full message from the node
        including the header.
    """
    HeaderSize = 3

    def __init__(self, msg_type: MessageType, msg_length: int, msg_data: bytes):
        self.type = msg_type
        self.length = msg_length
        self.data = json.loads(
            msg_data, object_hook=status.as_edge_update)


class EdgeServer(object):
    def __init__(self, ip: str, port: int, msg_queue: Queue):
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
        self.msg_queue = msg_queue

    def loop_forever(self):
        self.server_sock.bind(self.addr)
        self.inputs = [self.server_sock]
        logging.info(f"Bound to: {self.addr}")
        while True:
            self._loop()

    def _loop(self):
        """
            Runs select() and handles readable/writable/errornous sockets.
            After each select loop, idle clients are closed and removed.
        """
        readable, _, exceptional = select.select(
            self.inputs, self.outputs, self.inputs)

        client_messages = self._read_sockets(readable)
        if client_messages:
            logging.info(f"{client_messages.values()}")

        if exceptional:
            logging.info(f"EXCEPTION: {exceptional}")

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
        data = self.server_sock.recv(EdgeMessage.HeaderSize, socket.MSG_PEEK)
        (msg_type, msg_length) = self._parse_header(data)

        data, address = self.server_sock.recvfrom(
            msg_length+EdgeMessage.HeaderSize)

        if msg_type == MessageType.Hello:
            secret = str(data[EdgeMessage.HeaderSize:], "UTF-8")
            client_uuid = self._initialize_new_client(secret, address)
            logging.info(f"[{secret}] Connected as: {client_uuid}")
        elif msg_type == MessageType.Data:
            msg = self._parse_message(data)
            msg: status.EdgeUpdate = msg.data

            logging.debug(f"({msg.uuid})\t{msg}")
            self.msg_queue.put(msg)

        return client_messages

    @staticmethod
    def _parse_header(msg_header):
        (msg_type, msg_length) = struct.unpack_from('<BH', msg_header)
        return MessageType(msg_type), msg_length

    @staticmethod
    def _parse_message(msg_bytes) -> EdgeMessage:
        (msg_type, msg_length) = struct.unpack_from('<BH', msg_bytes)
        msg_data = str(msg_bytes[3:], "ASCII")

        return EdgeMessage(MessageType(msg_type), msg_length, msg_data)

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
