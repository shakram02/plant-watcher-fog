import socket
import struct
import uuid
import paho.mqtt.client as mqtt
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


def read_data(client):
    data = b''
    buf_size = 32
    while True:
        buf = client.recv(buf_size)
        data += buf
        if b"\r\n" in data:
            break
        elif not data:
            break

    return data


def http_main():

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = ("0.0.0.0", 8000)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, NOLINGER)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, TIMEOUT_VAL)
    sock.setblocking(True)
    sock.bind(addr)
    sock.listen()

    print("Waiting for connection...")
    while True:
        try:
            client, address = sock.accept()
            print("Connection from {}:{}".format(*address))
            secret = client.recv(128)
            device_uuid = str(uuid.uuid3(NAMESPACE, str(secret)))
            print("UUID:", device_uuid)
            client.send(bytes(device_uuid, "UTF-8"))
        except BlockingIOError:
            continue

        try:
            while True:
                data = read_data(client)
                if not data:
                    break
                print("CLIENT:", str(data, "UTF-8").strip())

        except (BlockingIOError, TimeoutError):
            print("Client disconnected")


def main():
    # mqtt_main()
    http_main()


if __name__ == "__main__":
    main()
