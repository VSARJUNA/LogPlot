import matplotlib.pyplot as plt
import numpy as np
import mplcursors
import re
def runScript(x_data, y_data, script):
    # Define a local dictionary to store the variables
    local_vars = {'x_data': x_data, 'y_data': y_data}
    
    # Use exec to run the script within the local_vars dictionary
    exec(script, {}, local_vars)
    
    # Return the updated x_data and y_data
    return local_vars['x_data'], local_vars['y_data']

# MYNODE class represents a node in the log structure
class MYNODE:
    """
    MYNODE class represents a node in the log structure. Each node may have a parent,
    a name, timestamp, and a set of attributes. Nodes are part of a hierarchical log structure.

    Attributes:
    -----------
    name : str
        Name of the node (e.g., message type).
    timestamp : str
        The timestamp associated with the node.
    parent : MYNODE
        Reference to the parent node in the hierarchy (if any).
    attributes : dict
        A dictionary of attributes for the node, including inherited parent attributes.
    """
    def __init__(self, name="none", timestamp="", parent=None):
        """
        Initializes a new node with a name, timestamp, and optional parent.
        Inherits attributes from the parent node.

        Parameters:
        -----------
        name : str
            The name of the node (e.g., message type).
        timestamp : str
            The timestamp of the node.
        parent : MYNODE
            The parent node reference (if applicable).
        """
        self.name = name  # Name of the node
        self.timestamp = timestamp  # Timestamp of the node
        self.parent = parent  # Reference to the parent node
        self.attributes = {}  # Node's attributes
        if parent:
            # Inherit parent attributes and prefix them with 'parent_'
            self.attributes.update({'parent_' + k: v for k, v in parent.attributes.items()})

    # Method to set attributes of the node
    def set_attributes(self, **attributes):
        """
        Sets or updates the attributes of the node.

        Parameters:
        -----------
        attributes : dict
            A dictionary of attribute key-value pairs to set for the node.
        """
        self.attributes.update(attributes)

    # Get attributes of the parent node if it exists
    def get_parent_attributes(self):
        """
        Returns the attributes of the parent node, if it exists.

        Returns:
        --------
        dict or None
            Returns the parent's attributes if the parent node exists, otherwise returns None.
        """
        return self.parent.attributes if self.parent else {}

    # Return a string representation of the node
    def __str__(self):
        """
        Returns a formatted string representation of the node, including its name, timestamp,
        and attributes. Parent nodes are represented as indentation.

        Returns:
        --------
        str
            A formatted string representing the node and its attributes.
        """
        indent = '-' * len(self.get_parent_list())  # Indentation based on parent hierarchy
        return f"{indent}>{self.name} ({self.timestamp})\n{' ' * (len(indent) + 2)}{self.attributes}"

    # Return a list of parent nodes up the hierarchy
    def get_parent_list(self):
        """
        Constructs a list of parent nodes up the hierarchy.

        Returns:
        --------
        list
            A list of parent nodes in reverse order (from root to the current node).
        """
        node, parents = self, []
        while node.parent:
            parents.append(node.parent)
            node = node.parent
        return parents[::-1]

# MYDS class represents the dataset and parsing logic
class MYDS:
    """
    MYDS class represents the dataset of nodes parsed from a log file. It includes
    methods to parse the log lines, manage node hierarchy, and store the nodes.

    Attributes:
    -----------
    lookup : dict
        A dictionary storing nodes categorized by message type.
    MIN : str
        The minimum timestamp in the dataset.
    MAX : str
        The maximum timestamp in the dataset.
    """
    def __init__(self):
        """
        Initializes the MYDS dataset with an empty lookup dictionary and default
        minimum and maximum timestamps.
        """
        self.lookup = {}  # Dictionary for storing nodes based on message type
        self.MIN = 0  # Minimum timestamp
        self.MAX = 0  # Maximum timestamp
        self.times=None

    # Parse log lines and populate the dataset
    def parse(self, lines):
        """
        Parses log lines and creates nodes for each log entry, storing them
        in the dataset. Manages the hierarchy of nodes based on message type
        (e.g., _START and _END markers).

        Parameters:
        -----------
        lines : list
            A list of log lines to be parsed.
        """
        parent_stack = []  # Stack to track parent nodes
        start = 0
        for line in lines:
            if '\t' not in line:  # Skip lines without tabs
                continue

            parts = line.split('\t')
            pre_message_parts = parts[0].split()
            timestamp = pre_message_parts[0][:-1]  # Extract timestamp
            if start == 0:
                self.MIN = timestamp  # Set MIN timestamp on first iteration
                start = 1
            message_type = parts[1].split('(')[0].strip()  # Extract message type

            # Extract attributes from the message part
            attributes_str = parts[1].split('(', 1)[1][:-1] if '(' in parts[1] else ''
            message_name = message_type

            # Create a new node and set its attributes
            key = message_type
            current_node = MYNODE(message_name, timestamp, parent_stack[-1] if parent_stack else None)
            current_node.set_attributes(**self._parse_attributes(attributes_str))

            if key not in self.lookup:
                self.lookup[key] = []
            self.lookup[key].append((timestamp, current_node))

            # Track start and end of node hierarchy
            if message_type.endswith("_START"):
                parent_stack.append(current_node)
            elif message_type.endswith("_END") and parent_stack:
                parent_stack.pop()
        self.MAX = timestamp  # Set MAX timestamp

    # Helper function to parse attributes from a string
    def _parse_attributes(self, attributes_str):
        """
        Helper function to parse the attributes string and convert it into a dictionary.

        Parameters:
        -----------
        attributes_str : str
            The raw attributes string extracted from the log entry.

        Returns:
        --------
        dict
            A dictionary of parsed attribute key-value pairs.
        """
        attributes = {}
        for attr in attributes_str.split(','):
            if ':' in attr:
                key, value = attr.split(':', 1)
                key = key.strip()
                value = value.strip()
                try:
                    if value.startswith('0x'):
                        attributes[key] = int(value, 16)  # Parse hex value
                    else:
                        attributes[key] = int(value)  # Parse integer
                except ValueError:
                    try:
                        attributes[key] = float(value)  # Parse float
                    except ValueError:
                        attributes[key] = value  # Store as string if parsing fails
        return attributes

