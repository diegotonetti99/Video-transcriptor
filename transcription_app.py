#!/usr/bin/python
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidgetItem

from AppUI.main_page import Ui_MainWindow

import sys

from Scripts.transcriber import *


class Application(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectEvents()
        self.transcribers = []
        self.queque = []

    def closeEvent(self, event):
        for tr in self.transcribers:
            tr.join()

    def connectEvents(self):
        self.select_files_button.clicked.connect(self.select_files_clicked)
        self.start_transcription_button.clicked.connect(
            self.start_transcription_clicked)

    def select_files_clicked(self):
        dialog = QFileDialog()
        #dialog.setOptions(QFileDialog.DontUseNativeDialog)
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilter("Video files (*.mp4)")
        if dialog.exec():
            self.filenames = dialog.selectedFiles()
            self.files_list_widget.clear()
            while len(self.filenames)>0:
                file=self.filenames.pop()
                widget=QListWidgetItem(file)
                tr=Transcriber(file, self.text_viewer, self.task_completed, self.split_audio_completed, widget)
                self.transcribers.append(tr)
                self.files_list_widget.addItem(tr.widget)

    def start_transcription_clicked(self):
        if len(self.transcribers) > 0:
            tr = self.transcribers[0]
            tr.start()
            self.queque.append(tr)

    def task_completed(self, transcriber):
        """ method that happens when a transcription thread is terminated """
        print('task completed')

        # start new transcription
        index = self.transcribers.index(transcriber)
        if len(self.transcribers) > index+1 and len(self.queque) < 4:
            tr = self.transcribers[index+1]
            if not self.queque.__contains__(tr) and not tr.isEnded:
                tr.start()
                self.queque.append(tr)

        self.queque.remove(transcriber)
        self.files_list_widget.takeItem(self.files_list_widget.row(transcriber.widget))
        self.text_viewer.setText(
            'Transcriptions completed, queque length: '+str(len(self.queque)))

    def split_audio_completed(self, transcriber):
        index = self.transcribers.index(transcriber)
        if len(self.transcribers) > index+1 and len(self.queque) < 4:
            tr = self.transcribers[index+1]
            if not self.queque.__contains__(tr) and not tr.isEnded:
                tr.start()
                self.queque.append(tr)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Application()
    win.show()
    sys.exit(app.exec())
