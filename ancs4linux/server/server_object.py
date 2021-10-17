from dasbus.typing import Str
from dasbus.server.interface import dbus_interface


@dbus_interface("org.example.HelloWorld")
class ServerObject(object):
    def Hello(self, name: Str) -> Str:
        return "Hello {}!".format(name)
