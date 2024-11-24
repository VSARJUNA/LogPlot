import sys, os
from PySide6.QtCore import QCoreApplication
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QGraphicsScene

from PySide6.QtWidgets import QFileDialog, QProgressDialog
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QInputDialog, QSplitter, QTextEdit, QPushButton, QVBoxLayout, QPlainTextEdit, QWidget, QLabel, QCompleter, QDialogButtonBox, QMenu, QFormLayout, QLineEdit, QMessageBox, QDialog
from PySide6.QtGui import QAction, QTextCursor, QTransform, QPixmap
from PySide6.QtCore import Qt, QThread, Signal, QStringListModel, QSortFilterProxyModel, QRect
from datetime import datetime
import pandas as pd
import MyDs  # Custom data structure module (likely a utility module for data management)
from ui_form import Ui_Widget  # Auto-generated UI class from Qt Designer for the main window
from ui_scriptdialog import Ui_Dialog  # Auto-generated UI class from Qt Designer for the script dialog

# This class handles rotating images in a separate thread to allow for smooth animation
from PySide6.QtCore import QThread, Signal

class WorkerThread(QThread):
    progress = Signal(int)  # Signal to send progress updates
    finished = Signal()  # Signal to indicate task completion

    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name

    def run(self):
        """
        This is the code that runs in the background thread.
        """
        # Simulate long-running initialization (replace with MyDs.initialize)
        MyDs.initialize(self.file_name)

        # Emit progress periodically if applicable (this is just a simulation)
        for i in range(1, 101):
            self.msleep(100)  # Simulate work
            self.progress.emit(i)  # Emit progress signal

        self.finished.emit()  # Emit a signal when done

class RotateThread(QThread):
    """
    RotateThread is a QThread responsible for rotating an image.
    It updates the image at a set interval and emits the rotated image
    via the 'rotated' signal to update the UI in real-time.

    Attributes:
    -----------
    pixmap : QPixmap
        The image to be rotated (as a QPixmap object).
    angle : int
        The current rotation angle for the image.
    _is_running : bool
        A boolean flag to indicate whether the thread should keep running.
    
    Signals:
    --------
    rotated : Signal(QPixmap)
        Emitted when a new rotated pixmap is ready to be displayed in the UI.
    """
    rotated = Signal(QPixmap)  # Signal to send the rotated image to the main UI

    def __init__(self, pixmap):
        """
        Constructor to initialize RotateThread with a given pixmap (image).

        Parameters:
        -----------
        pixmap : QPixmap
            The image that needs to be rotated periodically.
        """
        super().__init__()
        self.pixmap = pixmap  # Store the original pixmap
        self.angle = 0  # Initialize the angle to 0
        self._is_running = True  # Set the running flag to True so the thread can start

    def run(self):
        """
        The main function that runs in the thread. It keeps rotating the image
        at a fixed angle increment (12 degrees) and emits the rotated image at intervals.
        """
        while self._is_running:
            self.angle = (self.angle + 12) % 360  # Increase the angle by 12 degrees each cycle
            rotated_pixmap = self.pixmap.transformed(QTransform().rotate(self.angle))  # Rotate the image
            self.rotated.emit(rotated_pixmap)  # Emit the rotated image to update the UI
            self.msleep(50)  # Sleep for 50 milliseconds to control the speed of rotation

    def stop(self):
        """
        This method stops the rotation by setting the _is_running flag to False.
        """
        self._is_running = False  # Set the flag to stop the thread


# A window that prompts the user to input various fields to create a plot (graph)
class PromptWindow(QWidget):
    """
    PromptWindow handles user inputs for plotting data, allowing the user to set
    time ranges, data types, axes, and advanced filters.

    Attributes:
    -----------
    starttime_input : QLineEdit
        Input field where users enter the start time for the plot.
    endtime_input : QLineEdit
        Input field where users enter the end time for the plot.
    TypesBox : QLineEdit
        Input field for selecting the log type (with auto-completion).
    XBox : QLineEdit
        Input field for selecting the data for the X-axis.
    YBox : QLineEdit
        Input field for selecting the data for the Y-axis.
    filter_input : QLineEdit
        Input field for specifying advanced filter conditions (initially hidden).
    advanced_label : QLabel
        A clickable label to show/hide advanced options.
    ok_button : QPushButton
        A button to confirm the plot request and pass the inputs back to the main window.
    cancel_button : QPushButton
        A button to cancel and close the input window.
    """
    def __init__(self):
        """
        Initializes the PromptWindow by creating all the input fields and layout.
        """
        super().__init__()

        # Set up window properties
        self.setWindowTitle("Prompt Window")
        self.setFixedSize(400, 300)  # Set a fixed size for the window

        layout = QFormLayout()  # Use a form layout to arrange labels and input fields

        # Create input field for the start time and add it to the layout
        self.starttime_input = QLineEdit(self)
        layout.addRow("Start_Time", self.starttime_input)

        # Create input field for the end time and add it to the layout
        self.endtime_input = QLineEdit(self)
        layout.addRow("End_Time", self.endtime_input)

        # Type input with auto-completion
        self.TypesBox = QLineEdit(self)
        self.Typecompleter = SubstringCompleter(list(MyDs.dataset.lookup.keys()), self)  # Auto-complete based on dataset keys
        self.TypesBox.setCompleter(self.Typecompleter)
        self.TypesBox.returnPressed.connect(self.selectType)  # Connect to method for filling X and Y axis suggestions
        layout.addRow("Type", self.TypesBox)

        # Create input fields for X and Y axes, add them to the layout
        self.XBox = QLineEdit(self)
        layout.addRow("X", self.XBox)

        self.YBox = QLineEdit(self)
        layout.addRow("Y", self.YBox)

        # Add an "Advanced" label that acts as a clickable toggle to show/hide additional filter options
        self.advanced_label = QLabel("Advanced")
        self.advanced_label.setStyleSheet("color: blue; text-decoration: underline; cursor: pointer;")  # Style to indicate it's clickable
        self.advanced_label.mousePressEvent = self.toggle_advanced_section  # When clicked, show/hide advanced section
        layout.addRow(self.advanced_label)

        # Advanced section: Initially hidden
        self.filter_label = QLabel("Filter")
        self.filter_input = QLineEdit(self)
        self.filter_label.setVisible(False)  # Hide filter label
        self.filter_input.setVisible(False)  # Hide filter input field
        layout.addRow(self.filter_label, self.filter_input)
        self.script_label = QLabel("Script")
        self.script_label.setVisible(False)
        layout.addRow(self.script_label)
        self.script_view = QTextEdit(self)
        self.script_view.setVisible(False)
        layout.addRow(self.script_view)
        # Add advanced filter section to the layout

        # OK and Cancel buttons
        buttons_layout = QVBoxLayout()  # Layout to hold the OK/Cancel buttons
        self.ok_button = QPushButton("OK")  # Button to confirm and plot
        self.ok_button.clicked.connect(self.on_ok_clicked)  # Connect to function that handles OK click
        self.cancel_button = QPushButton("Cancel")  # Button to cancel and close the window
        self.cancel_button.clicked.connect(self.on_cancel_clicked)  # Connect to function that handles Cancel click
        buttons_layout.addWidget(self.ok_button)  # Add OK button to layout
        buttons_layout.addWidget(self.cancel_button)  # Add Cancel button to layout

        # Add buttons to the form layout
        layout.addRow(buttons_layout)

        # Set the overall layout for the window
        self.setLayout(layout)

    def toggle_advanced_section(self, event):
        """
        Toggles the visibility of the advanced filter section.
        When visible, the window expands in size.
        """
        if not self.filter_input.isVisible():  # If advanced section is currently hidden
            self.setFixedSize(400, 350)  # Expand the window
            self.filter_label.setVisible(True)  # Show filter label
            self.filter_input.setVisible(True)
            self.script_view.setVisible(True)
            self.script_label.setVisible(True)# Show filter input
            self.advanced_label.setText("Advanced ▼")  # Change the label to indicate expanded state
        else:
            self.setFixedSize(400, 300)  # Collapse the window back to its original size
            self.filter_label.setVisible(False)  # Hide filter label
            self.filter_input.setVisible(False)
            self.script_view.setVisible(False)
            self.script_label.setVisible(False)# Hide filter input
            self.advanced_label.setText("Advanced")  # Reset the label text

    def selectType(self):
        """
        Sets up auto-completion for the X and Y axis input fields based on the selected log type.
        When the user selects a type, the corresponding attributes are fetched from the dataset and added as suggestions.
        """
        self.type = self.TypesBox.text()  # Get the selected type from the input box
        # Set up auto-completion for the X and Y axes based on attributes of the selected type
        self.TypeXcompleter = SubstringCompleter(list(MyDs.dataset.lookup[self.type][0][1].attributes.keys()), self)
        self.XBox.setCompleter(self.TypeXcompleter)
        self.TypeYcompleter = SubstringCompleter(list(MyDs.dataset.lookup[self.type][0][1].attributes.keys()), self)
        self.YBox.setCompleter(self.TypeYcompleter)

    def on_ok_clicked(self):
        """
        Collects the input data from all fields (including advanced filters if visible) and sends them to the main window for plotting.
        """
        # Fetch the entered values from the input fields
        start_time = self.starttime_input.text()
        end_time = self.endtime_input.text()
        log_type = self.TypesBox.text()
        x_axis = self.XBox.text()
        y_axis = self.YBox.text()

        # Fetch filter input if advanced section is visible, otherwise set it to None
        filter_condition = self.filter_input.text() if self.filter_input.isVisible() else None
        script =self.script_view.toPlainText() if self.filter_input.isVisible() else None
        having_attribute = []

        # Parse the filter condition into key-value pairs if it's not empty
        try:
            if filter_condition:
                having_attribute = [(i.split("=")[0], i.split("=")[1]) for i in filter_condition.replace(" ", "").split(",")]
        except:
            pass

        # Call the plot_data function in the main window to handle the plot request
        main_window.plot_data(log_type, start_time, end_time, x_axis, y_axis, having_attribute,script=script)
        self.close()  # Close the prompt window after plotting

    def on_cancel_clicked(self):
        """
        Closes the prompt window when the Cancel button is clicked.
        """
        self.close()


