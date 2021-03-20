# USE THIS TO INSTALL STUFF: "pip install PySide2 pyqtgraph"
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLayout, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy, QLabel, QMainWindow, QFrame, QTabWidget, QComboBox
from PySide2.QtCore import QTimer
from pyqtgraph import PlotWidget, plot
from PySide2.QtSerialPort import QSerialPort, QSerialPortInfo
from PySide2.QtGui import QFont
import pyqtgraph as pg
import sys, os, minimalmodbus
from random import randint

# Create Application
app = QApplication([])
appFont = QFont()
appFont.setPointSize(15)

#controller = minimalmodbus.Instrument('COM20', 1)
controller = None

# Create Modbus Object
controllers = []

# Setup Style
style = open('qdarkstyle/style.qss')
app.setStyleSheet(style.read())

# first page layou
tab1 = QWidget()
x = []  # time points
y = []  # data points

graph = pg.PlotWidget()
graph.enableMouse(False)
graph.setBackground((48,48,48))
graph.setTitle("Plot of random values from 0 to 100")
graph.addLegend()
graph.showGrid(x = True, y = True)
graph.setLabel("left", "Random Value")
graph.setLabel("bottom", "Increment")

pen = pg.mkPen(color=(0,0,255))
line = graph.plot(x, y, pen = pen)

# startStopButton Behavior
def runControllers():
    global controller
    if not controller:
        return
    if (startStopButton.isChecked()):
        controller.write_register(75, 1)
    else:
        controller.write_register(75, 0)

# startStopButton
startStopButton = QPushButton("Start")
startStopButton.setCheckable(True)
startStopButton.setMaximumWidth(200)
startStopButton.setMaximumHeight(75)
startStopButton.setFont(appFont)
startStopButton.setDisabled(True)
startStopButton.toggled.connect(runControllers) # connect the function to the action

# Com Port Selection
portSelectBox = QComboBox()
portSelectBox.setFont(appFont)
def refrershPorts():
    portSelectBox.clear()
    for port in QSerialPortInfo.availablePorts():
        portSelectBox.addItem("(" + port.portName() + ") " + port.description())

refreshPortsButton = QPushButton("Refresh Ports")
refreshPortsButton.setFont(appFont)
refreshPortsButton.released.connect(refrershPorts)

def modbusUpdate():
    if (controller == None):
        return
    
modbusUpdateTimer = QTimer()
modbusUpdateTimer.setInterval(50)
modbusUpdateTimer.timeout.connect(modbusUpdate)

def connectToPort():
    if (connectButton.isChecked()):
        port = QSerialPortInfo.availablePorts()[portSelectBox.currentIndex()].portName()
        global controller 
        controller = minimalmodbus.Instrument(port, 1)
        controller.serial.timeout = .2
        controller.serial.baudrate = 115200
        controller.serial.bytesize = 8
        controller.serial.parity = 'N'
        controller.serial.stopbits = 1
        modbusUpdateTimer.start()
        graphUpdateTimer.start()
        if (controller != None):
            print("controller connected and started reading modbus")
        startStopButton.setEnabled(True)
    else:
        controller = None
        modbusUpdateTimer.stop()
        graphUpdateTimer.stop()

connectButton = QPushButton("Connect")
connectButton.setCheckable(True)
connectButton.setFont(appFont)
connectButton.toggled.connect(connectToPort)

tab1Layout = QGridLayout()
actionLayout = QVBoxLayout()
portSelectLayout = QHBoxLayout()
tab1Layout.columnCount = 2
tab1Layout.rowCount = 2
tab1Layout.setColumnStretch(0, 2)
tab1Layout.setColumnStretch(1, 1)

# actionLayout.setSizeConstraint()
actionLayout.addWidget(startStopButton)
portSelectLayout.setStretch(0, 1)
portSelectLayout.addWidget(refreshPortsButton)
portSelectLayout.setStretch(1, 4)
portSelectLayout.addWidget(portSelectBox)
portSelectLayout.setStretch(2, 2)
portSelectLayout.addWidget(connectButton)
actionLayout.addLayout(portSelectLayout)

tab1Layout.addWidget(graph, 0, 0)
tab1Layout.addLayout(actionLayout, 0, 1)

tab1.setLayout(tab1Layout)

# Setup Tabs
tabs = QTabWidget()
tabs.setTabPosition(QTabWidget.South)
tab2 = QWidget()
tab3 = QWidget()
tabs.addTab(tab1, "Tab 1")
tabs.addTab(tab2, "Tab 2")
tabs.addTab(tab3, "Tab 3")

# Setup Graph Update
def updateGraph():
    if len(x) > 1000:
        x.remove(x[0])
    if len(x) == 0:
        x.append(0)
    else:
        x.append(x[-1] + 1)

    if len(y) > 1000:
        y.remove(y[0])
    value = controller.read_register(77, number_of_decimals = 1)
    y.append(value)
    line.setData(x, y)
    
graphUpdateTimer = QTimer()
graphUpdateTimer.setInterval(50)
graphUpdateTimer.timeout.connect(updateGraph)

# Window Setup
win = QMainWindow()
win.setCentralWidget(tabs)
win.resize(800, 480)
win.show()
sys.exit (app.exec_())