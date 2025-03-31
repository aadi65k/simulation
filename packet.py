import json

class Packet:
    def __init__(self, data: str):
        self.data = data

    def encode(self) -> bytes:
        """Encode the packet data into bytes."""
        return json.dumps({"data": self.data}).encode()

    @staticmethod
    def decode(encoded_data: bytes) -> str:
        """Decode the packet data from bytes."""
        try:
            data = json.loads(encoded_data.decode())
            return data["data"]
        except Exception:
            return None
