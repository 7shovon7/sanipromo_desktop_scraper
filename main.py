import os
import platform
import sys

from PySide6.QtCore import Signal, QThread, QObject
import PySide6.QtGui
import PySide6.QtWidgets
from db import DB_ACTION
from script import scrape
from ui import *
import PySide6

from constants import *


if platform.system() == 'Darwin':
    os.chdir(sys._MEIPASS)


class Worker(QObject):
    finished = Signal()
    progress = Signal(int)
    msg = Signal(str)

    def __init__(self, input_file, output_dir):
        super().__init__()
        self.output_dir = output_dir
        self.input_file = input_file

    def run(self):
        try:
            if self.input_file is not None:
                scrape(
                    input_file=self.input_file,
                    output_dir=self.output_dir,
                    progress_callback=self.report_progress,
                    progress_msg_callback=self.report_progress_msg,
                )
        except Exception as e:
            print(e)
        self.finished.emit()

    def report_progress(self, progress):
        self.progress.emit(progress)

    def report_progress_msg(self, msg):
        self.msg.emit(msg)
    
    # def start_scraping_data(self):
    #     try:
    #         if self.input_file is not None:
    #             scrape(input_file=self.input_file, output_dir=self.output_dir)
    #     except Exception as e:
    #         pass


class AppWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        # Setup UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.file_name = None
        self.thread = None
        self.ui.progressBar.setVisible(False)
        self.ui.loadingLabel.setText("")
        self.ui.fileChooseButton.clicked.connect(self.upload_file)
        self.ui.startCollectionButton.clicked.connect(self.init_collection_functionality)
    
    def upload_file(self):
        default_dir = DB_ACTION.get_data(DEFAULT_FILE_PATH_KEY)
        full_path, _ = PySide6.QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', default_dir)
        file_dir, file_name = os.path.split(full_path)
        if file_name != '':
            # A file is selected
            DB_ACTION.save_data(DEFAULT_FILE_PATH_KEY, file_dir)
            self.file_name = full_path
            self.ui.fileChosenLabel.setText(f"Selected file:\n{full_path}")
            return True
        return False
    
    def get_output_dir(self):
        output_dir = DB_ACTION.get_data(OUTPUT_DIR_KEY)
        # Choose output directory
        file_dir = PySide6.QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose Folder', output_dir)
        if file_dir != output_dir and file_dir != "":
            # A file is selected
            DB_ACTION.save_data(OUTPUT_DIR_KEY, file_dir)
        return file_dir

    def init_collection_functionality(self):
        self.ui.startCollectionButton.setEnabled(False)
        self.ui.progressBar.setVisible(True)
        self.ui.progressBar.setValue(0)
        self.ui.loadingLabel.setText('Scraping...')
        self.start_scraping_data()

    def start_scraping_data(self):
        output_dir = self.get_output_dir()
        self.thread = QThread()
        self.worker = Worker(self.file_name, output_dir)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)
        self.worker.msg.connect(self.update_progress_msg)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.perform_scrape_completion_action)
        # self.ui.fileChosenLabel.setText("Scraping...")
        self.thread.start()

    def update_progress(self, progress):
        self.ui.progressBar.setValue(progress)

    def update_progress_msg(self, msg):
        self.ui.loadingLabel.setText(msg)
    
    def perform_scrape_completion_action(self):
        self.ui.startCollectionButton.setEnabled(True)
        self.ui.loadingLabel.setText(f'Scraping completed and file is saved to your selected folder.')
        self.file_name = None
        self.thread = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec())
