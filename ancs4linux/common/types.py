from pydantic import BaseModel


class ShowNotificationData(BaseModel):
    device_address: str
    device_name: str
    id: int
    title: str
    body: str
