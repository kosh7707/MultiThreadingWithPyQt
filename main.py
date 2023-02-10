from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from time import sleep
import random
from queue import Queue


class WorkQueue:
    def __init__(self):
        self.workQueue = Queue()

    def push(self, data):
        self.workQueue.put(data)

    def pop(self):
        return self.workQueue.get()

    def isEmpty(self):
        return self.workQueue.empty()


class Worker(QtCore.QObject):
    setProgressBarSignal = QtCore.pyqtSignal(tuple)

    def __init__(self, workQueue, number):
        super().__init__()
        self.number = number
        self.workQueue = workQueue

    @QtCore.pyqtSlot()
    def doWork(self):
        while True:
            if not self.workQueue.isEmpty():
                time = self.workQueue.pop()
                print("[no.{} Worker]: get time: {}".format(self.number, time))
                currentProgress = 0.0
                while currentProgress <= 100.0:
                    self.setProgressBarSignal.emit((self.number, currentProgress))
                    currentProgress += 100.0 / (time * 10.0)
                    sleep(0.1)
                sleep(0.2)
                self.setProgressBarSignal.emit((self.number, 0.0))


class MainWindow(QtWidgets.QWidget):
    addWorkSignal = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setGeometry(1100, 100, 280, 230)
        self.setFixedSize(280, 230)
        self.setWindowTitle("3 6 9 3 6 9 3 6 9")
        # font
        self.font = QtGui.QFont()
        self.font.setFamily("굴림")
        self.font.setPointSize(12)
        # centralWidget, QWidget
        self.centralWidget = QtWidgets.QWidget(self)
        self.centralWidget.setObjectName("centralWidget")
        self.centralWidget.setFont(self.font)
        # addWorkButton, QPushButton
        self.addWorkButton = QtWidgets.QPushButton(self.centralWidget)
        self.addWorkButton.setObjectName("addWorkButton")
        self.addWorkButton.setGeometry(QtCore.QRect(110, 150, 140, 60))
        self.addWorkButton.setText("일해라!")
        self.addWorkButton.clicked.connect(self.addWorkButtonClicked)
        # label1, QLabel
        self.label1 = QtWidgets.QLabel(self.centralWidget)
        self.label1.setAlignment(QtCore.Qt.AlignCenter)
        self.label1.setGeometry(QtCore.QRect(20, 20, 50, 30))
        self.label1.setText("1번")
        # label2, QLabel
        self.label2 = QtWidgets.QLabel(self.centralWidget)
        self.label2.setAlignment(QtCore.Qt.AlignCenter)
        self.label2.setGeometry(QtCore.QRect(20, 60, 50, 30))
        self.label2.setText("2번")
        # label3, QLabel
        self.label3 = QtWidgets.QLabel(self.centralWidget)
        self.label3.setAlignment(QtCore.Qt.AlignCenter)
        self.label3.setGeometry(QtCore.QRect(20, 100, 50, 30))
        self.label3.setText("3번")
        # firstWorkerProgressBar, QProgressBar
        self.firstWorkerProgressBar = QtWidgets.QProgressBar(self.centralWidget)
        self.firstWorkerProgressBar.setGeometry(QtCore.QRect(100, 20, 160, 30))
        self.firstWorkerProgressBar.setTextVisible(False)
        # secondWorkerProgressBar, QProgressBar
        self.secondWorkerProgressBar = QtWidgets.QProgressBar(self.centralWidget)
        self.secondWorkerProgressBar.setGeometry(QtCore.QRect(100, 60, 160, 30))
        self.secondWorkerProgressBar.setTextVisible(False)
        # thirdWorkerProgressBar, QProgressBar
        self.thirdWorkerProgressBar = QtWidgets.QProgressBar(self.centralWidget)
        self.thirdWorkerProgressBar.setGeometry(QtCore.QRect(100, 100, 160, 30))
        self.thirdWorkerProgressBar.setTextVisible(False)

    def addWorkButtonClicked(self):
        self.addWorkSignal.emit(random.randint(1, 10))  # To MainThread.addWork

    @QtCore.pyqtSlot(tuple)
    def setProgressBar(self, data):
        number = data[0]
        value = data[1]
        if number == 1:
            self.firstWorkerProgressBar.setValue(value)
        elif number == 2:
            self.secondWorkerProgressBar.setValue(value)
        else:
            self.thirdWorkerProgressBar.setValue(value)


class MainThread(QtCore.QObject):
    doWorkSignal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.mainWindow = MainWindow()
        self.score = 0
        self.workerCount = 3
        self.workQueue = WorkQueue()
        self.workerList = tuple([Worker(self.workQueue, i+1) for i in range(self.workerCount)])
        self.workerThreadList = tuple([QtCore.QThread() for i in range(self.workerCount)])
        self.mainWindow.addWorkSignal.connect(self.addWork)
        for i in range(self.workerCount):
            self.workerList[i].moveToThread(self.workerThreadList[i])
            self.workerThreadList[i].start()
            self.doWorkSignal.connect(self.workerList[i].doWork)
            self.workerList[i].setProgressBarSignal.connect(self.mainWindow.setProgressBar)
        self.mainWindow.show()

    def start(self):
        self.doWorkSignal.emit()

    @QtCore.pyqtSlot(int)
    def addWork(self, time):
        self.workQueue.push(time)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_DisableWindowContextHelpButton)
    mainThread = MainThread()
    mainThread.start()
    app.exec_()
    sys.exit()
