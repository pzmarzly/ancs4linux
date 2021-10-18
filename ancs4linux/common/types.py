from dataclasses import dataclass
import json


@dataclass
class NewNotification:
    id: int
    title: str
    description: str

    def to_json(self):
        return json.dumps(
            {"id": self.id, "title": self.title, "description": self.description}
        )

    @classmethod
    def from_json(cls, json):
        json = json.loads(json)
        return cls(id=json["id"], title=json["title"], description=json["description"])
