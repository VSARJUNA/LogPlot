import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QVBoxLayout, QWidget, QCompleter, QMenu, QFormLayout, QLineEdit,QMessageBox
from PySide6.QtGui import QAction, QTextCursor,QTransform,QPixmap
from ui_form import Ui_Widget
from PySide6.QtCore import Qt, QThread, Signal, QStringListModel, QSortFilterProxyModel,QRect
import MyDs
from datetime import datetime

class RotateThread(QThread):
    rotated = Signal(QPixmap)

    def __init__(self, pixmap):
        super().__init__()
        self.pixmap = pixmap
        self.angle = 0
        self._is_running = True

    def run(self):
        while self._is_running:
            self.angle = (self.angle + 12) % 360  # Increment the angle
            rotated_pixmap = self.pixmap.transformed(QTransform().rotate(self.angle))
            self.rotated.emit(rotated_pixmap)
            self.msleep(50)  # Adjust speed of rotation here

    def stop(self):
        self._is_running = False
        
        

class PromptWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prompt Window")

        layout = QFormLayout()
        self.starttime_input = QLineEdit(self)
        layout.addRow("Start_Time", self.starttime_input)

        self.endtime_input = QLineEdit(self)
        layout.addRow("End_Time", self.endtime_input)
        
        self.TypesBox = QLineEdit(self)
        self.Typecompleter = SubstringCompleter(list(MyDs.dataset.lookup.keys()), self)
        self.TypesBox.setCompleter(self.Typecompleter)
        self.TypesBox.returnPressed.connect(self.selectType)
        layout.addRow("Type", self.TypesBox)
        
        self.XBox = QLineEdit(self)
        layout.addRow("X", self.XBox)
        
        self.YBox = QLineEdit(self)
        layout.addRow("Y", self.YBox)

        buttons_layout = QVBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.on_ok_clicked)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addRow(buttons_layout)

        self.setLayout(layout)
        
    def selectType(self):
        self.type = self.TypesBox.text()
        self.TypeXcompleter = SubstringCompleter(list(MyDs.dataset.lookup[self.type][0][1].attributes.keys()), self)
        self.XBox.setCompleter(self.TypeXcompleter)
        self.TypeYcompleter = SubstringCompleter(list(MyDs.dataset.lookup[self.type][0][1].attributes.keys()), self)
        self.YBox.setCompleter(self.TypeYcompleter)

    def on_ok_clicked(self):
        start_time = self.starttime_input.text()
        end_time = self.endtime_input.text()
        log_type = self.TypesBox.text()
        x_axis = self.XBox.text()
        y_axis = self.YBox.text()
        
        main_window.plot_data(log_type, start_time, end_time, x_axis, y_axis)
        self.close()

    def on_cancel_clicked(self):
        self.close()

    def plot_data(self, log_type, start_time, end_time, x_axis, y_axis):
        if not log_type:
            print("Error: Log type is required.")
            return

        if not y_axis:
            print("Error: Y-axis type is required.")
            return

        if not start_time:
            print(f"Invalid or missing start time, setting to minimum: {MyDs.dataset.MIN}")
            start_time = MyDs.dataset.MIN

        if not end_time:
            print(f"Invalid or missing end time, setting to maximum: {MyDs.dataset.MAX}")
            end_time = MyDs.dataset.MAX

        if not x_axis:
            print("X-axis type not provided, defaulting to 'default'")
            x_axis = "default"

        print(f"Plotting {log_type} from {start_time} to {end_time} with X: {x_axis}, Y: {y_axis}")

        MyDs.main(f"Plot {log_type} x={x_axis} y={y_axis} from={start_time} to={end_time}")

class SubstringCompleter(QCompleter):
    def __init__(self, words, parent=None):
        super().__init__(words, parent)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(QStringListModel(words))
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setModel(self.proxy_model)
        self.setFilterMode(Qt.MatchContains)

    def updateModel(self, completion_prefix):
        self.proxy_model.setFilterFixedString(completion_prefix)
        self.popup().setCurrentIndex(self.proxy_model.index(0, 0))