# Function to parse plot commands from strings
def parse_command(command):
    """
    Parses a plot command string and extracts the plotting parameters.

    Parameters:
    -----------
    command : str
        The plot command string to be parsed.

    Returns:
    --------
    tuple or None
        Returns a tuple of extracted parameters (types, x_attr, y_attr, etc.) or None if parsing fails.
    """
    pattern = r"Plot (all|[\w,]+) x=(\w+|default) y=(\w+)(?: from=(\S+) to=(\S+))?(?: __att\[(\w+)\]=(\w+))?(?: p__att\[(\w+)\]=(\w+))?"
    match = re.match(pattern, command)
    if match:
        types, x_attr, y_attr, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value = match.groups()
        types = types.split(',') if types != 'all' else 'all'
        x_attr = None if x_attr == 'default' else x_attr
        return (types, x_attr, y_attr, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value)
    return None

# Alternate parser function for handling data commands
def data_parser(command):
    """
    Parses data commands and extracts the required parameters for data processing.

    Parameters:
    -----------
    command : str
        The command string for data processing.

    Returns:
    --------
    tuple or None
        Returns a tuple of extracted parameters or None if parsing fails.
    """
    pattern = r"Plot (all|[\w,]+) x=(\w+|default) y=(\w+)(?: from=(\S+) to=(\S+))?(?: __att\[(\w+)\]=(\w+))?(?: p__att\[(\w+)\]=(\w+))?"
    match = re.match(pattern, command)
    if match:
        types, x_attr, y_attr, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value = match.groups()
        types = types.split(',') if types != 'all' else 'all'
        x_attr = None if x_attr == 'default' else x_attr
        return (types, x_attr, y_attr, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value)
    return None

# Filter nodes based on command parameters
def filter_nodes(dataset, types, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value):
    """
    Filters nodes from the dataset based on the provided parameters such as type, 
    time range, and attribute filters.

    Parameters:
    -----------
    dataset : MYDS
        The dataset to filter nodes from.
    types : list or str
        The list of message types to filter (or 'all' for no type filtering).
    start_time : str
        The starting time for the filter.
    end_time : str
        The ending time for the filter.
    filter_key : str
        The attribute key to filter by.
    filter_value : str
        The attribute value to filter by.
    parent_filter_key : str
        The parent attribute key to filter by.
    parent_filter_value : str
        The parent attribute value to filter by.

    Returns:
    --------
    list
        A list of filtered nodes that match the filter criteria.
    """
    filtered_nodes = []
    for log_type, node_list in dataset.lookup.items():
        if types != 'all' and log_type not in types:
            continue
        for timestamp, node in node_list:
            if start_time and timestamp < start_time or end_time and timestamp > end_time:
                continue
            # Apply filters based on attributes
            if filter_key and str(node.attributes.get(filter_key)) != str(filter_value):
                continue
            filtered_nodes.append(node)
    return filtered_nodes