# SubstringCompleter is a custom QCompleter to support substring-based matching, allowing users to search for matches within words
class SubstringCompleter(QCompleter):
    """
    SubstringCompleter extends QCompleter to allow for more flexible matching of items.
    Instead of matching only from the start of the word, it allows matching within any part of the string.

    Attributes:
    -----------
    proxy_model : QSortFilterProxyModel
        A proxy model to filter and sort the suggestions based on user input.
    """
    def __init__(self, words, parent=None):
        """
        Initializes the completer with a list of possible words and sets up filtering.

        Parameters:
        -----------
        words : list
            A list of words that the completer will suggest to the user.
        parent : QWidget (optional)
            The parent widget for the completer.
        """
        super().__init__(words, parent)
        self.setCompletionMode(QCompleter.PopupCompletion)  # Show the popup list of suggestions
        self.setCaseSensitivity(Qt.CaseInsensitive)  # Ignore case while matching
        self.proxy_model = QSortFilterProxyModel(self)  # Set up the proxy model for filtering
        self.proxy_model.setSourceModel(QStringListModel(words))  # Set the source model as a QStringListModel of words
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)  # Make the filtering case-insensitive
        self.setModel(self.proxy_model)  # Set the proxy model as the completer's model
        self.setFilterMode(Qt.MatchContains)  # Match words if they contain the typed substring

    def updateModel(self, completion_prefix):
        """
        Updates the model (list of suggestions) based on the user's input (completion prefix).
        Filters the available suggestions and refreshes the popup.

        Parameters:
        -----------
        completion_prefix : str
            The text entered by the user that needs to be matched against the word list.
        """
        self.proxy_model.setFilterFixedString(completion_prefix)  # Update the filter with the current input
        self.popup().setCurrentIndex(self.proxy_model.index(0, 0))  # Highlight the first suggestion


# FileReaderThread handles reading a log file in chunks in the background to avoid freezing the UI
class FileReaderThread(QThread):
    """
    FileReaderThread reads large log files in chunks to avoid blocking the main thread.
    It processes lines of the file and applies any selected filters, sending updates to the UI in real-time.

    Attributes:
    -----------
    file_name : str
        The name of the file to be read.
    chunk_size : int
        The size of the file chunk to be read at a time.
    lines_per_page : int
        The number of lines to display per page in the UI.
    selected_filters : list
        A list of filters to be applied to the log data.
    filtersflag : bool
        A flag to indicate whether filters are applied.
    current_page : int
        The current page of the log being processed and displayed.
    encountered_types : set
        A set of log types encountered during file reading.

    Signals:
    --------
    update_content : Signal(str)
        Emitted whenever a new line of content is processed.
    update_page : Signal()
        Emitted when a new page of content is ready to be displayed.
    update_types : Signal(set)
        Emitted when new log types are encountered in the data.
    """
    update_content = Signal(str)  # Signal to update content in the UI as lines are read
    update_page = Signal()  # Signal to notify when a new page of content is ready
    update_types = Signal(set)  # Signal to send any new log types found during file reading

    def __init__(self, file_name, chunk_size, lines_per_page, selected_filters, filtersflag, current_page):
        """
        Initializes the FileReaderThread with parameters for reading the file in chunks
        and applying filters to the data.

        Parameters:
        -----------
        file_name : str
            Path to the log file being read.
        chunk_size : int
            Size of the file chunks to read at a time (to avoid memory issues).
        lines_per_page : int
            Number of lines to display per page in the UI.
        selected_filters : list
            Filters selected by the user to apply to the data.
        filtersflag : bool
            Whether filters are currently being applied to the data.
        current_page : int
            The current page of data being displayed in the UI.
        """
        super().__init__()
        self.file_name = file_name
        self.chunk_size = chunk_size
        self.lines_per_page = lines_per_page
        self.selected_filters = selected_filters
        self.filtersflag = filtersflag
        self.current_page = current_page
        self.encountered_types = set()  # Initialize an empty set for log types

    def run(self):
        """
        The main logic for reading the file in chunks. It processes each line and applies
        filters if necessary, updating the UI in real-time.
        """
        try:
            with open(self.file_name, 'r') as file:
                buffer = ""  # Initialize an empty buffer to store file content
                while True:
                    chunk = file.read(self.chunk_size)  # Read a chunk of the file
                    if not chunk:
                        break  # If no more content, exit the loop
                    buffer += chunk
                    if '\n' in buffer:
                        lines = buffer.split('\n')  # Split buffer into lines
                        for line in lines[:-1]:  # Process each line except the last (which may be incomplete)
                            self.process_line(line)
                        buffer = lines[-1]  # Keep the last incomplete line in the buffer for the next chunk
                if buffer:
                    self.process_line(buffer)  # Process the remaining content in the buffer
            self.update_page.emit()  # Emit signal to update the page in the UI
            self.update_types.emit(self.encountered_types)  # Emit any newly encountered log types
        except Exception as e:
            print(e)

    def process_line(self, line):
        """
        Process each line of the log and apply any filters.
        If the line matches the filter conditions, it is sent to the UI for display.

        Parameters:
        -----------
        line : str
            The line of the log being processed.
        """
        try:
            log_type = self.extract_type(line)  # Extract the log type from the line
            if log_type:
                self.encountered_types.add(log_type)  # Add the log type to the set of encountered types

            # Apply filters if any are selected
            if self.filtersflag and log_type in self.selected_filters:
                self.update_content.emit(line)  # Emit the filtered line to the UI
            elif not self.filtersflag:
                self.update_content.emit(line)  # If no filters, emit the line unconditionally
        except Exception as e:
            print(e)

    def extract_type(self, line):
        """
        Extracts the log type from the line of text.
        Assumes the log type is within parentheses in the second tab-delimited section of the line.

        Parameters:
        -----------
        line : str
            The line of log data to extract the type from.

        Returns:
        --------
        str or None
            Returns the extracted log type, or None if no type could be found.
        """
        try:
            id_index = line.split('\t')[1].index('(')  # Find the opening parenthesis in the second section of the line
            log_type = line.split('\t')[1][:id_index]  # Extract the type from before the parenthesis
            return log_type
        except:
            return None


