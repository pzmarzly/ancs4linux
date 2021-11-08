from dataclasses import dataclass
import json


@dataclass
class ShowNotificationData:
    device_address: str
    device_name: str
    id: int
    title: str
    body: str

    def to_json(self):
        return json.dumps(vars(self))

    @classmethod
    def from_json(cls, json):
        return cls(**json.loads(json))
