import matplotlib.pyplot as plt
import numpy as np
import mplcursors
import re

class MYNODE:
    def __init__(self, name="none", timestamp="", parent=None):
        self.name = name
        self.timestamp = timestamp
        self.parent = parent
        self.attributes = {}
        if parent:
            self.attributes.update({'parent_' + k: v for k, v in parent.attributes.items()})

    def set_attributes(self, **attributes):
        self.attributes.update(attributes)

    def get_parent_attributes(self):
        return self.parent.attributes if self.parent else {}

    def __str__(self):
        indent = '-' * len(self.get_parent_list())
        return f"{indent}>{self.name} ({self.timestamp})\n{' ' * (len(indent) + 2)}{self.attributes}"

    def get_parent_list(self):
        node, parents = self, []
        while node.parent:
            parents.append(node.parent)
            node = node.parent
        return parents[::-1]

class MYDS:
    def __init__(self):
        self.lookup = {}
        self.MIN = 0
        self.MAX = 0

    def parse(self, lines):
        parent_stack = []
        start = 0
        for line in lines:
            if '\t' not in line:
                continue

            parts = line.split('\t')
            pre_message_parts = parts[0].split()
            timestamp = pre_message_parts[0][:-1]
            if start == 0:
                self.MIN = timestamp
                start = 1
            message_type = parts[1].split('(')[0].strip()

            attributes_str = parts[1].split('(', 1)[1][:-1] if '(' in parts[1] else ''
            message_name = message_type

            key = message_type
            current_node = MYNODE(message_name, timestamp, parent_stack[-1] if parent_stack else None)
            current_node.set_attributes(**self._parse_attributes(attributes_str))

            if key not in self.lookup:
                self.lookup[key] = []
            self.lookup[key].append((timestamp, current_node))

            if message_type.endswith("_START"):
                parent_stack.append(current_node)
            elif message_type.endswith("_END") and parent_stack:
                parent_stack.pop()
        self.MAX = timestamp

    def _parse_attributes(self, attributes_str):
        attributes = {}
        for attr in attributes_str.split(','):
            if ':' in attr:
                key, value = attr.split(':', 1)
                key = key.strip()
                value = value.strip()
                try:
                    if value.startswith('0x'):
                        attributes[key] = int(value, 16)
                    else:
                        attributes[key] = int(value)
                except ValueError:
                    try:
                        attributes[key] = float(value)
                    except ValueError:
                        attributes[key] = value
        return attributes

def parse_command(command):
    pattern = r"Plot (all|[\w,]+) x=(\w+|default) y=(\w+)(?: from=(\S+) to=(\S+))?(?: __att\[(\w+)\]=(\w+))?(?: p__att\[(\w+)\]=(\w+))?"
    match = re.match(pattern, command)
    if match:
        types, x_attr, y_attr, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value = match.groups()
        types = types.split(',') if types != 'all' else 'all'
        x_attr = None if x_attr == 'default' else x_attr
        return (types, x_attr, y_attr, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value)
    return None
def data_parser(command):
    pattern = r"Plot (all|[\w,]+) x=(\w+|default) to=(\S+))?(?: __att\[(\w+)\]=(\w+))?(?: p__att\[(\w+)\]=(\w+))?"
    match = re.match(pattern,command)
    if match:
        types, x_attr, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value = match.groups()
        types = types.split(',') if types != 'all' else 'all'
        x_attr = None if x_attr == 'default' else x_attr
        return (types, x_attr, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value)




def filter_nodes(dataset, types, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value):
    filtered_nodes = []
    for log_type, node_list in dataset.lookup.items():
        if types != 'all' and log_type not in types:
            continue
        for timestamp, node in node_list:
            if start_time and timestamp < start_time or end_time and timestamp > end_time:
                continue
            # Directly using detailed node information in filtering
            if filter_key and str(node.attributes.get(filter_key)) != str(filter_value):
                continue
            # Checking parent attribute directly in the filter condition
            if parent_filter_key and str(node.parent.attributes.get(parent_filter_key)) != str(parent_filter_value):
                continue
            # All conditions passed, add node to filtered list
            filtered_nodes.append(node)
    return filtered_nodes



def prepare_plot_data(nodes, x_attr, y_attr):
    # Simplify data preparation using filtered nodes
    x_data = [getattr(node, x_attr, node.timestamp) for node in nodes] if x_attr else [node.timestamp for node in nodes]
    y_data = [node.attributes.get(y_attr, 'N/B') for node in nodes]
    # Gather info for annotations directly here for efficiency
    node_info = [{'line_number': idx + 1, 'x': x_data[idx], 'y': y_data[idx], 'attributes': node.attributes, 'parent_attributes': node.parent.attributes if node.parent else {}} for idx, node in enumerate(nodes)]
    return(x_data,y_data,node_info)
def prepare_get_data(nodes,x_attr):
    x_data = [getattr(node, x_attr, node.timestamp) for node in nodes] if x_attr else [node.timestamp for node in nodes]
    return(x_data)

def plot_data(x_data, y_data, node_info, x_attr=None, y_attr=None, max_points=10000):
    try:
        y_data = [int(i) for i in y_data]
    except:
        pass
    if len(x_data) > max_points:
        indices = np.linspace(0, len(x_data) - 1, max_points).astype(int)
        x_data = np.array(x_data)[indices]
        y_data = np.array(y_data)[indices]
        node_info = [node_info[i] for i in indices]

    plt.figure(figsize=(15, 10))

    scatter = plt.scatter(x_data, y_data, s=20)
    plt.title(f"Plot of {y_attr} vs {x_attr or 'Timestamp'}", fontsize=14)
    plt.xlabel(x_attr or "Timestamp", fontsize=12)
    plt.ylabel(y_attr, fontsize=12)
    plt.grid(True)

    cursor = mplcursors.cursor(scatter, hover=True)

    @cursor.connect("add")
    def on_add(sel):
        idx = sel.index
        info = node_info[idx]
        parent_attr_text = f'Parent Attributes: {info["parent_attributes"]}' if info["parent_attributes"] else "No Parent"
        sel.annotation.set(text=f'Line: {info["line_number"]}\nX: {info["x"]}\nY: {info["y"]}\nAttributes: {info["attributes"]}\n{parent_attr_text}', fontsize=9, bbox=dict(facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.show()

def main(command):
    parsed = parse_command(command)
    if not parsed:
        print("Invalid command format.")
        return
    types, x_attr, y_attr, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value = parsed

    nodes = filter_nodes(dataset, types, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value)
    x_data, y_data, node_info = prepare_plot_data(nodes, x_attr, y_attr)
    plot_data(x_data, y_data, node_info, x_attr, y_attr)
def get(command):
    parsed =data_parser(command)
    if not parsed:
        print("invalid command formart.")
        return
    types, x_attr, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value = parsed
    nodes = filter_nodes(dataset, types, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value)
    x_data= prepare_get_data(nodes, x_attr)
    return(x_data)


dataset = MYDS()
def initialize(path):
    try:
        with open(path, "r") as file:
            lines = file.readlines()
        dataset.parse(lines)
    except Exception as e:
        print(f"An error occurred: {e}")
