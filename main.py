from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QFileDialog, QLabel, 
        QPushButton, QWidget, QTableWidget, QTableWidgetItem,
        QMessageBox, QCheckBox, QGroupBox)
import os
import sys
import warnings
from PlotCanvas import PlotCanvas
from Process import *

class App(QWidget):
    def __init__(self):
        super().__init__()

        self.sampleData = []
        self.ratio = [0] * 6

        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Công cụ tính toán pha màu")
        self.setGeometry(60, 60, 1000, 650)
        self.setFixedSize(1000, 650)

        self.label1 = QLabel(self)
        self.label1.setText("Các màu cơ bản")
        self.label1.move(20, 20)

        self.basicColor1CheckBox = QCheckBox("Yellow C", self)
        self.basicColor1CheckBox.resize(200, 20)
        self.basicColor1CheckBox.move(20, 50)

        self.basicColor2CheckBox = QCheckBox("Red 032C", self)
        self.basicColor2CheckBox.resize(200, 20)
        self.basicColor2CheckBox.move(20, 80)

        self.basicColor3CheckBox = QCheckBox("Rhodmine Red C", self)
        self.basicColor3CheckBox.resize(200, 20)
        self.basicColor3CheckBox.move(20, 110)

        self.basicColor4CheckBox = QCheckBox("Pink C", self)
        self.basicColor4CheckBox.resize(200, 20)
        self.basicColor4CheckBox.move(140, 50)

        self.basicColor5CheckBox = QCheckBox("Blue C", self)
        self.basicColor5CheckBox.resize(200, 20)
        self.basicColor5CheckBox.move(140, 80)

        self.basicColor6CheckBox = QCheckBox("Black C", self)
        self.basicColor6CheckBox.resize(200, 20)
        self.basicColor6CheckBox.move(140, 110)

        self.importSampleBtn = QPushButton("Nhập màu mẫu", self)
        self.importSampleBtn.resize(100, 30)
        self.importSampleBtn.move(20, 160)
        self.importSampleBtn.clicked.connect(self.importSample)

        self.sampleColorTable = QTableWidget(self)
        self.sampleColorTable.resize(180, 400)
        self.sampleColorTable.move(20, 200)
        self.sampleColorTable.setRowCount(31)
        self.sampleColorTable.setColumnCount(2)
        self.sampleColorTable.setColumnWidth(0, 70)
        self.sampleColorTable.setColumnWidth(1, 90)
        self.sampleColorTable.verticalHeader().setVisible(False)
        self.sampleColorTable.setHorizontalHeaderLabels(["Bước sóng", "Hệ số phản xạ"])
        self.sampleColorTable.horizontalHeader().setStyleSheet("::section{font-weight: bold; background-color: #eee}")
        wvl = 400
        for i in range(31):
            self.sampleColorTable.setItem(i, 0, QTableWidgetItem(str(wvl)))
            wvl += 10

        self.computeBtn = QPushButton(self)
        self.computeBtn.setIcon(QIcon('run.png'))
        self.computeBtn.setIconSize(QSize(25, 25))
        self.computeBtn.resize(40, 120)
        self.computeBtn.move(210, 200)
        self.computeBtn.clicked.connect(self.compute)

        self.ratioGroupBox = QGroupBox('Tỷ lệ pha màu', self)
        self.ratioGroupBox.resize(250, 200)
        self.ratioGroupBox.move(320, 20)
        self.ratioText = QLabel(self)
        self.ratioText.resize(200, 180)
        self.ratioText.move(350, 30)
        self.ratioText.setStyleSheet("font-weight:bold;")
        self.printRatio()

        self.sampleColorLabel = QLabel('Màu mẫu', self)
        self.sampleColorLabel.move(650, 50)
        self.sampleColorBox = QLabel(self)
        self.sampleColorBox.resize(70, 20)
        self.sampleColorBox.move(730, 48)
        self.sampleColorBox.setStyleSheet('border: 1px solid #a9a8b3')
        self.sampleColorCIELAB = QLabel('CIELAB: ', self)
        self.sampleColorCIELAB.resize(180, 40)
        self.sampleColorCIELAB.move(820, 36)

        self.computeColorLabel = QLabel('Màu pha được', self)
        self.computeColorLabel.move(650, 120)
        self.computeColorBox = QLabel(self)
        self.computeColorBox.resize(70, 20)
        self.computeColorBox.move(730, 118)
        self.computeColorBox.setStyleSheet('border: 1px solid #a9a8b3')
        self.computeColorCIELAB = QLabel('CIELAB: ', self)
        self.computeColorCIELAB.resize(180, 40)
        self.computeColorCIELAB.move(820, 106)

        self.graphView = PlotCanvas(self, width = 6, height = 3.5)
        self.graphView.move(320, 250)
        self.graphView.clear()

        self.show()

    def importSample(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Chọn tệp tin chứa thông số màu (.txt)", "./.",
                                               "All Files(*)", options = options)
        try:
            if file != '':
                self.sampleData = []
                fp = open(file, 'r')
                line = fp.readline()
                while line:
                    self.sampleData += [float(line)]
                    line = fp.readline()
                for i in range(31):
                    self.sampleColorTable.setItem(i, 1, QTableWidgetItem(str(self.sampleData[i])))
        except:
            QMessageBox.about(self, 'Lỗi', 'File đầu vào sai định dạng dữ liệu. Hãy thử lại!')

    def setSampleData(self):
        self.sampleData = [0 for i in range(31)] 
        for i in range(31):
            self.sampleData[i] = float(self.sampleColorTable.item(i, 1).text())

    def compute(self):
        basicColorChosen = ((self.basicColor1CheckBox.isChecked()) 
                        + (self.basicColor2CheckBox.isChecked() << 1)
                        + (self.basicColor3CheckBox.isChecked() << 2)
                        + (self.basicColor4CheckBox.isChecked() << 3)
                        + (self.basicColor5CheckBox.isChecked() << 4)
                        + (self.basicColor6CheckBox.isChecked() << 5))
        self.setSampleData()                
        process = Process()
        Max = 5000
        tmp  = process.compute(basicColorChosen, self.sampleData, [[0, Max]] * 6, 100, Max)
        tmp  = process.compute(basicColorChosen, self.sampleData, [[tmp[0][i] - 200, tmp[0][i] + 200] for i in range(len(tmp[0]))], 50, Max)
        tmp  = process.compute(basicColorChosen, self.sampleData, [[tmp[0][i] - 100, tmp[0][i] + 100] for i in range(len(tmp[0]))], 25, Max)
        tmp  = process.compute(basicColorChosen, self.sampleData, [[tmp[0][i] - 50, tmp[0][i] + 50] for i in range(len(tmp[0]))], 10, Max)
        tmp  = process.compute(basicColorChosen, self.sampleData, [[tmp[0][i] - 25, tmp[0][i] + 25] for i in range(len(tmp[0]))], 5, Max)
        resp = process.compute(basicColorChosen, self.sampleData, [[tmp[0][i] - 10, tmp[0][i] + 10] for i in range(len(tmp[0]))], 1, Max)
        sampleRes = resp[1]
        ratio = [i / Max for i in resp[0]]
        pos = 0
        self.ratio = [0, 0, 0, 0, 0, 0]
        if self.basicColor1CheckBox.isChecked():
            self.ratio[0] = ratio[pos]
            pos += 1
        if self.basicColor2CheckBox.isChecked():
            self.ratio[1] = ratio[pos]
            pos += 1
        if self.basicColor3CheckBox.isChecked():
            self.ratio[2] = ratio[pos]
            pos += 1
        if self.basicColor4CheckBox.isChecked():
            self.ratio[3] = ratio[pos]
            pos += 1
        if self.basicColor5CheckBox.isChecked():
            self.ratio[4] = ratio[pos]
            pos += 1
        if self.basicColor6CheckBox.isChecked():
            self.ratio[5] = ratio[pos]
            pos += 1
        self.printRatio()
        self.graphView.plot(list(range(400, 701, 10)), self.sampleData, sampleRes)

        self.setColorBox(0, Helper.sampleToRGB(self.sampleData))
        self.setColorBox(1, Helper.sampleToRGB(sampleRes))

        LAB1 = Helper.sampleToCIELAB(self.sampleData)
        LAB2 = Helper.sampleToCIELAB(sampleRes)
        self.sampleColorCIELAB.setText('CIELAB: (%.2f, %.2f, %.2f)' % (LAB1[0], LAB1[1], LAB1[2]))
        self.computeColorCIELAB.setText('CIELAB: (%.2f, %.2f, %.2f)' % (LAB2[0], LAB2[1], LAB2[2]))

        QMessageBox.about(self, 'Thông báo', 'Đã tính toán xong!')

    def printRatio(self):
        self.ratioText.setText("Yellow C: {:.2f} %\n\nRed 032C: {:.2f} %\n\nRhodmine Red C: {:.2f} %\n\nPink C: {:.2f} %\n\nBlue C: {:.2f} %\n\nBlack C: {:.2f} %".format(self.ratio[0] * 100, self.ratio[1] * 100, self.ratio[2] * 100, self.ratio[3] * 100, self.ratio[4] * 100, self.ratio[5] * 100))

    def setColorBox(self, box, RGB): ## box = 0 -> sampleColor; box = 1 -> computeColor
        styleSheet = 'border: 1px solid #a9a8b3; background-color: #' + '%02x%02x%02x' % (RGB[0], RGB[1], RGB[2])   
        if box == 0:
            self.sampleColorBox.setStyleSheet(styleSheet)
        else:
            self.computeColorBox.setStyleSheet(styleSheet)     

if __name__ == '__main__':
    os.system("color 0a")
    warnings.filterwarnings('ignore') 
    app = QApplication(sys.argv)
    exe = App()
    sys.exit(app.exec_())
