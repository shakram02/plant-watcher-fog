
class EdgeUpdate(object):
    def __init__(self, uuid, timestamp, temp, dht_temp, dht_humidity):
        self.uuid = uuid
        self.timestamp = timestamp
        self.temp = temp
        self.dht_temp = dht_temp
        self.dht_humidity = dht_humidity

    def __str__(self) -> str:
        buffer = f"[{self.timestamp}] "
        if self.temp:
            buffer += f"Soil Temp:{self.temp}°C "
        if self.dht_temp:
            buffer += f"Air Temp:{self.dht_temp}°C "
        if self.dht_humidity:
            buffer += f"Air Humidity:{self.dht_humidity}°C "

        return buffer


def as_edge_update(msg_dict: dict):
    update_uuid = msg_dict.get("uuid")
    timestamp = msg_dict.get("epoch")
    temp = msg_dict.get("temp")
    dht_temp = msg_dict.get("dhtT")
    dht_humidity = msg_dict.get("dhtH")

    return EdgeUpdate(update_uuid, timestamp, temp, dht_temp, dht_humidity)