class FileReaderThread(QThread):
    update_content = Signal(str)
    update_page = Signal()
    update_types = Signal(set)

    def __init__(self, file_name, chunk_size, lines_per_page, selected_filters, filtersflag, current_page):
        super().__init__()
        self.file_name = file_name
        self.chunk_size = chunk_size
        self.lines_per_page = lines_per_page
        self.selected_filters = selected_filters
        self.filtersflag = filtersflag
        self.current_page = current_page
        self.encountered_types = set()

    def run(self):
        try:
            with open(self.file_name, 'r') as file:
                buffer = ""
                while True:
                    chunk = file.read(self.chunk_size)
                    if not chunk:
                        break
                    buffer += chunk
                    if '\n' in buffer:
                        lines = buffer.split('\n')
                        for line in lines[:-1]:
                            self.process_line(line)
                        buffer = lines[-1]
                if buffer:
                    self.process_line(buffer)
            self.update_page.emit()
            self.update_types.emit(self.encountered_types)
        except Exception as e:
            print(e)

    def process_line(self, line):
        try:
            log_type = self.extract_type(line)
            if log_type:
                self.encountered_types.add(log_type)

            if self.filtersflag:
                if log_type in self.selected_filters:
                    self.update_content.emit(line)
            else:
                self.update_content.emit(line)
        except Exception as e:
            print(e)

    def extract_type(self, line):
        try:
            id_index = line.split('\t')[1].index('(')
            log_type = line.split('\t')[1][:id_index]
            return log_type
        except:
            return None

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.ui.TextArea.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.TextArea.customContextMenuRequested.connect(self.show_context_menu)
        self.ui.TextArea.setReadOnly(False)
        self.setWindowTitle("LogPlot App")

        self.content = []
        self.selected_filters = []
        self.filtersflag = False
        self.file_name = ""
        self.chunk_size = 2048
        self.lines_per_page = 1000
        self.current_page = 0
        self.file_reader_thread = None
        self.graphs = []
        self.graphs_model = QStringListModel()
        self.ui.GraphsListView.setModel(self.graphs_model)

        self.ui.LoadButton.clicked.connect(self.load_file)
        self.ui.FilterButton.clicked.connect(self.add_filter)
        self.ui.ClearFilter.clicked.connect(self.remove_all_filters)
        self.ui.FilterInput.setPlaceholderText("No Filters set")
        self.ui.PlotButton.clicked.connect(self.open_prompt_window)
        self.ui.FiltersSearchBox.returnPressed.connect(self.on_filter_selected)

        self.ui.GraphsListView.clicked.connect(self.on_graph_selected)
        self.ui.SaveButton.clicked.connect(self.save_graphs_and_context)
        self.pixmap=self.ui.label_2.pixmap()
        self.rotate_thread = RotateThread(self.pixmap)
        self.rotate_thread.rotated.connect(self.update_image)
        self.rotate_thread.start()
        self.hidden="no"
        self.toggle_visibility()
        self.load_available_filters()
    def update_image(self, pixmap):
        self.ui.label_2.setPixmap(pixmap)

    def toggle_visibility(self):
        if(self.hidden=="yes"):
            self.ui.label_2.setGeometry(QRect(770, 10, 51, 51))
            self.hidden="no"
        else:
            self.ui.label_2.setGeometry(QRect(0, 0, 0,0))
            self.hidden="yes"

    def closeEvent(self, event):
        self.rotate_thread.stop()
        self.rotate_thread.wait()
        super().closeEvent(event)
    def save_graphs_and_context(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Graphs", "", "SAV Files (*.sav);;All Files (*)", options=options)
        if fileName:
            with open(fileName, 'w') as file:
                file.write(f"{self.file_name}\n")  # Save the path to the log file
                file.write(','.join(self.selected_filters) + '\n')
                for graph in self.graphs:
                    graph_line = f"{graph['timestamp']}|{graph['log_type']}|{graph['start_time']}|{graph['end_time']}|{graph['x_axis']}|{graph['y_axis']}\n"
                    print(f"Saving graph: {graph_line.strip()}")  # Debugging output
                    file.write(graph_line)
    def open_prompt_window(self):
        self.prompt_window = PromptWindow()
        self.prompt_window.resize(400, 300)  # Set the initial size (width, height)
        self.prompt_window.show()

    def load_available_filters(self):
        try:
            with open("types.txt", "r") as file:
                self.available_filters = [filter.strip() for filter in file.read().split(',') if filter.strip()]
        except FileNotFoundError:
            self.available_filters = []

    def save_available_filters(self):
        with open("types.txt", "w") as file:
            file.write(",".join(sorted(self.available_filters)))

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

    def show_output(self):
        self.toggle_visibility()
        if self.file_reader_thread and self.file_reader_thread.isRunning():
            self.file_reader_thread.terminate()

        self.file_reader_thread = FileReaderThread(
            self.file_name,
            self.chunk_size,
            self.lines_per_page,
            self.selected_filters,
            self.filtersflag,
            self.current_page
        )
        self.file_reader_thread.update_content.connect(self.update_content)
        self.file_reader_thread.update_page.connect(self.display_page)
        self.file_reader_thread.update_types.connect(self.update_filters)
        self.file_reader_thread.start()
        self.toggle_visibility()
        

    def update_content(self, line):
        if len(self.content) < (self.current_page + 1) * self.lines_per_page:
            self.content.append(line)

    def display_page(self):
        start_line = self.current_page * self.lines_per_page
        end_line = start_line + self.lines_per_page
        page_content = "\n".join(self.content[start_line:end_line])
        self.ui.TextArea.setPlainText(page_content)

    def add_filter(self):
        self.content = []
        self.filtersflag = True
        self.selected_filters = list(map(str, self.ui.FilterInput.toPlainText().strip().split(",")))
        self.current_page = 0
        self.show_output()

    def remove_all_filters(self):
        self.content = []
        self.filtersflag = False
        self.current_page = 0
        self.ui.FilterInput.clear()
        self.show_output()

    def update_filters(self, new_filters):
        self.available_filters = list(set(self.available_filters).union(new_filters))
        self.save_available_filters()
        self.completer = SubstringCompleter(self.available_filters, self)
        self.ui.FiltersSearchBox.setCompleter(self.completer)
        
    def show_context_menu(self, position):
        context_menu = QMenu(self)
        plot_action = QAction("Quick Plot", self)
        plot_action.triggered.connect(self.plot_selected_text)
        context_menu.addAction(plot_action)
        
        plot_To_action = QAction("Plot till here", self)
        plot_To_action.triggered.connect(self.Plot_To)
        context_menu.addAction(plot_To_action)
        
        plot_From_action = QAction("Plot From here", self)
        plot_From_action.triggered.connect(self.Plot_From)
        context_menu.addAction(plot_From_action)
        
        if not self.ui.TextArea.textCursor().selectedText():
            plot_action.setEnabled(False)
        context_menu.exec_(self.ui.TextArea.mapToGlobal(position))

    def plot_selected_text(self):
        cursor = self.ui.TextArea.textCursor()
        selected_text = cursor.selectedText()

        start_pos = cursor.selectionStart()
        cursor.setPosition(start_pos)

        line_number = cursor.blockNumber() + 1

        cursor.select(QTextCursor.LineUnderCursor)
        entire_line_text = cursor.selectedText()

        c = entire_line_text.split('\t')[1]
        time = entire_line_text.split(" ")[5]
        typ = c[:c.index("(")]
        #MyDs.main(f"Plot {typ} x=default y={selected_text} from={MyDs.dataset.MIN} to={MyDs.dataset.MAX}")
        self.plot_data(typ,MyDs.dataset.MIN,MyDs.dataset.MAX,None,selected_text)
        

    def Plot_To(self):
        cursor = self.ui.TextArea.textCursor()
        selected_text = cursor.selectedText()

        start_pos = cursor.selectionStart()
        cursor.setPosition(start_pos)

        line_number = cursor.blockNumber() + 1

        cursor.select(QTextCursor.LineUnderCursor)
        entire_line_text = cursor.selectedText()

        c = entire_line_text.split('\t')[1]
        time = entire_line_text.split(" ")[5]
        typ = c[:c.index("(")]
        #MyDs.main(f"Plot {typ} x=default y={selected_text} from={MyDs.dataset.MIN} to={time}")
        self.plot_data(typ,MyDs.dataset.MIN,time,'default',selected_text)
    
    def Plot_From(self):
        cursor = self.ui.TextArea.textCursor()
        selected_text = cursor.selectedText()

        start_pos = cursor.selectionStart()
        cursor.setPosition(start_pos)

        line_number = cursor.blockNumber() + 1

        cursor.select(QTextCursor.LineUnderCursor)
        entire_line_text = cursor.selectedText()

        c = entire_line_text.split('\t')[1]
        time = entire_line_text.split(" ")[5]
        typ = c[:c.index("(")]
        #MyDs.main(f"Plot {typ} x=default y={selected_text} from={time} to={MyDs.dataset.MAX}")
        self.plot_data(typ,time,MyDs.dataset.MAX,'default',selected_text)

    def plot_data(self, log_type, start_time, end_time, x_axis, y_axis, having_attribute=[], parent_having_attribute=[]):
        self.toggle_visibility()
        if not log_type:
            # QMessageBox.warning(self, "Error", "Log type is required.")
            return

        if not y_axis:
            # QMessageBox.warning(self, "Error", "Y-axis type is required.")
            return

        if not start_time:
            # QMessageBox.warning(self, "Error", f"Invalid or missing start time, setting to minimum: {MyDs.dataset.MIN}")
            start_time = MyDs.dataset.MIN

        if not end_time:
            # QMessageBox.warning(self, "Error", f"Invalid or missing end time, setting to maximum: {MyDs.dataset.MAX}")
            end_time = MyDs.dataset.MAX

        if not x_axis:
            x_axis = "default"

        attr_command = ' '.join(f"__att[{key}]={value}" for key, value in having_attribute)
        parent_attr_command = ' '.join(f"p__att[{key}]={value}" for key, value in parent_having_attribute)
        command = f"Plot {log_type} x={x_axis} y={y_axis} from={start_time} to={end_time} {attr_command} {parent_attr_command}"

        data_got=MyDs.main(command)
        

        graph_info = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'log_type': log_type,
            'x_axis': x_axis,
            'y_axis': y_axis,
            'start_time': start_time,
            'end_time': end_time
        }
        self.graphs.append(graph_info)
        self.update_graphs_list()
        self.toggle_visibility()

    def update_graphs_list(self):
        graph_descriptions = [
            f"{g['timestamp']}: {g['log_type']} from {g['start_time']} to {g['end_time']} (X: {g['x_axis']}, Y: {g['y_axis']})"
            for g in self.graphs
        ]
        if self.graphs_model:
            self.graphs_model.setStringList(graph_descriptions)

    def on_graph_selected(self, index):
        graph_info = self.graphs[index.row()]
        command = f"Plot {graph_info['log_type']} x={graph_info['x_axis']} y={graph_info['y_axis']} from={graph_info['start_time']} to={graph_info['end_time']}"
        MyDs.main(command)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())