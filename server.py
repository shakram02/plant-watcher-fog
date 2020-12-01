import socket
import struct
import uuid
import select
import paho.mqtt.client as mqtt
from datetime import datetime
MQTT_BROKER = "174.138.103.162"
MQTT_TOPIC = "/hello_world"
MQTT_PORT = 3881
NAMESPACE = uuid.uuid4()

NOLINGER = struct.pack('ii', 1, 0)
TIMEOUT_VAL = struct.pack('ll', 5, 0)


def connect_mqtt(client):
    """
    Connects the client to MQTT server
    if it's not already connected.
    """
    client.connect(MQTT_BROKER, port=MQTT_PORT)  # connect to MQTT broke


def mqtt_main():
    client = mqtt.Client()  # create new instance
    connect_mqtt(client)

    while True:
        message = input(">")

        if not client.is_connected():
            # connect to MQTT broker
            client.connect(MQTT_BROKER, port=MQTT_PORT)

        if not message:
            break
        client.publish(MQTT_TOPIC, message)


def read_data(client: socket.socket):
    data = b''
    buf_size = 256
    try:
        while True:
            buf = client.recv(buf_size)
            data += buf
            if b"\r\n" in data:
                break
    except BlockingIOError:
        print("BLOCKING IO", data)
        pass

    return data


def read_chunkable_message(client_buffer: bytes):
    splits = client_buffer.split(b'\r\n')
    if not splits:
        return None

    return splits


def http_main():

    # Create a TCP/IP socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = ("0.0.0.0", 8000)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, NOLINGER)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, TIMEOUT_VAL)
    server_sock.setblocking(0)
    server_sock.bind(addr)
    server_sock.listen(5)

    inputs = [server_sock]
    outputs = []
    message_queues = {}
    heartbeats = {}

    print("Waiting for connection...")
    while True:
        readable, writable, exceptional = select.select(
            inputs, outputs, inputs)
        print("SELECT")
        for s in readable:
            if s is server_sock:
                client, address = server_sock.accept()
                print("Connection from {}:{}".format(*address))

                client.setblocking(0)
                inputs.append(client)
            else:
                client: socket.socket = s
                if client not in message_queues:
                    secret = client.recv(128)
                    device_uuid = str(uuid.uuid3(NAMESPACE, str(secret)))
                    print("UUID:", device_uuid)
                    client.send(bytes(device_uuid, "UTF-8"))
                    message_queues[client] = b''
                    heartbeats[client] = datetime.now()
                else:
                    data = read_data(client)
                    if not data:
                        print("Client disconnected")
                        inputs.remove(client)
                        outputs.remove(client)

                    message_queues[client] += data
                    msgs = read_chunkable_message(message_queues[client])
                    if not msgs:
                        continue
                    else:
                        *full, rem = msgs
                        # Re-append unparsed messages
                        message_queues[client] = rem
                        print("MESSAGES:", full)

            if exceptional:
                print("EXCEPTION:", exceptional)

            now = datetime.now()
            for client in tuple(heartbeats):
                last_heartbeat_timestamp = heartbeats[client]
                idle_minutes = (
                    now - last_heartbeat_timestamp).total_seconds() // 60
                if idle_minutes > 0:
                    print(client.getsockname(), "Idle for:",
                          idle_minutes, "minutes")

                    # Remove client data
                    heartbeats.pop(client)
                    inputs.remove(client)
                    client.close()


def main():
    # mqtt_main()
    http_main()


if __name__ == "__main__":
    main()
