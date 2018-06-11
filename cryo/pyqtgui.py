from pyqtgraph import QtCore, QtGui
import numpy as np
import sys
import datetime
import os
import subprocess
import time
import pyqtgraph as pg
#import settings as st
import takedata as td
import random as rm

class mcegui(QtGui.QWidget):
    def __init__(self):
        super(mcegui, self).__init__()
        self.init_mce()
        self.init_ui()
        self.qt_connections()

    def init_mce(self):
        self.timeinterval = 1
        for i in range(self.timeinterval):
            tempfilename = 'tempfiles/tempgraphdata%s.txt' % (i)
            tempfile = os.path.exists(tempfilename)
            if tempfile:
                delete_file = ['rm ' + tempfilename]
                subprocess.Popen(delete_file,shell=True)
        self.observer = ''
        self.datamode = ''
        self.readoutcard = ''
        self.framenumber = ''
        self.frameperfile = 374
        self.totaltimeinterval = 120
        self.currentchannel = 1
        self.oldch = 1

    def init_ui(self):
        self.setWindowTitle('MCE TIME Data')
        self.getparameters()
        self.channelselection()
        self.grid = QtGui.QGridLayout()
        self.grid.addLayout(self.parametersquit, 1, 1, 1, 1)
        self.setLayout(self.grid)

        self.grid.addLayout(self.channelbox, 3, 1, 1, 1)

        self.setGeometry(10, 10, 1920, 1080)
        self.show()

    def qt_connections(self):
        self.quitbutton.clicked.connect(self.on_quitbutton_clicked)
        self.submitbutton.clicked.connect(self.on_submitbutton_clicked)
        self.selectchannel.currentIndexChanged.connect(self.changechannel)

    def on_quitbutton_clicked(self):
        print('Quitting Application')
        run = ['mce_cmd -x stop rc%s ret_dat' %(self.readoutcard)]
        a = subprocess.Popen(run, shell=True)
        deletetemp = ['rm /data/cryo/current_data/temp.*']
        b = subprocess.Popen(deletetemp, shell=True)
        #self.runtakedata.terminate()
        sys.exit()

    def on_submitbutton_clicked(self):
        self.observer = self.enterobserver.text()
        self.datamode = self.enterdatamode.currentText()
        if self.datamode == 'Error':
            self.datamode = 0
        elif self.datamode == 'Raw':
            self.datamode = 12
        elif self.datamode == 'Low Pass Filtered':
            self.datamode = 2
        elif self.datamode == 'Mixed Mode':
            self.datamode = 10
        elif self.datamode == 'SQ1 Feedback':
            self.datamode = 1
        self.readoutcard = self.enterreadoutcard.currentIndex() + 1
        self.framenumber = self.enterframenumber.text()
        self.datarate = self.enterdatarate.text()
        self.channeldelete = self.enterchanneldelete.currentText()
        self.timestarted = datetime.datetime.utcnow()
        self.timestarted = self.timestarted.isoformat()
        if self.observer == '' or self.framenumber == '' or self.framenumber == '0' or self.datarate == '0' or self.datarate == '':
            self.parameterwarning = QtGui.QMessageBox()
            self.parameterwarning.setIcon(QtGui.QMessageBox.Warning)
            self.parameterwarning.setText('One or more parameters not entered correctly!')
            self.parameterwarning.setStandardButtons(QtGui.QMessageBox.Ok)
            self.parameterwarning.setWindowTitle('Parameter Warning')
            self.parameterwarning.buttonClicked.connect(self.on_warningbutton_clicked)
            self.parameterwarning.exec_()
        else:
            parafile = open('tempfiles/tempparameters.txt', 'w')
            parafile.write(self.observer+' ')
            parafile.write(str(self.datamode)+' ')
            parafile.write(str(self.readoutcard)+' ')
            parafile.write(self.framenumber+' ')
            parafile.write(self.datarate+' ')
            parafile.write(self.channeldelete+' ')
            parafile.write(self.timestarted+' ')
            parafile.close()

            editdatarate = ['mce_cmd -x wb cc data_rate %s' % (self.datarate)]
            a = subprocess.call(editdatarate, shell=True)

            parameteroutput = QtGui.QVBoxLayout()

            self.observertext = QtGui.QLabel()
            self.datamodetext = QtGui.QLabel()
            self.readoutcardtext = QtGui.QLabel()
            self.framenumbertext = QtGui.QLabel()
            self.dataratetext = QtGui.QLabel()
            self.channeldeletetext = QtGui.QLabel()
            self.timestartedtext = QtGui.QLabel()

            self.observertext.setText('Observer: %s' % (self.observer))
            self.datamodetext.setText('Datamode: %s' % (self.datamode))
            self.readoutcardtext.setText('Readout Card: %s' % (self.readoutcard))
            self.framenumbertext.setText('Frame Number: %s' % (self.framenumber))
            self.dataratetext.setText('Data Rate: %s' % (self.datarate))
            self.channeldeletetext.setText('Delete Old Channels: %s' % (self.channeldelete))
            self.timestartedtext.setText('Time Started: %s' % (self.timestarted))


            parameteroutput.addWidget(self.observertext)
            parameteroutput.addWidget(self.datamodetext)
            parameteroutput.addWidget(self.readoutcardtext)
            parameteroutput.addWidget(self.framenumbertext)
            parameteroutput.addWidget(self.dataratetext)
            parameteroutput.addWidget(self.channeldeletetext)
            parameteroutput.addWidget(self.timestartedtext)

            self.grid.addLayout(parameteroutput, 2, 1, 1, 1)

            print('Observer: %s' % (self.observer))
            print('Datamode: %s' % (self.datamode))
            print('Readout Card: %s' % (self.readoutcard))
            print('Frame Number: %s' % (self.framenumber))
            print('Data Rate: %s' % (self.datarate))
            print('Delete Old Channels: %s' % (self.channeldelete))
            print('Time Started: %s' % (self.timestarted))

            self.frameperfile = (50 * 10 ** 6) / (33 * 90 * int(self.datarate))
            print('Frame per file: %s' % (self.frameperfile))

            self.initplot()

    def on_warningbutton_clicked(self):
        self.observer = ''
        self.datamode = ''
        self.readoutcard = ''
        self.framenumber = ''

    def getparameters(self):
        self.parametersquit = QtGui.QVBoxLayout()

        self.enterobserver = QtGui.QLineEdit('Jake')
        self.enterdatamode = QtGui.QComboBox()
        self.enterdatamode.addItems(['Error', 'Raw', 'Low Pass Filtered', 'Mixed Mode', 'SQ1 Feedback'])
        self.enterreadoutcard = QtGui.QComboBox()
        for i in range(8):
            if i < 4:
                self.enterreadoutcard.addItem('MCE 1 RC %s' % (i % 4 + 1))
            else:
                self.enterreadoutcard.addItem('MCE 2 RC %s' % (i % 4 + 1))
        self.enterframenumber = QtGui.QLineEdit('1350000')
        self.enterdatarate = QtGui.QLineEdit('45')
        self.enterchanneldelete = QtGui.QComboBox()
        self.enterchanneldelete.addItems(['No', 'Yes'])
        self.submitbutton = QtGui.QPushButton('Submit')

        self.parameters = QtGui.QFormLayout()
        self.parameters.addRow('Observer', self.enterobserver)
        self.parameters.addRow('Datamode', self.enterdatamode)
        self.parameters.addRow('Readout Card', self.enterreadoutcard)
        self.parameters.addRow('Frame Number', self.enterframenumber)
        self.parameters.addRow('Data Rate', self.enterdatarate)
        self.parameters.addRow('Delete Old Channels', self.enterchanneldelete)
        self.parameters.addRow(self.submitbutton)

        self.parametersquit.addLayout(self.parameters)

        self.quitbutton = QtGui.QPushButton('Quit')
        self.parametersquit.addWidget(self.quitbutton)

    def channelselection(self):
        #tempfile = open('tempfiles/tempchannel.txt', 'w')
        #tempfile.write('1')
        #tempfile.close()

        self.channelbox = QtGui.QVBoxLayout()

        self.selectchannel = QtGui.QComboBox()
        self.selectchannel.addItems(['1', '2', '3', '4', '5', '6', '7', '8'])

        self.channelbox.addWidget(self.selectchannel)

    def changechannel(self):
        #tempfile = open('tempfiles/tempchannel.txt', 'w')
        self.currentchannel = int(self.selectchannel.currentText())
        #tempfile.write(self.selectchannel.currentText())
        #tempfile.close()
        #print(self.selectchannel.currentText())
        print(self.currentchannel)

    def initkmirrordata(self):
        self.parallacticangle = rm.randint(10, 170)
        self.positionalerror = rm.randint(0, 90)

        self.parallacticangletext = QtGui.QLabel()
        self.positionalerrortext = QtGui.QLabel()

        self.parallacticangletext.setText('Parallactic Angle: %s' % (self.parallacticangle))
        self.positionalerrortext.setText('Positonal Error: %s' % (self.positionalerror))

        self.kmirrordatatext = QtGui.QVBoxLayout()

        self.kmirrordatatext.addWidget(self.parallacticangletext)
        self.kmirrordatatext.addWidget(self.positionalerrortext)

        self.grid.addLayout(self.kmirrordatatext, 4, 1, 1, 1)

    def updatekmirrordata(self):
        self.parallacticangle = rm.randint(10, 170)
        self.positionalerror = rm.randint(0, 90)

        self.parallacticangletext.setText('Parallactic Angle: %s' % (self.parallacticangle))
        self.positionalerrortext.setText('Positonal Error: %s' % (self.positionalerror))

    def initplot(self):
        changedatamode = ["mce_cmd -x wb rc%s data_mode %s" % (self.readoutcard, self.datamode)]
        b = subprocess.Popen(changedatamode, shell=True)
        run = ["mce_run temp %s %s --sequence=%s" %(self.framenumber, self.readoutcard, self.frameperfile)]
        c = subprocess.Popen(run, shell=True)

        self.n_intervals = 1

        self.starttime = datetime.datetime.utcnow()

        if self.readoutcard == 'All':
            self.runtakedata = subprocess.call(['python', 'takedataall.py', str(self.n_intervals)])
        else:
        #    self.runtakedata = subprocess.call(['python', 'takedata.py', str(self.n_intervals)])
            self.z, self.graphdata = td.takedata(self.n_intervals, self.currentchannel)

        self.data = [0, 0, 0]

        self.mcegraphdata = pg.ScatterPlotItem()
        #self.graphwin = pg.GraphicsWindow()
        #self.graphwin.setWindowTitle('MCE TIME Data')

        #self.mcegraph = self.graphwin.addPlot(col=2)
    	self.mcegraph = pg.PlotWidget()

    	self.grid.addWidget(self.mcegraph, 1, 5, 2, 3)

        self.mcegraph.setLabel('bottom', 'Time', 's')
        self.mcegraph.setLabel('left', 'Counts')
        self.mcegraph.setTitle('MCE TIME Data')

        self.initheatmap()
        self.initkmirrordata()
        self.updateplot()

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.moveplot)
        self.timer.start(1000 * self.timeinterval)

    def moveplot(self):
        self.n_intervals+=self.timeinterval

        self.starttime = datetime.datetime.utcnow()

        if self.readoutcard == 'All':
            self.runtakedata = subprocess.call(['python', 'takedataall.py', str(self.n_intervals)])
        else:
        #    self.runtakedata = subprocess.call(['python', 'takedata.py', str(self.n_intervals)])
            self.z, self.graphdata = td.takedata(self.n_intervals, self.currentchannel)

        self.updateheatmap()
        self.updatekmirrordata()
        self.updateplot()

    def updateplot(self):
        #if self.n_intervals == 1:
        #    while not os.path.isfile('tempfiles/tempgraphdata%s.txt' % (0)):
        #        continue
        #    time.sleep(0.1)
        #self.runtakedata.terminate()
        #tempfile = open('tempfiles/tempgraphdata%s.txt' % (0), 'r')
        #ch = tempfile.readline().strip()
        ch = self.graphdata[1]
        #if not ch:
        #    ch = 1
        #else:
        #    ch = int(ch)
        #a = tempfile.readline().strip()
        a = self.graphdata[0]
        print('gui %s %s' % (self.n_intervals, a))
        #a = int(a)
        #datagrab = tempfile.readline().strip().split()
        #xy = []
        pointcolor = []
        x = []
        y = self.graphdata[2][:self.frameperfile]
        for i in range(self.frameperfile):
            masterx = i / 374.0
            x.append(self.n_intervals + masterx - 1)
            #y.append(float(datagrab[i]))
            if ch == 1:
                pointcolor.append(pg.mkBrush('b'))
            elif ch == 2:
                pointcolor.append(pg.mkBrush('r'))
            elif ch == 3:
                pointcolor.append(pg.mkBrush('g'))
            elif ch == 4:
                pointcolor.append(pg.mkBrush('y'))
            elif ch == 5:
                pointcolor.append(pg.mkBrush('c'))
            elif ch == 6:
                pointcolor.append(pg.mkBrush('m'))
            elif ch == 7:
                pointcolor.append(pg.mkBrush('k'))
            elif ch == 8:
                pointcolor.append(pg.mkBrush('w'))

        #tempfile.close()
        if self.n_intervals == 1 or self.n_intervals % self.totaltimeinterval == 2:
            self.data[0] = x
            self.data[1] = y
        else:
            self.data[0].extend(x)
            self.data[1].extend(y)
        #print(len(pointcolor))
        #print(len(x))
        #print(len(y))
        x = np.asarray(x)
        y = np.asarray(y)
        if self.n_intervals == 1:
            self.mcegraph.addItem(self.mcegraphdata)
            self.mcegraph.setXRange(self.n_intervals - 1, self.n_intervals + self.totaltimeinterval - 1, padding=0)
            self.mcegraphdata.setData(x, y, brush=pointcolor)
            self.oldch = ch
        elif self.n_intervals % self.totaltimeinterval == 1:
            if self.n_intervals == self.totaltimeinterval + 1:
                self.oldmcegraphdata = pg.PlotCurveItem()
                #self.oldmcegraph = self.graphwin.addPlot(col=1)
                self.oldmcegraph = pg.PlotWidget()
                self.grid.addWidget(self.oldmcegraph, 1, 2, 2, 3)
                self.oldmcegraph.setLabel('bottom', 'Time', 's')
                self.oldmcegraph.setLabel('left', 'Counts')
                self.oldmcegraph.setTitle('Old MCE TIME Data')
                self.oldmcegraph.addItem(self.oldmcegraphdata)
            self.oldmcegraph.setXRange(self.data[0][0], self.data[0][-1], padding=0)
            self.oldmcegraphdata.setData(self.data[0], self.data[1])
            self.mcegraphdata.clear()
            self.mcegraph.setXRange(self.n_intervals - 1, self.n_intervals + self.totaltimeinterval - 1, padding=0)
            self.mcegraphdata.setData(x, y, brush=pointcolor)
            self.data = [0, 0, 0]
        else:
            if self.channeldelete == 'Yes' and self.oldch != ch:
                self.mcegraphdata.clear()
                self.mcegraphdata.setData(x, y, brush=pointcolor)
            else:
                self.mcegraphdata.addPoints(x, y, brush=pointcolor)
            self.oldch = ch
        self.endtime = datetime.datetime.utcnow()
        self.timetaken = self.endtime - self.starttime
        print('Time taken: %s' % (self.timetaken))

    def initheatmap(self):
        z = np.asarray(self.z)
        z.astype(int)
        #print(z)
        self.heatmapplot = pg.PlotItem()
        self.heatmapplot.setLabel('bottom', 'Row')
        self.heatmapplot.setLabel('left', 'Channel')
        self.heatmapplot.setXRange(0, 8, padding=0)
        self.heatmapplot.setYRange(0, 32, padding=0)
        self.heatmap = pg.ImageView(view= self.heatmapplot)
        self.heatmap.setPredefinedGradient('thermal')
        self.heatmap.setImage(z)
        if self.frameperfile == 11:
            #self.heatmap.setPredefinedGradient('flame')
            self.heatmap.setLevels(60, 260)
        else:
            self.heatmap.setLevels(100, 190)

        #self.heatmap.setYRange
        #self.heatmap.setTitle('MCE Heatmap')
        #self.heatmap = pg.ImageItem(z)
        #self.heatmapwin.addItem(self.heatmap)
        self.grid.addWidget(self.heatmap, 3, 2, 2, 5)

    def updateheatmap(self):
        z = np.asarray(self.z)
        z.astype(int)
        #print(z)
        self.heatmap.setImage(z)
        if self.frameperfile == 11:
            #self.heatmap.setPredefinedGradient('flame')
            self.heatmap.setLevels(60, 260)
        else:
            self.heatmap.setLevels(100, 190)

def main():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('MCE TIME Data')
    ex = mcegui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
