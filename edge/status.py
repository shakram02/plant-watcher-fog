from json.encoder import JSONEncoder


class EdgeUpdate(object):
    """
        Represents a snapshot of the readings from
        the sensing node.
    """

    def __init__(self, uuid, timestamp, temp, dht_temp, dht_humidity):
        self.uuid = uuid
        self.timestamp = timestamp
        self.temp = temp
        self.humidity = None
        self.dht_temp = dht_temp
        self.dht_humidity = dht_humidity

    def __str__(self) -> str:
        buffer = ""
        if self.temp:
            buffer += f"Soil Temp:{self.temp}°C "
        if self.dht_temp:
            buffer += f"Air Temp:{self.dht_temp}°C "
        if self.dht_humidity:
            buffer += f"Air Humidity:{self.dht_humidity}%"

        return buffer


def as_edge_update(msg_dict: dict):
    update_uuid = msg_dict.get("uuid")
    timestamp = msg_dict.get("epoch")
    temp = msg_dict.get("temp")
    dht_temp = msg_dict.get("dhtT")
    dht_humidity = msg_dict.get("dhtH")

    return EdgeUpdate(update_uuid, timestamp, temp, dht_temp, dht_humidity)


class EdgeUpdateEncoder(JSONEncoder):
    def default(self, update: EdgeUpdate):
        if not isinstance(update, EdgeUpdate):
            return JSONEncoder.default(self, update)

        json_obj = {}
        air_json = self.encode_dht(update)
        if air_json:
            json_obj["air"] = air_json

        soil_json = self.encode_soil(update)
        if soil_json:
            json_obj["soil"] = soil_json

        if not (air_json or soil_json):
            return None

        node_json = {}
        node_json["data"] = json_obj
        node_json["timestamp"] = update.timestamp
        node_json["uuid"] = update.uuid
        return node_json

    def encode_dht(self, update: EdgeUpdate):
        if not (update.dht_temp or update.dht_humidity):
            return

        air = {}
        if update.dht_humidity:
            air["humidity"] = update.dht_humidity
        if update.dht_temp:
            air["temp"] = update.dht_temp

        return air

    def encode_soil(self, update: EdgeUpdate):
        if not (update.temp or update.humidity):
            return

        soil = {}
        if update.humidity:
            soil["humidity"] = update.humidity
        if update.temp:
            soil["temp"] = update.temp

        return soil
