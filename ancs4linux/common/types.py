from dataclasses import dataclass
import json


@dataclass
class ShowNotificationData:
    device_address: str
    device_name: str
    id: int
    title: str
    body: str

    def to_json(self) -> str:
        return json.dumps(vars(self))

    @classmethod
    def from_json(cls, data: str) -> "ShowNotificationData":
        return cls(**json.loads(data))
