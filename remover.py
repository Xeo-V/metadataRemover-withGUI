import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QAction, QMessageBox, QTextEdit
from PyQt5.QtCore import Qt
from PIL import Image, ExifTags
import datetime
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Metadata Cleaner')
        self.setGeometry(300, 300, 400, 300)
        self.setStyleSheet("background-color: black; color: white;")
        
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)
        clear_metadata_action = QAction('Clear Metadata', self)
        clear_metadata_action.triggered.connect(self.clear_metadata)
        menubar.addAction(clear_metadata_action)
        
        self.metadata_display = QTextEdit(self)
        self.metadata_display.setGeometry(0, 100, 400, 200)
        self.metadata_display.setStyleSheet("background-color: black; color: white;")
        self.metadata_display.setReadOnly(True)
        
        self.file_path = None
        self.show()

    def open_file_dialog(self):
        self.metadata_display.clear()
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'All Files (*)', options=options)
        if file_path:
            self.file_path = file_path
            self.display_metadata()

    def display_metadata(self):
        try:
            if self.file_path.lower().endswith('.txt'):
                file_info = os.stat(self.file_path)
                text = f"Size: {file_info.st_size} bytes\n"
                text += f"Creation Time: {datetime.datetime.fromtimestamp(file_info.st_ctime)}\n"
                text += f"Last Access Time: {datetime.datetime.fromtimestamp(file_info.st_atime)}\n"
                text += f"Last Modification Time: {datetime.datetime.fromtimestamp(file_info.st_mtime)}\n"
                self.metadata_display.setPlainText(text)
            elif self.file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                with Image.open(self.file_path) as img:
                    info = img._getexif()
                    if info is not None:
                        for tag, value in info.items():
                            tagname = ExifTags.TAGS.get(tag, tag)
                            self.metadata_display.append(f"{tagname}: {value}")
        except Exception as e:
            QMessageBox.warning(self, 'Error', str(e))

    def clear_metadata(self):
        try:
            if self.file_path.lower().endswith('.txt'):
                os.utime(self.file_path, None)
                self.metadata_display.clear()
                QMessageBox.information(self, 'Success', 'Metadata cleared successfully!')
            elif self.file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                img = Image.open(self.file_path)
                data = img.getdata()
                img_without_exif = Image.new(img.mode, img.size)
                img_without_exif.putdata(data)
                
                options = QFileDialog.Options()
                save_path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'JPEG Images (*.jpg);;All Files (*)', options=options)
                if save_path:
                    img_without_exif.save(save_path, 'JPEG')
                    img_without_exif.close()
                    img.close()
                    self.metadata_display.clear()
                    QMessageBox.information(self, 'Success', f'Metadata cleared successfully! Saved as {save_path}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', str(e))
