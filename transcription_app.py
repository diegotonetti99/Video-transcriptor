#!/usr/bin/python
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

from AppUI.main_page import Ui_MainWindow

import sys

from Scripts.transcriber import *

class Application(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectEvents()
        self.transcribers=[]

    def closeEvent(self,event):
        for tr in self.transcribers:
            tr.join()

    def connectEvents(self):
        self.select_files_button.clicked.connect(self.select_files_clicked)
        self.start_transcription_button.clicked.connect(
            self.start_transcription_clicked)

    def select_files_clicked(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilter("Video files (*.mp4)")
        if dialog.exec():
            self.filenames=dialog.selectedFiles()
            self.files_list_widget.addItems(self.filenames)

    def start_transcription_clicked(self):
        # do while there are files left
        while len(self.filenames)>0:
            # if app hasn't started 4 threads yet create a new thread
            if len(self.transcribers)<4:
                file=self.filenames.pop()
                self.text_viewer.setText('Transcripting ')
                tr=Transcriber(file,self.text_viewer,self.task_completed)
                tr.start()
                self.transcribers.append(tr)
            else: 
                # if 4 threads are executing exit method
                break
    
    def task_completed(self, transcriber):
        """ method that happens when a transcription thread is terminated """
        print('task completed')
        #transcriber.join()
        self.transcribers.remove(transcriber)
        self.text_viewer.setText('Transcriptions completed')
        # start new transcription
        self.start_transcription_clicked()
            
            


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Application()
    win.show()
    sys.exit(app.exec())
