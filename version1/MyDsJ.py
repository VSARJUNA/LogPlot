import json
import re

class MYNODE:
    def __init__(self, name="", timestamp="", attributes=None):
        self.name = name
        self.timestamp = timestamp
        self.attributes = attributes if attributes is not None else {}

class MYDS:
    def __init__(self):
        self.nodes = []

    def parse(self, lines):
        for line in lines:
            parts = line.strip().split(maxsplit=4)
            if len(parts) < 5:
                continue
            timestamp, module, process, message = parts[:4]
            attributes = self.fake_json_to_dict(parts[4])
            node = MYNODE(name=message, timestamp=timestamp, attributes=attributes)
            self.nodes.append(node)

    def fake_json_to_dict(self, text):
        # Convert text data into a dictionary assuming simple 'key: value' pairs
        attr_dict = {}
        for attr in text.split(','):
            if ':' in attr:
                key, value = attr.split(':', 1)
                attr_dict[key.strip()] = value.strip()
        return attr_dict

def initialize(path):
    with open(path, "r") as file:
        lines = file.readlines()
    ds = MYDS()
    ds.parse(lines)
    return ds
