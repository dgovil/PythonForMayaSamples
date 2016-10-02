"""
Fair Warning: This will be the most complex example in the course using more advanced maya features alongside
              more advanced python features than previous examples.
"""

import Qt
from Qt import QtWidgets, QtCore
import logging

logging.basicConfig()
logger = logging.getLogger('LightingManager')
logger.setLevel(logging.DEBUG)

if Qt.__binding__.startswith('PyQt'):
    logger.debug('Using sip')
    from sip import wrapinstance as wrapInstance
elif Qt.__binding__ == 'PySide':
    logger.debug('Using shiboken')
    from shiboken import wrapInstance
else:
    logger.debug('Using shiboken2')
    from shiboken2 import wrapInstance

from maya import OpenMayaUI as omui

import pymel.core as pm
from functools import partial



class LightingManager(QtWidgets.QWidget):

    lightTypes = {
        "Point Light": pm.pointLight,
        "Spot Light": pm.spotLight,
        "Area Light": partial(pm.shadingNode, 'areaLight', asLight=True),
        "Directional Light": pm.directionalLight,
        "Volume Light": partial(pm.shadingNode, 'volumeLight', asLight=True)
    }

    def __init__(self, dock=False):
        if dock:
            parent = getDock()
        else:
            deleteDock()
            try:
                pm.deleteUI('lightingManager')
            except:
                pass

            parent = QtWidgets.QDialog(getMayaMainWindow())
            parent.setWindowTitle('Lighting Manager')
            parent.setObjectName('lightingManager')

            dlgLayout = QtWidgets.QVBoxLayout(parent)

        super(LightingManager, self).__init__(parent=parent)
        self.buildUI()
        self.parent().layout().addWidget(self)
        if not dock:
            parent.show()


    def buildUI(self):
        layout = QtWidgets.QGridLayout(self)

        self.lightTypeCB = QtWidgets.QComboBox()
        for lightType in sorted(self.lightTypes):
            self.lightTypeCB.addItem(lightType)
        layout.addWidget(self.lightTypeCB, 0, 0)

        createBtn = QtWidgets.QPushButton('Create')
        createBtn.clicked.connect(self.createLight)
        layout.addWidget(createBtn, 0, 1)

        scrollWidget = QtWidgets.QWidget()
        self.scrollLayout = QtWidgets.QVBoxLayout(scrollWidget)

        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidget(scrollWidget)
        layout.addWidget(scrollArea,1, 0, 1, 2)

        self.populate()

        refreshBtn = QtWidgets.QPushButton('Refresh')
        refreshBtn.clicked.connect(self.refresh)
        layout.addWidget(refreshBtn, 2, 1)

    def refresh(self):
        pass

    def populate(self):
        for light in pm.ls(type=["areaLight", "spotLight", "pointLight", "directionalLight", "volumeLight"]):
            light = pm.PyNode(light)
            self.addLight(light)

    def createLight(self):
        lightType = self.lightTypeCB.currentText()
        func = self.lightTypes[lightType]

        light = func()
        self.addLight(light)

    def addLight(self, light):
        print light


class LightWidget(QtWidgets.QWidget):
    def __init__(self, light):
        super(LightWidget, self).__init__()
        print light


def deleteDock(name='LightingManagerDock'):
    if pm.workspaceControl(name, query=True, exists=True):
        pm.deleteUI(name)

def getDock(name='LightingManagerDock'):
    deleteDock(name)
    ctrl = pm.workspaceControl(name, dockToMainWindow=('right', 1), label="Lighting Manager")
    qtCtrl = omui.MQtUtil_findControl(ctrl)
    ptr = wrapInstance(long(qtCtrl), QtWidgets.QWidget)

    return ptr


def getMayaMainWindow():
    win = omui.MQtUtil_mainWindow()
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    return ptr