# Prepare data for plotting
def prepare_plot_data(nodes, x_attr, y_attr):
    """
    Prepares the X and Y data for plotting along with node information.

    Parameters:
    -----------
    nodes : list
        A list of filtered nodes to be plotted.
    x_attr : str
        The attribute for the X axis (or None for timestamp).
    y_attr : str
        The attribute for the Y axis.

    Returns:
    --------
    tuple
        Returns a tuple containing X data, Y data, and node information for annotation.
    """
    x_data = [getattr(node, x_attr, node.timestamp) for node in nodes] if x_attr else [node.timestamp for node in nodes]
    y_data = [node.attributes.get(y_attr, 'N/B') for node in nodes]
    node_info = [{'line_number': idx + 1, 'x': x_data[idx], 'y': y_data[idx], 'attributes': node.attributes, 'parent_attributes': node.parent.attributes if node.parent else {}} for idx, node in enumerate(nodes)]
    return (x_data, y_data, node_info)

# Prepare y_data for get function
def prepare_get_data(nodes, x_attr, y_attr):
    """
    Prepares the Y data for fetching based on filtered nodes and attributes.

    Parameters:
    -----------
    nodes : list
        A list of filtered nodes to process.
    x_attr : str
        The attribute for the X axis (or None for timestamp).
    y_attr : str
        The attribute for the Y axis.

    Returns:
    --------
    list
        A list of Y values extracted from the node attributes.
    """
    x_data = [getattr(node, x_attr, node.timestamp) for node in nodes] if x_attr else [node.timestamp for node in nodes]
    y_data = [node.attributes.get(y_attr, 'N/B') for node in nodes]
    node_info = [{'line_number': idx + 1, 'x': x_data[idx], 'y': y_data[idx], 'attributes': node.attributes, 'parent_attributes': node.parent.attributes if node.parent else {}} for idx, node in enumerate(nodes)]
    return y_data

# Plot data using matplotlib
def plot_data(x_data, y_data, node_info, x_attr=None, y_attr=None, max_points=10000):
    """
    Plots the data using matplotlib, with optional interaction using mplcursors for annotation.

    Parameters:
    -----------
    x_data : list
        The X axis data for plotting.
    y_data : list
        The Y axis data for plotting.
    node_info : list
        A list of dictionaries containing node information for annotation.
    x_attr : str, optional
        The attribute for the X axis (default is timestamp).
    y_attr : str
        The attribute for the Y axis.
    max_points : int, optional
        Maximum number of points to display (default is 10,000).
    """
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

    # Cursor for showing node information on hover
    cursor = mplcursors.cursor(scatter, hover=True)

    @cursor.connect("add")
    def on_add(sel):
        """
        Display node information when hovering over data points.
        """
        idx = sel.index
        info = node_info[idx]
        parent_attr_text = f'Parent Attributes: {info["parent_attributes"]}' if info["parent_attributes"] else "No Parent"
        sel.annotation.set(text=f'Line: {info["line_number"]}\nX: {info["x"]}\nY: {info["y"]}\nAttributes: {info["attributes"]}\n{parent_attr_text}', fontsize=9, bbox=dict(facecolor='white', alpha=0.8))

    plt.show()

# Main function to execute a plot command
def main(command,script=None):
    """
    Main function to execute a plot command. Parses the command, filters the dataset, and plots the data.

    Parameters:
    -----------
    command : str
        The plot command string to be executed.
    """
    parsed = parse_command(command)
    if not parsed:
        print("Invalid command format.")
        return
    types, x_attr, y_attr, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value = parsed

    # Filter and plot data
    nodes = filter_nodes(dataset, types, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value)
    x_data, y_data, node_info = prepare_plot_data(nodes, x_attr, y_attr)
    if(script!=None):
        x_data,y_data=runScript(x_data,y_data,script)
    plot_data(x_data, y_data, node_info, x_attr, y_attr)

# Function to get data based on command
def get(command):
    """
    Retrieves data based on the provided command. Filters nodes and returns the Y data.

    Parameters:
    -----------
    command : str
        The command string for fetching data.

    Returns:
    --------
    list
        A list of Y data values from the filtered nodes.
    """
    parsed = data_parser(command)
    if not parsed:
        print("Invalid command format.")
        return
    types, x_attr, y_attr, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value = parsed
    nodes = filter_nodes(dataset, types, start_time, end_time, filter_key, filter_value, parent_filter_key, parent_filter_value)
    y_data = prepare_get_data(nodes, x_attr, y_attr)
    return y_data

# Initialize dataset by reading a log file
dataset = MYDS()

# Function to initialize dataset from a file
def initialize(path):
    """
    Initializes the dataset by reading log lines from the specified file.

    Parameters:
    -----------
    path : str
        The file path of the log file to read and parse.
    """
    dataset.lookup = {}  # Dictionary for storing nodes based on message type
    dataset.MIN = 0  # Minimum timestamp
    dataset.MAX = 0  # Maximum timestamp
    dataset.times=None
    try:
        with open(path, "r") as file:
            lines = file.readlines()
        dataset.parse(lines)
    except Exception as e:
        print(f"An error occurred: {e}")
