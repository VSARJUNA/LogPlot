import pandas as pd

class MYDS:
    def __init__(self):
        self.df = pd.DataFrame()

    def parse(self, lines):
        data = []
        for line in lines:
            parts = line.strip().split(maxsplit=4)
            if len(parts) < 5:
                continue
            timestamp, module, process, message = parts[:4]
            attributes = self.parse_attributes(parts[4])
            row = {'timestamp': timestamp, 'module': module, 'process': process, 'message': message, **attributes}
            data.append(row)

        self.df = pd.DataFrame(data)

    def parse_attributes(self, attribute_str):
        attributes = {}
        for attr in attribute_str.split(','):
            key_value = attr.split(':')
            if len(key_value) == 2:
                attributes[key_value[0].strip()] = key_value[1].strip()
        return attributes

def initialize(path):
    with open(path, "r") as file:
        lines = file.readlines()
    ds = MYDS()
    ds.parse(lines)
    return ds