# Dialog for adding a new column to the data table
class AddColumnDialog(QDialog):
    """
    AddColumnDialog allows the user to add a new column to the table widget.
    It collects the necessary details such as column name, filters, and type.

    Attributes:
    -----------
    col_name_edit : QLineEdit
        Input field for the name of the new column.
    filter_edit : QLineEdit
        Input field for specifying filter conditions for the new column.
    type_edit : QLineEdit
        Input field for specifying the data type of the new column.
    from_edit : QLineEdit
        Input field for specifying the starting range of the data to add.
    to_edit : QLineEdit
        Input field for specifying the ending range of the data to add.
    data_edit : QLineEdit
        Input field for specifying the data to be added to the column.
    """
    def __init__(self, parent=None):
        """
        Initializes the AddColumnDialog by creating input fields for the user to specify
        details about the new column to be added.

        Parameters:
        -----------
        parent : QWidget (optional)
            The parent widget for the dialog.
        """
        super().__init__(parent)

        # Set the dialog title and layout
        self.setWindowTitle('Add Column')

        # Create input fields for column details
        self.col_name_edit = QLineEdit(self)  # Column name input
        self.filter_edit = QLineEdit(self)  # Filter input
        self.type_edit = QLineEdit(self)  # Type input
        self.from_edit = QLineEdit(self)  # From range input
        self.to_edit = QLineEdit(self)  # To range input
        self.data_edit = QLineEdit(self)  # Data input

        # Arrange input fields in a form layout
        form_layout = QFormLayout()
        form_layout.addRow("Column Name:", self.col_name_edit)
        form_layout.addRow("Filter:", self.filter_edit)
        form_layout.addRow("Type:", self.type_edit)
        form_layout.addRow("From :", self.from_edit)
        form_layout.addRow("To :", self.to_edit)
        form_layout.addRow("Data:", self.data_edit)

        # OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)  # Accept input and add column
        button_box.rejected.connect(self.reject)  # Reject input and close dialog

        # Set the dialog's main layout
        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_data(self):
        """
        Fetches and returns the user inputs as a tuple for further processing.

        Returns:
        --------
        tuple : (col_name, filter, type, from, to, data)
            Returns the column name, filter, type, from, to, and data as entered by the user.
        """
        return self.col_name_edit.text(), self.filter_edit.text(), self.type_edit.text(), self.from_edit.text(), self.to_edit.text(), self.data_edit.text()


# A dialog window for running custom Python scripts
class ScriptWindow(QDialog):
    """
    ScriptWindow provides a code editor interface where users can load, edit, and run Python scripts on their data.
    It allows users to work with the table widget data and apply custom transformations.

    Attributes:
    -----------
    table_widget : QTableWidget
        A reference to the main table widget containing the data.

    Constants:
    ----------
    SCRIPT_FILE : str
        The default file to store and load Python scripts.
    """
    SCRIPT_FILE = "script.txt"  # Default file to store the user's Python scripts

    def __init__(self, parent=None, table_widget=None):
        """
        Initializes the ScriptWindow, setting up the editor, loading an existing script (if any),
        and allowing users to save, load, and run scripts.

        Parameters:
        -----------
        parent : QWidget (optional)
            The parent widget for the script dialog.
        table_widget : QTableWidget
            Reference to the main table widget containing the data.
        """
        super().__init__(parent)

        self.ui = Ui_Dialog()  # Set up the UI for the dialog
        self.ui.setupUi(self)

        self.table_widget = table_widget  # Reference to the table widget

        # Connect buttons to their corresponding methods
        self.ui.run_button.clicked.connect(self.run_script)  # Run the script
        self.ui.load_button.clicked.connect(self.load_script_from_file)  # Load script from file
        self.ui.save_button.clicked.connect(self.save_script_to_file)  # Save script to file

        self.load_script()  # Load the default script when the window opens

    def load_script(self):
        """
        Load the script from the default file (if it exists) and display it in the editor.
        """
        if os.path.exists(self.SCRIPT_FILE):  # Check if the default script file exists
            with open(self.SCRIPT_FILE, 'r') as file:
                self.ui.editor.setPlainText(file.read())  # Load the script into the editor
        else:
            self.ui.editor.setPlainText("# Write your script here. The table data is available as 'table_data'.")

    def save_script(self):
        """
        Save the current script from the editor to the default script file.
        """
        with open(self.SCRIPT_FILE, 'w') as file:
            file.write(self.ui.editor.toPlainText())  # Save the script from the editor to file

    def load_script_from_file(self):
        """
        Open a file dialog to allow the user to select and load a Python script into the editor.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Script File", "", "Text Files (*.txt);;Python Files (*.py)", options=options)
        if file_name:  # If the user selects a file
            with open(file_name, 'r') as file:
                self.ui.editor.setPlainText(file.read())  # Load the selected file into the editor

    def save_script_to_file(self):
        """
        Open a file dialog to allow the user to save the current script to a file.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Script File", "", "Text Files (*.txt);;Python Files (*.py)", options=options)
        if file_name:  # If the user selects a file name
            with open(file_name, 'w') as file:
                file.write(self.ui.editor.toPlainText())  # Save the current script to the file

    def run_script(self):
        """
        Run the Python script written in the editor and apply it to the table data.
        Any output or errors are displayed in the output display.
        """
        script = self.ui.editor.toPlainText()  # Get the script text from the editor

        # Save the script before running it
        self.save_script()

        # Clear the previous output
        self.ui.output_display.clear()

        # Initialize an empty dictionary to store the table data
        table_data = {}

        # Get the number of rows and columns in the table widget
        row_count = self.table_widget.rowCount()
        column_count = self.table_widget.columnCount()

        # Get the column headers (names of the columns)
        headers = [self.table_widget.horizontalHeaderItem(i).text() for i in range(column_count)]

        # Initialize the table_data dictionary with empty lists for each column
        for header in headers:
            table_data[header] = []

        # Iterate over the rows and columns to populate the table_data dictionary
        for row in range(row_count):
            for col in range(column_count):
                item = self.table_widget.item(row, col)  # Get the item at the current cell
                if item is not None:
                    table_data[headers[col]].append(item.text())  # Add the cell value to the corresponding column
                else:
                    table_data[headers[col]].append(None)  # If no value, add None

        # Execute the script with the table data in a safe environment
        try:
            # Redirect the print output to the append_output method
            exec(script, {"table_data": table_data, "__builtins__": __builtins__, "print": self.append_output})
        except Exception as e:
            self.append_output(f"An error occurred: {str(e)}")  # Display any errors in the output display

    def append_output(self, text):
        """
        Appends the script's output or any errors to the output display.

        Parameters:
        -----------
        text : str
            The text (output or error) to append to the output display.
        """
        self.ui.output_display.append(str(text))  # Append the text to the output display

    def closeEvent(self, event):
        """
        Overrides the close event to save the script before closing the dialog.
        """
        self.save_script()  # Save the script before closing
        super().closeEvent(event)  # Call the parent class's close event method


