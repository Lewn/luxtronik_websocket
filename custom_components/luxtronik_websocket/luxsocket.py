"""Simple websocket communication with a Luxtronik heat pump."""

from defusedxml.minidom import parseString
from websockets.client import connect


class LuxSocket:
    """Main class."""

    def __init__(self, host: str, port: str = "8214", password: str = "") -> None:
        """Initialize the class."""
        self.host = host
        self.port = port
        self.password = password
        self.data = None

    @property
    def headers(self):
        """Return the headers needed to connect."""
        return {
            "uri": f"ws://{self.host}:{self.port}",
            "subprotocols": ["Lux_WS"],
        }

    async def test_connection(self):
        """Test the connection to the heatpump."""
        try:
            await self.get_data()
            return True
        except:  # noqa: E722
            return False

    async def get_data(self):
        """Retrieve data from the heatpump."""
        self.data = {}
        async with connect(**self.headers) as websocket:
            await websocket.send(f"LOGIN;{self.password}")
            result = await websocket.recv()
            navigation = parseString(result).firstChild
            assert navigation.tagName == "Navigation"
            for item in navigation.childNodes:
                itemid = item.getAttribute("id")
                itemname = item.getElementsByTagName("name")[0].firstChild.nodeValue

                await websocket.send(f"GET;{itemid}")
                result = await websocket.recv()
                content = parseString(result).firstChild
                assert content.tagName == "Content"

                for elem in content.getElementsByTagName("value"):
                    if elem.firstChild is None or elem.firstChild.nodeValue is None:
                        continue

                    value = elem.firstChild.nodeValue
                    key = []
                    while (elem := elem.parentNode).tagName == "item":
                        elemname = elem.getElementsByTagName("name")[
                            0
                        ].firstChild.nodeValue
                        key.append(elemname)
                    key.append(itemname)

                    key = "_".join(reversed(key)).replace(" ", "-")

                    self.data[key] = value


async def main():
    """Test main funtion."""
    luxSocket = LuxSocket("192.168.6.157")
    await luxSocket.get_data()
    for key, value in luxSocket.data.items():
        print(f"{key:.<80s}{value}")  # noqa: T201


if __name__ == "__main__":
    import asyncio
    import logging

    logging.basicConfig(
        format="%(message)s",
        level=logging.DEBUG,
    )

    asyncio.run(main())
