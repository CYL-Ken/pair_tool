from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QTimer, QRect, QRectF, Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPainterPath, QPen

class SwitchButton(QtWidgets.QWidget):
    checkedChanged = pyqtSignal(bool)
    def __init__(self,parent=None):
        super(QtWidgets.QWidget, self).__init__(parent)

        self.checked = False
        self.bgColorOff = QColor("#DBE2EF")
        self.bgColorOn = QColor("#DBE2EF")

        self.sliderColorOff = QColor("#F9F7F7")
        self.sliderColorOn = QColor("#3F72AF")

        self.textColorOff = QColor("#112D4E")
        self.textColorOn = QColor("#112D4E")

        self.textOff = "OFF"
        self.textOn = "ON"

        self.space = 2
        self.rectRadius = 5

        self.step = self.width() // 50
        self.startX = 0
        self.endX = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateValue)

        self.setFont(QFont("Microsoft Yahei", 10))
        
        
    def init_button(self):
        self.checked = True
        self.startX = (self.width() - self.height())


    def updateValue(self):
        if self.checked:
            if self.startX < self.endX:
                self.startX = self.startX + self.step
            else:
                self.startX = self.endX
                self.timer.stop()
        else:
            if self.startX  > self.endX:
                self.startX = self.startX - self.step
            else:
                self.startX = self.endX
                self.timer.stop()

        self.update()


    def mousePressEvent(self,event):
        self.checked = not self.checked
        self.checkedChanged.emit(self.checked)

        self.step = self.width() // 50
    
        if self.checked:
            self.endX = self.width() - self.height()
        else:
            self.endX = 0
        self.timer.start(5)

    def paintEvent(self, evt): 
        painter = QPainter()

        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)


        self.drawBg(evt, painter)
        
        self.drawSlider(evt, painter)
        
        self.drawText(evt, painter)

        painter.end()


    def drawText(self, event, painter):
        painter.save()

        if self.checked:
            painter.setPen(self.textColorOn)
            painter.drawText(0, 0, self.width() // 2 + self.space * 2, self.height(), Qt.AlignCenter, self.textOn)
        else:
            painter.setPen(self.textColorOff)
            painter.drawText(self.width() // 2, 0,self.width() // 2 - self.space, self.height(), Qt.AlignCenter, self.textOff)

        painter.restore()


    def drawBg(self, event, painter):
        painter.save()
        painter.setPen(Qt.NoPen)

        if self.checked:
            painter.setBrush(self.bgColorOn)
        else:
            painter.setBrush(self.bgColorOff)

        rect = QRect(0, 0, self.width(), self.height())
        
        radius = rect.height() // 2
        
        circleWidth = rect.height()

        path = QPainterPath()
        path.moveTo(radius, rect.left())
        path.arcTo(QRectF(rect.left(), rect.top(), circleWidth, circleWidth), 90, 180)
        path.lineTo(rect.width() - radius, rect.height())
        path.arcTo(QRectF(rect.width() - rect.height(), rect.top(), circleWidth, circleWidth), 270, 180)
        path.lineTo(radius, rect.top())

        painter.drawPath(path)
        painter.restore()


    def drawSlider(self, event, painter):
        painter.save()

        if self.checked:
            painter.setBrush(self.sliderColorOn)
        else:
            painter.setBrush(self.sliderColorOff)

        rect = QRect(0, 0, self.width(), self.height())
        sliderWidth = rect.height() - self.space * 2
        sliderRect = QRect(self.startX + self.space, self.space, sliderWidth, sliderWidth)
        painter.drawEllipse(sliderRect)

        painter.restore()