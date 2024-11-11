import sys
import os
import shutil
from PyQt5.QtCore import Qt, QDir, QFileInfo
from PyQt5.QtGui import QColor, QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QHBoxLayout, QAbstractItemView, QMessageBox
import subprocess
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QDialog, QFormLayout, QLabel
from PyQt5.QtCore import QThread, pyqtSignal

class SearchThread(QThread):
    result_signal = pyqtSignal(list)
    finished_signal = pyqtSignal()

    def __init__(self, keyword, directory):
        super().__init__()
        self.keyword = keyword
        self.directory = directory

    def run(self):
        results = []
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if self.keyword.lower() in file.lower():
                    results.append(os.path.join(root, file))
        self.result_signal.emit(results)
        self.finished_signal.emit()

class FileExplorerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Streamlined Explorer")
        self.setGeometry(100, 100, 800, 600)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #2e2e2e;
                color: white;
            }
            QLineEdit, QPushButton {
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QTableWidget {
                background-color: #333333;
                color: white;
                border: 1px solid #555555;
            }
            QTableWidget::item {
                background-color: #444444;
            }
        """)

        self.current_path = QDir.rootPath()  
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        button_layout = QHBoxLayout()

        open_folder_button = QPushButton("Open Folder")
        open_folder_button.setFixedSize(100, 30)  
        open_folder_button.clicked.connect(self.open_directory)
        button_layout.addWidget(open_folder_button, alignment=Qt.AlignLeft)

        view_properties_button = QPushButton("View Properties")
        view_properties_button.setFixedSize(150, 30)
        view_properties_button.clicked.connect(self.view_properties)
        button_layout.addWidget(view_properties_button)

        rename_button = QPushButton("Rename Selected Item")
        rename_button.setFixedSize(150, 30)
        rename_button.clicked.connect(self.rename_selected_item)
        button_layout.addWidget(rename_button)

        delete_button = QPushButton("Delete Selected Item")
        delete_button.setFixedSize(150, 30)
        delete_button.clicked.connect(self.delete_item)  
        button_layout.addWidget(delete_button)

        new_button = QPushButton("+")
        new_button.setFixedSize(30, 30)
        new_button.clicked.connect(self.show_new_item_menu)
        button_layout.addWidget(new_button)

        layout.addLayout(button_layout)

        self.path_bar = QLineEdit(self.current_path)
        self.path_bar.setReadOnly(False)  
        self.path_bar.returnPressed.connect(self.change_path)  
        layout.addWidget(self.path_bar)

        self.file_table = QTableWidget(self)
        self.file_table.setColumnCount(3)
        self.file_table.setHorizontalHeaderLabels(["Name", "Date Modified", "Size"])
        self.file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.file_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  
        layout.addWidget(self.file_table)

        self.load_files(self.current_path)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.file_table.cellDoubleClicked.connect(self.on_file_double_click)

    def rename_selected_item(self):
        selected_row = self.file_table.currentRow()
        if selected_row >= 0:
            file_item = self.file_table.item(selected_row, 0)
            if file_item:
                file_name = file_item.text()
                new_name, ok = QInputDialog.getText(self, "Rename Item", "Enter new name:", QLineEdit.Normal, file_name)
                if ok and new_name:
                    old_path = os.path.join(self.current_path, file_name)
                    new_path = os.path.join(self.current_path, new_name)
                    if not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        self.load_files(self.current_path)
                    else:
                        QMessageBox.warning(self, "Error", "A file or folder with this name already exists.")
            else:
                QMessageBox.warning(self, "Error", "No item selected to rename.")
        else:
            QMessageBox.warning(self, "Error", "No item selected to rename.")

    def show_new_item_menu(self):

        menu = QMenu(self)

        new_folder_action = QAction("New Folder", self)
        new_folder_action.triggered.connect(self.create_new_folder)

        new_file_action = QAction("New File", self)
        new_file_action.triggered.connect(self.create_new_file)

        menu.addAction(new_folder_action)
        menu.addAction(new_file_action)

        menu.exec_(QCursor.pos())

    def create_new_folder(self):

        folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and folder_name:
            folder_path = os.path.join(self.current_path, folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                self.load_files(self.current_path)
            else:
                QMessageBox.warning(self, "Error", "A folder with this name already exists.")

    def create_new_file(self):

        file_name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and file_name:
            file_path = os.path.join(self.current_path, file_name)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write("")  
                self.load_files(self.current_path)
            else:
                QMessageBox.warning(self, "Error", "A file with this name already exists.")

    def view_properties(self):
        selected_row = self.file_table.currentRow()
        if selected_row >= 0:
            file_item = self.file_table.item(selected_row, 0)
            if file_item:
                file_name = file_item.text()
                file_info = QFileInfo(os.path.join(self.current_path, file_name))

                if file_info.exists():

                    properties_dialog = QDialog(self)
                    properties_dialog.setWindowTitle("File Properties")
                    layout = QFormLayout(properties_dialog)

                    layout.addRow("Name:", QLabel(file_name))
                    layout.addRow("Path:", QLabel(file_info.absoluteFilePath()))
                    layout.addRow("Size:", QLabel(f"{file_info.size() / 1024:.1f} KB" if file_info.isFile() else "N/A"))
                    layout.addRow("Date Modified:", QLabel(file_info.lastModified().toString("yyyy-MM-dd HH:mm:ss")))
                    layout.addRow("Type:", QLabel("Directory" if file_info.isDir() else "File"))

                    properties_dialog.exec_()
                else:
                    QMessageBox.warning(self, "Error", f"{file_name} does not exist.")
            else:
                QMessageBox.warning(self, "Error", "No item selected.")
        else:
            QMessageBox.warning(self, "Error", "No item selected.")

    def load_files(self, path):

        self.file_table.setRowCount(0)

        if path != QDir.rootPath():
            row_position = self.file_table.rowCount()
            self.file_table.insertRow(row_position)
            back_item = QTableWidgetItem("↰ Back to Parent Directory")
            back_item.setForeground(QColor(0, 255, 0))  
            self.file_table.setItem(row_position, 0, back_item)
            self.file_table.setSpan(row_position, 0, 1, 3)  

        dir_info = QDir(path)
        dir_info.setFilter(QDir.Files | QDir.Dirs | QDir.NoDotAndDotDot)
        files = dir_info.entryInfoList()

        for file_info in files:
            row_position = self.file_table.rowCount()
            self.file_table.insertRow(row_position)

            name_item = QTableWidgetItem(file_info.fileName())
            self.file_table.setItem(row_position, 0, name_item)

            date_item = QTableWidgetItem(file_info.lastModified().toString("yyyy-MM-dd HH:mm:ss"))
            self.file_table.setItem(row_position, 1, date_item)

            size_item = QTableWidgetItem(f"{file_info.size() / 1024:.1f} KB" if file_info.isFile() else "N/A")
            self.file_table.setItem(row_position, 2, size_item)

    def open_directory(self):

        selected_dir = QFileDialog.getExistingDirectory(self, "Select Directory", self.current_path)
        if selected_dir:
            self.current_path = selected_dir
            self.path_bar.setText(self.current_path)
            self.load_files(self.current_path)

    def on_file_double_click(self, row, column):

        file_name = self.file_table.item(row, 0).text()
        if file_name == "↰ Back to Parent Directory":
            self.go_back()  
        else:
            file_info = QFileInfo(os.path.join(self.current_path, file_name))

            if file_info.isDir():
                self.current_path = file_info.absoluteFilePath()
                self.path_bar.setText(self.current_path)
                self.load_files(self.current_path)
            else:
                self.open_file(file_info)

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Backspace:
            self.go_back()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:

            selected_row = self.file_table.currentRow()

            file_item = self.file_table.item(selected_row, 0)
            if file_item:
                file_name = file_item.text()
                if file_name == "↰ Back to Parent Directory": 
                    self.go_back()
                else:
                    file_info = QFileInfo(os.path.join(self.current_path, file_name))
                    if file_info.isDir():
                        self.current_path = file_info.absoluteFilePath()
                        self.path_bar.setText(self.current_path)
                        self.load_files(self.current_path)
                    else:
                        self.open_file(file_info)
            else:
                print("No file selected or invalid selection")
        else:
            super().keyPressEvent(event)

    def go_back(self):

        parent_dir = os.path.dirname(self.current_path)
        if parent_dir != self.current_path:  
            self.current_path = parent_dir
            self.path_bar.setText(self.current_path)
            self.load_files(self.current_path)

    def open_file(self, file_info):

        try:
            subprocess.run(['xdg-open', file_info.absoluteFilePath()], check=True)
        except Exception as e:
            print(f"Error opening file {file_info.fileName()}: {e}")

    def delete_item(self):

        selected_row = self.file_table.currentRow()
        file_item = self.file_table.item(selected_row, 0)

        if file_item:
            file_name = file_item.text()
            file_info = QFileInfo(os.path.join(self.current_path, file_name))

            reply = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete {file_name}?", 
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:

                try:
                    if file_info.isFile():
                        os.remove(file_info.absoluteFilePath())
                    elif file_info.isDir():
                        shutil.rmtree(file_info.absoluteFilePath())
                    self.load_files(self.current_path)  
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to delete {file_name}: {e}")

    def change_path(self):

        user_input = self.path_bar.text()
        if os.path.isdir(user_input):
            self.current_path = user_input
            self.load_files(self.current_path)
        else:

            QMessageBox.warning(self, "Invalid Path", "Path doesn't exist.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileExplorerApp()
    window.show()
    sys.exit(app.exec_())