# Main window of the application, where the user interacts with log data, filtering, and plotting
class MainWindow(QMainWindow):
    """
    MainWindow is the central UI for the application, handling log file loading, data filtering,
    plotting, and other core functionalities.

    Attributes:
    -----------
    content : list
        A list to store the content of the currently loaded log file.
    selected_filters : list
        A list of filters currently applied to the log data.
    filtersflag : bool
        A flag to indicate if filters are applied.
    file_name : str
        The path of the current log file being processed.
    chunk_size : int
        The size of each file chunk being processed in the background.
    lines_per_page : int
        The number of lines displayed per page in the UI.
    current_page : int
        The current page of data being displayed.
    file_reader_thread : FileReaderThread
        A thread for reading the log file in the background.
    graphs : list
        A list of graph data for storing plot information.
    graphs_model : QStringListModel
        A model to display the list of saved graphs in the UI.
    pixmap : QPixmap
        The image used for the rotating animation.
    rotate_thread : RotateThread
        A thread to handle rotating the image.
    hidden : str
        A flag to determine if the rotating image is hidden or visible.
    """

    def __init__(self, parent=None):
        """
        Initializes the main window, setting up the UI components, buttons, and threads.
        Connects buttons to their respective functionalities and initializes background tasks.

        Parameters:
        -----------
        parent : QWidget (optional)
            The parent widget for the main window.
        """
        super().__init__(parent)
        self.ui = Ui_Widget()  # Set up the UI components
        self.ui.setupUi(self)
        self.ui.TextArea.setContextMenuPolicy(Qt.CustomContextMenu)  # Enable custom context menu for the text area
        self.ui.TextArea.customContextMenuRequested.connect(self.show_context_menu)  # Connect to show custom menu on right-click
        self.ui.TextArea.setReadOnly(False)  # Allow the text area to be editable
        self.setWindowTitle("LogPilot")  # Set the window title



        # Initialize data structures and threading objects
        self.content = []  # Buffer to store log file content
        self.selected_filters = []  # List to store applied filters
        self.filtersflag = False  # Flag indicating whether filters are being applied
        self.file_name = ""  # Name of the file currently loaded
        self.chunk_size = 2048  # Size of file chunks to be processed
        self.lines_per_page = 1000  # Number of lines displayed per page
        self.current_page = 0  # Current page of log content being displayed
        self.file_reader_thread = None  # Thread for reading the log file
        self.graphs = []  # List to store graph data
        self.graphs_model = QStringListModel()  # Model to display the list of graphs in the UI
        self.ui.GraphsListView.setModel(self.graphs_model)  # Set the model for the graphs list view

        # Connect buttons to their respective functions
        self.ui.LoadButton.clicked.connect(self.load_file)  # Load file button
        self.ui.FilterButton.clicked.connect(self.add_filter)  # Add filter button
        self.ui.ClearFilter.clicked.connect(self.remove_all_filters)  # Clear filters button
        self.ui.FilterInput.setPlaceholderText("No Filters set")  # Placeholder text for filter input
        self.ui.PlotButton.clicked.connect(self.open_prompt_window)  # Plot button
        self.ui.FiltersSearchBox.returnPressed.connect(self.on_filter_selected)  # Enter key on filter search box

        self.ui.GraphsListView.clicked.connect(self.on_graph_selected)  # Click on a graph in the list
        self.ui.SaveButton.clicked.connect(self.save_graphs_and_context)  # Save graphs button

        # Set up rotating image (animation)
        self.pixmap = self.ui.label_2.pixmap()  # Get the pixmap for the rotating image
        self.rotate_thread = RotateThread(self.pixmap)  # Create a new RotateThread
        self.rotate_thread.rotated.connect(self.update_image)  # Connect the rotated image to the update method
        self.rotate_thread.start()  # Start the thread for rotating the image
        self.hidden = "no"  # Initial state: the image is visible
        self.toggle_visibility()  # Toggle image visibility

        # Load available filters from a file
        self.load_available_filters()

        # Connect additional buttons
        self.ui.AddColButton.clicked.connect(self.open_add_column_dialog)  # Open dialog to add new column
        self.ui.ExportButton.clicked.connect(self.export_to_excel)  # Export data to Excel button
        self.ui.tableWidget.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)  # Enable custom context menu for table header
        self.ui.tableWidget.horizontalHeader().customContextMenuRequested.connect(self.show_column_context_menu)  # Right-click on table header

        # Script window functionality
        self.ui.ScriptButton.clicked.connect(self.open_script_window)  # Open script editor window
    # Function to display context menu for table column headers
    def show_column_context_menu(self, position):
        """
        Show a context menu when right-clicking on a table column header.
        Provides options to edit or delete the selected column.

        Parameters:
        -----------
        position : QPoint
            The position where the context menu is requested.
        """
        header = self.ui.tableWidget.horizontalHeader()  # Get reference to the header
        col = header.logicalIndexAt(position)  # Get the index of the column where the right-click occurred

        # Create a custom context menu
        menu = QMenu(self)

        edit_action = QAction("Edit Column", self)  # Option to edit the column
        edit_action.triggered.connect(lambda: self.edit_column(col))  # Connect edit action to editing function
        menu.addAction(edit_action)

        delete_action = QAction("Delete Column", self)  # Option to delete the column
        delete_action.triggered.connect(lambda: self.delete_column(col))  # Connect delete action to deleting function
        menu.addAction(delete_action)

        menu.exec_(header.mapToGlobal(position))  # Display the context menu at the position of the right-click

    # Edit the column name in the table
    def edit_column(self, col_index):
        """
        Allows the user to edit the name of a column in the table widget.

        Parameters:
        -----------
        col_index : int
            The index of the column being edited.
        """
        # Open an input dialog to get the new column name from the user
        new_name, ok = QInputDialog.getText(self, "Edit Column", "Enter new column name:",
                                            QLineEdit.Normal, self.ui.tableWidget.horizontalHeaderItem(col_index).text())
        if ok and new_name:  # If the user confirms (OK) and enters a valid name
            self.ui.tableWidget.setHorizontalHeaderItem(col_index, QTableWidgetItem(new_name))  # Update the column name

    # Delete the column in the table
    def delete_column(self, col_index):
        """
        Allows the user to delete a column from the table widget, after confirmation.

        Parameters:
        -----------
        col_index : int
            The index of the column being deleted.
        """
        # Prompt the user for confirmation before deleting the column
        confirm = QMessageBox.question(self, "Delete Column",
                                       f"Are you sure you want to delete column '{self.ui.tableWidget.horizontalHeaderItem(col_index).text()}'?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:  # If the user confirms the deletion
            self.ui.tableWidget.removeColumn(col_index)  # Remove the selected column

    # Export the table data to an Excel file
    def export_to_excel(self):
        """
        Allows the user to export the table data to an Excel file.
        Opens a file dialog to select the location for saving the file.
        """
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if not fileName:
            return  # If no file is selected, do nothing

        # Collect data from the table widget
        row_count = self.ui.tableWidget.rowCount()
        column_count = self.ui.tableWidget.columnCount()

        # Create a pandas DataFrame to store the table data
        data = []
        headers = [self.ui.tableWidget.horizontalHeaderItem(i).text() for i in range(column_count)]

        for row in range(row_count):
            row_data = []
            for col in range(column_count):
                item = self.ui.tableWidget.item(row, col)
                row_data.append(item.text() if item else '')  # Add table cell data to the row list
            data.append(row_data)  # Append the row to the data list

        df = pd.DataFrame(data, columns=headers)  # Convert the data into a pandas DataFrame

        # Save the DataFrame to an Excel file
        df.to_excel(fileName, index=False, engine='openpyxl')
        QMessageBox.information(self, "Success", "Data exported successfully!")  # Notify the user of success

    # Function to open the Add Column dialog
    def open_add_column_dialog(self):
        """
        Opens a dialog to add a new column to the table widget.
        The user can specify column details such as name, filters, and type.
        """
        dialog = AddColumnDialog(self)  # Open the AddColumnDialog
        if dialog.exec() == QDialog.Accepted:  # If the user accepts the dialog
            col_name, filter_value, log_type, start_time, end_time, x_axis = dialog.get_data()
            if col_name:  # Only proceed if a column name is provided
                col_index = self.ui.tableWidget.columnCount()  # Get the current column count
                self.ui.tableWidget.insertColumn(col_index)  # Add a new column
                self.ui.tableWidget.setHorizontalHeaderItem(col_index, QTableWidgetItem(col_name))  # Set the column header

                # Handle empty inputs with defaults
                if not log_type:
                    return
                if not start_time:
                    start_time = MyDs.dataset.MIN  # Set default start time
                if not end_time:
                    end_time = MyDs.dataset.MAX  # Set default end time
                if not x_axis:
                    x_axis = "default"

                # Parse the filter values if provided
                having_attribute = []
                try:
                    if filter_value:
                        having_attribute = [(i.split("=")[0], i.split("=")[1]) for i in filter_value.replace(" ", "").split(",")]
                except:
                    pass

                # Construct the command to get data and populate the column
                command = f"Plot {log_type} x=default y={x_axis} from={start_time} to={end_time} " + ' '.join(f"__att[{key}]={value}" for key, value in having_attribute)
                Xdata = MyDs.get(command)  # Fetch the data using the constructed command

                # Populate the new column with data
                row_count = self.ui.tableWidget.rowCount()
                for row, value in enumerate(Xdata):
                    if row >= row_count:
                        self.ui.tableWidget.insertRow(row)  # Add a new row if necessary
                    self.ui.tableWidget.setItem(row, col_index, QTableWidgetItem(str(value)))  # Set the cell value

    # Function to update the rotating image in the UI
    def update_image(self, pixmap):
        """
        Updates the rotating image displayed in the UI.

        Parameters:
        -----------
        pixmap : QPixmap
            The updated image to display.
        """
        self.ui.label_2.setPixmap(pixmap)  # Update the label with the rotated image

    # Toggle visibility of the rotating image in the UI
    def toggle_visibility(self):
        """
        Toggles the visibility of the rotating image in the UI.
        If the image is currently visible, it will be hidden, and vice versa.
        """
        if self.hidden == "yes":  # If the image is hidden
            self.ui.label_2.setGeometry(QRect(770, 10, 51, 51))  # Restore the image size and position
            self.hidden = "no"  # Update the hidden state
        else:
            self.ui.label_2.setGeometry(QRect(0, 0, 0, 0))  # Hide the image by setting its size to 0
            self.hidden = "yes"  # Update the hidden state

    # Stop the rotation thread when closing the window
    def closeEvent(self, event):
        """
        Handles the close event for the main window.
        Stops the rotation thread and waits for it to finish before exiting.
        """
        self.rotate_thread.stop()  # Stop the rotating image thread
        self.rotate_thread.wait()  # Wait for the thread to finish
        super().closeEvent(event)  # Call the parent class's close event method

    # Save the current graphs and filters context to a file
    def save_graphs_and_context(self):
        """
        Saves the current graph and filter context to a file.
        The user is prompted to choose a location to save the file.
        """
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Graphs", "", "SAV Files (*.sav);;All Files (*)", options=options)
        if fileName:  # If the user selects a file
            with open(fileName, 'w') as file:
                file.write(f"{self.file_name}\n")  # Save the log file name
                file.write(','.join(self.selected_filters) + '\n')  # Save the selected filters
                for graph in self.graphs:
                    file.write(f"{graph['timestamp']}|{graph['log_type']}|{graph['start_time']}|{graph['end_time']}|{graph['x_axis']}|{graph['y_axis']}\n")  # Save the graph details

    # Function to open the plot prompt window
    def open_prompt_window(self):
        """
        Opens the PromptWindow to allow users to input data for plotting.
        """
        self.prompt_window = PromptWindow()  # Create a new instance of the PromptWindow
        self.prompt_window.resize(400, 300)  # Set the window size
        self.prompt_window.show()  # Display the window

    # Function to load available filters from a file
    def load_file(self):
        options = QFileDialog.Options()
        self.file_name, _ = QFileDialog.getOpenFileName(self,"Open File","","All Files (*);;Text Files (*.txt);;SAV Files (*.sav)",options=options)
        if self.file_name:
            if self.file_name.endswith('.sav'):
                self.load_sav_file(self.file_name)
            else:
                MyDs.initialize(self.file_name)
                self.content = []
                self.current_page = 0
                self.show_output()

    def load_sav_file(self, file_path):
        self.graphs.clear()  # Clear existing graphs
        with open(file_path, 'r') as file:
            self.file_name = file.readline().strip()
            print(f"Loaded file path: {self.file_name}")  # Debug output
            MyDs.initialize(self.file_name)
            
            selected_filters = file.readline().strip()
            self.selected_filters = selected_filters.split(',')
            print(f"Loaded filters: {self.selected_filters}")  # Debug output
            
            # Set the filters text in the UI
            self.ui.FilterInput.setPlainText(','.join(self.selected_filters))

            for line in file:
                timestamp, log_type, start_time, end_time, x_axis, y_axis = line.strip().split('|')
                graph_info = {
                    'timestamp': timestamp,
                    'log_type': log_type,
                    'x_axis': x_axis,
                    'y_axis': y_axis,
                    'start_time': start_time,
                    'end_time': end_time
                }
                print(f"Loading graph: {graph_info}")  # Debug output
                self.graphs.append(graph_info)
            self.update_graphs_list()  # Update the UI with loaded graphs
        
        # Apply the loaded filters to the view
        self.apply_loaded_filters()
    def apply_loaded_filters(self):
        if self.selected_filters:
            self.filtersflag = True  # Set the flag to use filters
            self.content = []  # Clear current content to prepare for filtered content
            self.current_page = 0  # Reset page view to the beginning
            self.show_output()  # Load and display the filtered content
        else:
            self.remove_all_filters()  # If no filters are loaded, remove all existing filters



    def on_filter_selected(self):
        selected_filter = self.ui.FiltersSearchBox.text().strip()
        if selected_filter and selected_filter in self.available_filters:
            current_filters = self.ui.FilterInput.toPlainText().strip()
            if current_filters:
                new_filters = current_filters + "," + selected_filter
            else:
                new_filters = selected_filter
            self.ui.FilterInput.setPlainText(new_filters)
            self.ui.FiltersSearchBox.clear()

        self.add_filter()
    def load_available_filters(self):
        """
        Loads available filters from a file and populates the list of filters.
        If no file is found, initializes an empty list.
        """
        try:
            with open("types.txt", "r") as file:
                self.available_filters = [filter.strip() for filter in file.read().split(',') if filter.strip()]  # Read and split the filter list
        except FileNotFoundError:
            self.available_filters = []  # Initialize an empty list if the file is not found

    # Function to save available filters to a file
    def save_available_filters(self):
        """
        Saves the current available filters to a file.
        """
        with open("types.txt", "w") as file:
            file.write(",".join(sorted(self.available_filters)))  # Write the sorted list of filters to the file

    # def load_file(self):
    #     """
    #     Opens a file dialog to select and load a log file for processing.
    #     Supports both text files and saved graph files (.sav).
    #     """
    #     options = QFileDialog.Options()
    #     self.file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt);;SAV Files (*.sav)", options=options)

    #     if self.file_name:
    #         # Reset progress bar and label before starting the task
    #         self.ui.progressBar.setValue(0)
    #         self.ui.progressBarLabel.setText("Loading log file...")
            
    #         # Load the raw log data into the text view (QTextBrowser)
    #     with open(self.file_name, 'r') as file:
    #         lines = []
    #         for i in range(160000):
    #             line = file.readline()
    #             if not line:
    #                 break
    #             lines.append(line)
    #         log_data = ''.join(lines)

    #         self.ui.RangeDataTextView.setPlainText(log_data)
    #         self.ui.TextArea.setPlainText(log_data)# Assuming QTextBrowser or QPlainTextEdit for log display

    #         # Process the file using your dataset parser (MYDS)
    #         MyDs.initialize(self.file_name)

    #         # Update the progress bar to 50% after parsing the file
    #         self.ui.progressBar.setValue(50)
    #         self.ui.progressBarLabel.setText("Log file loaded, generating heatmap...")

    #         # Generate heatmap and display in the QGraphicsView
    #         self.generate_heatmap()

    #         # Update the progress bar to 100% after heatmap generation
    #         self.ui.progressBar.setValue(100)
    #         self.ui.progressBarLabel.setText("Heatmap generation complete!")

    # def generate_heatmap(self):
    #     """
    #     Generates a log-scaled heatmap using parsed log data and displays it in QGraphicsView.
    #     Adds a constant color to all points and ensures it fills the screen.
    #     """
    #     # Extract data from MyDs dataset
    #     time_values = []
    #     message_types = []

    #     # Get the message types and timestamps from dataset.lookup
    #     for message_type, node_list in MyDs.dataset.lookup.items():
    #         for timestamp, node in node_list:
    #             time_values.append(float(timestamp))  # Convert timestamp to float
    #             message_types.append(message_type)

    #     # Bin the time values for the heatmap
    #     num_bins = 100  # Customize the number of bins based on your data
    #     time_bins = np.linspace(min(time_values), max(time_values), num_bins)

    #     # Create a matrix of message types vs time
    #     message_type_unique = list(set(message_types))
    #     heatmap_matrix = np.zeros((len(message_type_unique), num_bins))

    #     # Populate the heatmap matrix
    #     for i, msg_type in enumerate(message_types):
    #         time_bin_index = np.digitize(float(time_values[i]), time_bins) - 1
    #         type_index = message_type_unique.index(msg_type)
    #         heatmap_matrix[type_index, time_bin_index] += 1

    #     # Add a small constant to all elements to ensure even low counts have some visibility
    #     heatmap_matrix += 1

    #     # Apply log scale to the heatmap data to handle large variations in frequency
    #     log_heatmap_matrix = np.log1p(heatmap_matrix)  # Logarithmic scaling with np.log1p to avoid log(0)

    #     # Create the heatmap using seaborn with logarithmic scaling
    #     plt.figure(figsize=(10, 5))  # Adjusted figure size to fill the screen better
    #     sns.heatmap(
    #         log_heatmap_matrix,
    #         cmap="Blues",  # Use a clean color palette
    #         cbar=False,     # Show the color bar to indicate the range of values
    #         square=False,  # Allow the cells to be non-square to fill available space better
    #         xticklabels=True,  # Turn off tick labels for X-axis
    #         yticklabels=True   # Turn off tick labels for Y-axis
    #     )
    #     plt.axis('off')  # Turn off axis for a cleaner look
    #     plt.tight_layout()

    #     # Save the figure to a QPixmap
    #     fig = plt.gcf()
    #     fig.canvas.draw()
    #     width, height = fig.canvas.get_width_height()
    #     image = QImage(fig.canvas.buffer_rgba(), width, height, QImage.Format_RGBA8888)
    #     pixmap = QPixmap.fromImage(image)

    #     # Display the heatmap in QGraphicsView
    #     scene = QGraphicsScene(self)
    #     scene.addPixmap(pixmap)
    #     self.ui.DatarangegraphicsView.setScene(scene)  # Assuming QGraphicsView for heatmap display
    #     plt.close(fig)  # Close the figure after displaying
    def open_script_window(self):
        """
        Opens the ScriptWindow to allow users to run custom scripts on the table data.
        """
        script_window = ScriptWindow(self, self.ui.tableWidget)  # Create a new ScriptWindow
        script_window.exec()  # Show the script window

    # # Function to load a saved graph and filter context from a file
    # def load_sav_file(self, file_path):
    #     """
    #     Loads a saved file containing graphs and filters.
    #     Restores the saved graphs and filter settings in the UI.

    #     Parameters:
    #     -----------
    #     file_path : str
    #         The path to the saved file (.sav).
    #     """
    #     self.graphs.clear()  # Clear the current graph list
    #     with open(file_path, 'r') as file:
    #         self.file_name = file.readline().strip()  # Read the first line as the log file name
    #         MyDs.initialize(self.file_name)  # Initialize the dataset with the log file

    #         selected_filters = file.readline().strip()  # Read the second line as the selected filters
    #         self.selected_filters = selected_filters.split(',')  # Split the filters into a list

    #         for line in file:
    #             # Read and parse each line to restore graph data
    #             timestamp, log_type, start_time, end_time, x_axis, y_axis = line.strip().split('|')
    #             self.graphs.append({
    #                 'timestamp': timestamp,
    #                 'log_type': log_type,
    #                 'x_axis': x_axis,
    #                 'y_axis': y_axis,
    #                 'start_time': start_time,
    #                 'end_time': end_time
    #             })

    #         self.update_graphs_list()  # Update the list of graphs in the UI

    #     self.apply_loaded_filters()  # Apply the loaded filters

    # # Function to apply loaded filters to the data
    # def apply_loaded_filters(self):
    #     """
    #     Applies the loaded filters to the current log data and refreshes the view.
    #     """
    #     if self.selected_filters:
    #         self.filtersflag = True  # Set the filter flag
    #         self.content = []  # Reset content buffer
    #         self.current_page = 0  # Reset the current page
    #         self.show_output()  # Show the filtered content
    #     else:
    #         self.remove_all_filters()  # Remove filters if none are loaded

    # # Function to handle filter selection in the UI
    # def on_filter_selected(self):
    #     """
    #     Adds the selected filter to the list of applied filters and refreshes the view.
    #     """
    #     selected_filter = self.ui.FiltersSearchBox.text().strip()  # Get the selected filter
    #     if selected_filter and selected_filter in self.available_filters:
    #         current_filters = self.ui.FilterInput.toPlainText().strip()  # Get the current filters
    #         new_filters = f"{current_filters},{selected_filter}" if current_filters else selected_filter  # Add the new filter
    #         self.ui.FilterInput.setPlainText(new_filters)  # Update the filter input box
    #         self.ui.FiltersSearchBox.clear()  # Clear the search box

    #     self.add_filter()  # Apply the new filter

    # Function to show log output in the text area
    def show_output(self):
        """
        Displays the content of the log file in the text area, applying filters if necessary.
        Content is read in chunks to avoid performance issues with large files.
        """
        self.toggle_visibility()  # Hide the rotating image during file reading
        if self.file_reader_thread and self.file_reader_thread.isRunning():
            self.file_reader_thread.terminate()  # Stop the file reader thread if it's running

        # Create a new FileReaderThread to read the file in chunks
        self.file_reader_thread = FileReaderThread(
            self.file_name,
            self.chunk_size,
            self.lines_per_page,
            self.selected_filters,
            self.filtersflag,
            self.current_page
        )
        self.file_reader_thread.update_content.connect(self.update_content)  # Connect to update content in UI
        self.file_reader_thread.update_page.connect(self.display_page)  # Connect to display the page
        self.file_reader_thread.update_types.connect(self.update_filters)  # Connect to update available filters
        self.file_reader_thread.start()  # Start the thread for reading the file
        self.toggle_visibility()  # Show the rotating image again

    # Function to update the content in the text area
    def update_content(self, line):
        """
        Adds a new line of processed content to the buffer and updates the view.

        Parameters:
        -----------
        line : str
            The line of log data to add to the content buffer.
        """
        if len(self.content) < (self.current_page + 1) * self.lines_per_page:
            self.content.append(line)  # Add the new line to the buffer

    # Function to display the current page of content in the text area
    def display_page(self):
        """
        Displays the current page of content in the text area.
        """
        start_line = self.current_page * self.lines_per_page  # Calculate the start line for the current page
        end_line = start_line + self.lines_per_page  # Calculate the end line
        page_content = "\n".join(self.content[start_line:end_line])  # Get the content for the current page
        self.ui.TextArea.setPlainText(page_content)  # Display the content in the text area

    # Function to apply a new filter to the data
    def add_filter(self):
        """
        Applies the selected filters to the log data and refreshes the view.
        """
        self.content = []  # Reset the content buffer
        self.filtersflag = True  # Set the filter flag
        self.selected_filters = list(map(str, self.ui.FilterInput.toPlainText().strip().split(",")))  # Get the selected filters
        self.current_page = 0  # Reset the current page
        self.show_output()  # Show the filtered content

    # Function to remove all filters from the data
    def remove_all_filters(self):
        """
        Removes all filters and displays the full content of the log file.
        """
        self.content = []  # Reset the content buffer
        self.filtersflag = False  # Clear the filter flag
        self.current_page = 0  # Reset the current page
        self.ui.FilterInput.clear()  # Clear the filter input box
        self.show_output()  # Show the full content

    # Function to update the list of available filters based on the log data
    def update_filters(self, new_filters):
        """
        Updates the list of available filters with any new log types found in the data.

        Parameters:
        -----------
        new_filters : set
            A set of new log types encountered while reading the file.
        """
        self.available_filters = list(set(self.available_filters).union(new_filters))  # Merge the new filters with existing ones
        self.save_available_filters()  # Save the updated list of filters
        self.completer = SubstringCompleter(self.available_filters, self)  # Create a new completer with the updated filters
        self.ui.FiltersSearchBox.setCompleter(self.completer)  # Set the completer for the filter search box

    # Function to display a custom context menu for the text area
    def show_context_menu(self, position):
        """
        Shows a custom context menu for the text area, providing options for plotting and adding data to the table.

        Parameters:
        -----------
        position : QPoint
            The position where the context menu is requested.
        """
        context_menu = QMenu(self)
        plot_action = QAction("Quick Plot", self)
        plot_action.triggered.connect(self.plot_selected_text)  # Connect to quick plot function
        context_menu.addAction(plot_action)

        plot_To_action = QAction("Plot till here", self)
        plot_To_action.triggered.connect(self.Plot_To)  # Connect to plot till here function
        context_menu.addAction(plot_To_action)

        plot_From_action = QAction("Plot From here", self)
        plot_From_action.triggered.connect(self.Plot_From)  # Connect to plot from here function
        context_menu.addAction(plot_From_action)

        Add_col_action = QAction("Add to Table", self)
        Add_col_action.triggered.connect(self.add_selected_text)  # Connect to add selected text to table function
        context_menu.addAction(Add_col_action)

        Addf_col_action = QAction("Add from here to Table", self)
        Addf_col_action.triggered.connect(self.add_from_selected_text)  # Connect to add from here to table function
        context_menu.addAction(Addf_col_action)

        Add2_col_action = QAction("Add till here to Table", self)
        Add2_col_action.triggered.connect(self.add_to_selected_text)  # Connect to add till here to table function
        context_menu.addAction(Add2_col_action)

        if not self.ui.TextArea.textCursor().selectedText():
            plot_action.setEnabled(False)  # Disable plot action if no text is selected
        context_menu.exec_(self.ui.TextArea.mapToGlobal(position))  # Show the context menu at the cursor's position

    # Function to plot the selected text in the text area
    def plot_selected_text(self):
        """
        Plots the selected text in the text area using the log data.
        """
        cursor = self.ui.TextArea.textCursor()  # Get the current text cursor
        selected_text = cursor.selectedText()  # Get the selected text

        start_pos = cursor.selectionStart()  # Get the starting position of the selection
        cursor.setPosition(start_pos)

        line_number = cursor.blockNumber() + 1  # Get the line number of the selected text

        cursor.select(QTextCursor.LineUnderCursor)  # Select the entire line
        entire_line_text = cursor.selectedText()  # Get the text of the selected line

        # Extract the log type and time from the line
        c = entire_line_text.split('\t')[1]
        time = entire_line_text.split(" ")[5]
        typ = c[:c.index("(")]
        self.plot_data(typ, MyDs.dataset.MIN, MyDs.dataset.MAX, None, selected_text)  # Call the plot function

    # Function to add the selected text as a new column in the table widget
    def add_selected_text(self):
        """
        Adds the selected text as a new column in the table widget.
        """
        cursor = self.ui.TextArea.textCursor()  # Get the current text cursor
        selected_text = cursor.selectedText()  # Get the selected text

        cursor.select(QTextCursor.LineUnderCursor)  # Select the entire line
        entire_line_text = cursor.selectedText()  # Get the text of the selected line

        # Extract the log type and time from the line
        c = entire_line_text.split('\t')[1]
        time = entire_line_text.split(" ")[5]
        typ = c[:c.index("(")]

        # Insert a new column into the table
        col_index = self.ui.tableWidget.columnCount()
        self.ui.tableWidget.insertColumn(col_index)
        self.ui.tableWidget.setHorizontalHeaderItem(col_index, QTableWidgetItem(selected_text))

        # Fetch the data for the new column
        xdata = MyDs.get(f"Plot {typ} x=default y={selected_text} from={MyDs.dataset.MIN} to={MyDs.dataset.MAX}")

        # Populate the new column with data
        row_count = self.ui.tableWidget.rowCount()
        for row, value in enumerate(xdata):
            if row >= row_count:
                self.ui.tableWidget.insertRow(row)
            self.ui.tableWidget.setItem(row, col_index, QTableWidgetItem(str(value)))

    # Function to add data up to the selected line as a column in the table widget
    def add_to_selected_text(self):
        """
        Adds the data up to the selected line as a column in the table widget.
        """
        cursor = self.ui.TextArea.textCursor()  # Get the current text cursor
        selected_text = cursor.selectedText()  # Get the selected text

        cursor.select(QTextCursor.LineUnderCursor)  # Select the entire line
        entire_line_text = cursor.selectedText()  # Get the text of the selected line

        # Extract the log type and time from the line
        c = entire_line_text.split('\t')[1]
        time = entire_line_text.split(" ")[5]
        typ = c[:c.index("(")]

        # Insert a new column into the table
        col_index = self.ui.tableWidget.columnCount()
        self.ui.tableWidget.insertColumn(col_index)
        self.ui.tableWidget.setHorizontalHeaderItem(col_index, QTableWidgetItem(selected_text))

        # Fetch the data for the new column
        xdata = MyDs.get(f"Plot {typ} x=default y={selected_text} from={MyDs.dataset.MIN} to={time}")

        # Populate the new column with data
        row_count = self.ui.tableWidget.rowCount()
        for row, value in enumerate(xdata):
            if row >= row_count:
                self.ui.tableWidget.insertRow(row)
            self.ui.tableWidget.setItem(row, col_index, QTableWidgetItem(str(value)))

    # Function to add data from the selected line onwards as a column in the table widget
    def add_from_selected_text(self):
        """
        Adds the data from the selected line onwards as a column in the table widget.
        """
        cursor = self.ui.TextArea.textCursor()  # Get the current text cursor
        selected_text = cursor.selectedText()  # Get the selected text

        cursor.select(QTextCursor.LineUnderCursor)  # Select the entire line
        entire_line_text = cursor.selectedText()  # Get the text of the selected line

        # Extract the log type and time from the line
        c = entire_line_text.split('\t')[1]
        time = entire_line_text.split(" ")[5]
        typ = c[:c.index("(")]

        # Insert a new column into the table
        col_index = self.ui.tableWidget.columnCount()
        self.ui.tableWidget.insertColumn(col_index)
        self.ui.tableWidget.setHorizontalHeaderItem(col_index, QTableWidgetItem(selected_text))

        # Fetch the data for the new column
        xdata = MyDs.get(f"Plot {typ} x=default y={selected_text} from={time} to={MyDs.dataset.MAX}")

        # Populate the new column with data
        row_count = self.ui.tableWidget.rowCount()
        for row, value in enumerate(xdata):
            if row >= row_count:
                self.ui.tableWidget.insertRow(row)
            self.ui.tableWidget.setItem(row, col_index, QTableWidgetItem(str(value)))

    # Function to plot data up to the selected line in the text area
    def Plot_To(self):
        """
        Plots the data up to the selected line in the text area.
        """
        cursor = self.ui.TextArea.textCursor()  # Get the current text cursor
        selected_text = cursor.selectedText()  # Get the selected text

        start_pos = cursor.selectionStart()  # Get the starting position of the selection
        cursor.setPosition(start_pos)

        cursor.select(QTextCursor.LineUnderCursor)  # Select the entire line
        entire_line_text = cursor.selectedText()  # Get the text of the selected line

        # Extract the log type and time from the line
        c = entire_line_text.split('\t')[1]
        time = entire_line_text.split(" ")[5]
        typ = c[:c.index("(")]

        self.plot_data(typ, MyDs.dataset.MIN, time, 'default', selected_text)  # Call the plot function

    # Function to plot data starting from the selected line in the text area
    def Plot_From(self):
        """
        Plots the data starting from the selected line in the text area.
        """
        cursor = self.ui.TextArea.textCursor()  # Get the current text cursor
        selected_text = cursor.selectedText()  # Get the selected text

        start_pos = cursor.selectionStart()  # Get the starting position of the selection
        cursor.setPosition(start_pos)

        cursor.select(QTextCursor.LineUnderCursor)  # Select the entire line
        entire_line_text = cursor.selectedText()  # Get the text of the selected line

        # Extract the log type and time from the line
        c = entire_line_text.split('\t')[1]
        time = entire_line_text.split(" ")[5]
        typ = c[:c.index("(")]

        self.plot_data(typ, time, MyDs.dataset.MAX, 'default', selected_text)  # Call the plot function

    # Function to plot the data using the specified parameters
    def plot_data(self, log_type, start_time, end_time, x_axis, y_axis, having_attribute=[], parent_having_attribute=[],script=""):
        """
        Plots the data using the specified parameters and updates the list of saved graphs.

        Parameters:
        -----------
        log_type : str
            The type of log data to plot.
        start_time : str
            The starting time for the data to plot.
        end_time : str
            The ending time for the data to plot.
        x_axis : str
            The data attribute to use for the X-axis.
        y_axis : str
            The data attribute to use for the Y-axis.
        having_attribute : list
            A list of additional filter attributes for the data.
        parent_having_attribute : list
            A list of parent filter attributes for the data.
        """
        self.toggle_visibility()  # Hide the rotating image while plotting
        if not log_type:
            return  # Exit if no log type is specified

        if not y_axis:
            return  # Exit if no Y-axis is specified

        if not start_time:
            start_time = MyDs.dataset.MIN  # Set default start time

        if not end_time:
            end_time = MyDs.dataset.MAX  # Set default end time

        if not x_axis:
            x_axis = "default"  # Set default X-axis if not provided

        # Construct the plot command with optional filter attributes
        attr_command = ' '.join(f"__att[{key}]={value}" for key, value in having_attribute)
        parent_attr_command = ' '.join(f"p__att[{key}]={value}" for key, value in parent_having_attribute)
        command = f"Plot {log_type} x={x_axis} y={y_axis} from={start_time} to={end_time} {attr_command} {parent_attr_command}"

        MyDs.main(command,script)  # Call the main plotting function

        # Save the graph details for future reference
        graph_info = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'log_type': log_type,
            'x_axis': x_axis,
            'y_axis': y_axis,
            'start_time': start_time,
            'end_time': end_time,
            'attr_command': attr_command
        }
        self.graphs.append(graph_info)  # Add the graph info to the list
        self.update_graphs_list()  # Update the graph list in the UI
        self.toggle_visibility()  # Show the rotating image again

    # Function to update the list of saved graphs in the UI
    def update_graphs_list(self):
        """
        Updates the list of saved graphs displayed in the UI.
        """
        graph_descriptions = [
            f"{g['timestamp']}: {g['log_type']} from {g['start_time']} to {g['end_time']} (X: {g['x_axis']}, Y: {g['y_axis']})"
            for g in self.graphs
        ]
        if self.graphs_model:
            self.graphs_model.setStringList(graph_descriptions)  # Update the model with the list of graphs

    # Function to re-plot a selected graph from the list of saved graphs
    def on_graph_selected(self, index):
        """
        Re-plots the selected graph from the list when the user selects a graph.

        Parameters:
        -----------
        index : QModelIndex
            The index of the selected graph in the list.
        """
        graph_info = self.graphs[index.row()]  # Get the selected graph info
        command = f"Plot {graph_info['log_type']} x={graph_info['x_axis']} y={graph_info['y_axis']} from={graph_info['start_time']} to={graph_info['end_time']} {graph_info['attr_command']}"
        MyDs.main(command)  # Re-plot the graph using the saved parameters


# Entry point for the application
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create the QApplication object
    main_window = MainWindow()  # Create an instance of the MainWindow
    main_window.show()  # Show the main window
    sys.exit(app.exec())  # Run the application's event loop
    