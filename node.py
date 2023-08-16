from typing import TypedDict


class Node:
    def __init__(self, name: str, uri: str):
        self.name = name
        self.uri = uri

    def from_string(self, nameuri: str):
        return Node(*nameuri.split("|"))

    def __str__(self):
        return self.name + "|" + self.uri
