"""
Fair Warning: This will be the most complex example in the course using more advanced maya features alongside
              more advanced python features than previous examples.
"""

# First of all let me grab the Qt module because it has somethings I want that I don't need to use often
import Qt

# I will use the following modules more often, so let me import them directly
from Qt import QtWidgets, QtCore, QtGui

# This is the logging module
# It is a much better way of logging output instead of using print statements
import logging

# We'll do a basic configuration of the loggers
logging.basicConfig()

# We want a logger specifically for this tool, so lets grab one so that we can control it on its own
logger = logging.getLogger('LightingManager')

# Loggers have different levels we can log to.
# We can configure the current level to make it disable certain logs when we don't want it.
logger.setLevel(logging.DEBUG)

# Okay, so this is kind of messy but necessary at the moment.
# While Qt.py lets us abstract the actual Qt library, there are a few things it cannot do yet and a few support libraries we need that we have to import ourtselves
# So I need to check the correct binding we're using under Qt.py
# If you're specifically using a Qt binding, then just use the import that makes sense for you. I'll elaborate below
if Qt.__binding__.startswith('PyQt'):
    # If we're using PyQt4 or PyQt5 we need to import sip
    logger.debug('Using sip')
    # So we import wrapInstance from sip and alias it to wrapInstance so that it's the same as the others
    from sip import wrapinstance as wrapInstance
    # Also PyQt uses pyqtSignal instead of Signal so we will import it and alias it to Signal
    from Qt.QtCore import pyqtSignal as Signal
elif Qt.__binding__ == 'PySide':
    # If we're using PySide (Maya 2016 and earlier), we'll use shiboken instead
    logger.debug('Using shiboken')
    # Shiboken already uses the correct names for both wrapInstance and Signal so we just need to import them without aliasing them
    from shiboken import wrapInstance
    from Qt.QtCore import Signal
else:
    # Finally, the only option left is PySide2(Maya 2017 and higher) which uses shiboken2
    logger.debug('Using shiboken2')
    # Again, this uses the correct naming so we just import without aliasing
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal

# For the import statemnets above, if you feel like simplifying the process, then just use the part that is relevant to the Maya version you're using

# This is the Maya API library for dealing with UIs
# This is the extent of the internal Maya API that we will be using directly for this course.
from maya import OpenMayaUI as omui

# Then we plan to use pyMel instead of maya.cmds for this project
# PyMel is like a layer above maya.cmds and the Maya API that bridges them together to make a more python like API
# This is nicer than using cmds which was originally made for MEL and the API which was designed for C++
# That said, it has its shortcomings that I will cover in a video which is why I haven't covered it till now
import pymel.core as pm

# Finally from the functional tools library we import partial that will be useful for craeting temporary functions
from functools import partial



class LightWidget(QtWidgets.QWidget):
    """
    Now on to the good stuff
    This is our Basic controller for controlling lights

    to display it, give it the name of a light like so

    ui = LightWidget('directionalLight1')
    ui.show()
    """

    # This is our solo signal
    # We are creating our own signal for other Qt objects to connect to
    # Qt demands that we make the signal here so it knows what the class looks like
    onSolo = Signal(bool)

    def __init__(self, light):
        # Our init function takes the name of a light

        # We then call the init from QWidget to make sure that our object is initialized properly
        super(LightWidget, self).__init__()

        # If the light is a string, we want to convert it to a PyMel object to deal with it easier
        # The isInstance checks if it is of type basestring (which includes all the various string types)
        if isinstance(light, basestring):
            light = pm.PyNode(light)

        # Then we store the pyMel node on this class
        self.light = light

        # Finally we call the buildUI method
        self.buildUI()


    def buildUI(self):
        # We create a GridLayout
        # GridLayouts are very flexible and allow us to quickly position widgets in a grid
        layout = QtWidgets.QGridLayout(self)

        # We make a checkbox with the label of our Light node's transform
        # Here you can see why PyMel is useful. Rather than passing our light's name to other cmds functions to get its parent
        #       we can simply just call a method of the light object itself.
        self.name = name = QtWidgets.QCheckBox(str(self.light.getTransform()))
        # Lets make sure its value is the same as the lights visibility
        # Again, instead of doing cmds.getAttr('%s.visibility' % self.light), this simplifies the code a lot
        name.setChecked(self.light.visibility.get())
        # We connect the toggled signal from the checkbox to a lambda. It will be called anytime the checkbox value changes
        # A lambda is another name for an unnamed function that will be called later
        # It is the same as this piece of code
        #
        # def setLightVisibility(self, val):
        #     self.light.visibility.set(val)
        #
        # I like using lambdas when the logic is very simple. If your logic is more complex, use a real function or method
        name.toggled.connect(lambda val: self.light.visibility.set(val))
        # Finally we add it to the layout in position 0, 0 (row 0, column 0)
        layout.addWidget(name, 0, 0)

        # Now we need a button to solo the light
        solo = QtWidgets.QPushButton('Solo')
        # Buttons can also be checkable, in that when you click them they will stay pressed till you unpress them
        solo.setCheckable(True)
        # Finally we connect the toggled value of the button to another lambda
        # This lambda will in turn tell our custom onSolo signal to emit with the same value it receive
        # This is the same as this piece of code
        #
        # def emitSoloSignal(self, value):
        #     self.onSolo.emit(value)
        #
        # Again, for a simple one line function that we never use again, a lambda is a good fit
        solo.toggled.connect(lambda val: self.onSolo.emit(val))
        # Then we add it to the grid layout in position (row 0, column 1)
        layout.addWidget(solo, 0, 1)

        # This will be our button to delete the light
        delete = QtWidgets.QPushButton('X')
        # The delete Light function is a little more complex so we will make it a real method and connect to it
        delete.clicked.connect(self.deleteLight)
        # We set the maximum width to 10, so that it's not super wide
        delete.setMaximumWidth(10)
        # Finally we add it to the same row, but the next column over
        layout.addWidget(delete, 0, 2)

        # We want a slider that can control the intensity of the light
        # We tell it that we want it to be horizontal by passing it the Qt value for Horizontal
        intensity = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        # We set the minimum and maximum value of the slider
        intensity.setMinimum(1)
        intensity.setMaximum(1000)
        # Then we set its current value based of the intensity of the light itself
        intensity.setValue(self.light.intensity.get())
        # We then connect its value changed signal to another lambda that sets the lights intensity
        intensity.valueChanged.connect(lambda val: self.light.intensity.set(val))
        # Finally we add it to the grid, on the next row down.
        # If you notice this takes two extra variables, which tell it how many rows and columns to occupy
        # So we are adding it to row 1, column 2 and telling it to take 1 row and 2 columns of space
        # If you don't provide the last two arguments, they default to 1 each
        layout.addWidget(intensity, 1, 0, 1, 2)

        # This will be our button to display the color of the light
        self.colorBtn = QtWidgets.QPushButton()
        # We set the width and height of the button to our liking
        self.colorBtn.setMaximumWidth(20)
        self.colorBtn.setMaximumHeight(20)
        # Finally we call a method to sat the buttons color based on the lights current color
        self.setButtonColor()
        # We then connect it to our setColor method, again something too complex to be a lambda
        self.colorBtn.clicked.connect(self.setColor)
        # Finally we add it to the grid again, at row 1, column 2 with the default sizing
        layout.addWidget(self.colorBtn, 1, 2)

        # Now this is a weird Qt thing where we tell it the kind of sizing we want it respect
        # We are saying that the widget should never be larger than the maximum space it needs
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)


    def disableLight(self, val):
        # This function takes a value, converts it to bool and then sets our checkbox to that value
        self.name.setChecked(not bool(val))

    def deleteLight(self):
        self.setParent(None)
        self.setVisible(False)
        pm.delete(self.light.getTransform())

    def setColor(self):
        lightColor = self.light.color.get()
        color = pm.colorEditor(rgbValue=lightColor)
        r,g,b,a = [float(c) for c in color.split()]

        color = (r,g,b)
        self.light.color.set(color)
        self.setButtonColor(color)

    def setButtonColor(self, color=None):
        if not color:
            color = self.light.color.get()

        assert len(color) ==  3, "You must provide a list of 3 colors"
        r,g,b = [c*255 for c in color]

        self.colorBtn.setStyleSheet('background-color: rgba(%s, %s, %s, 1.0);' % (r,g,b))




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
        scrollWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.scrollLayout = QtWidgets.QVBoxLayout(scrollWidget)


        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(scrollWidget)
        layout.addWidget(scrollArea,1, 0, 1, 2)

        self.populate()

        refreshBtn = QtWidgets.QPushButton('Refresh')
        refreshBtn.clicked.connect(self.refresh)
        layout.addWidget(refreshBtn, 2, 1)




    def refresh(self):
        while self.scrollLayout.count():
            widget = self.scrollLayout.takeAt(0).widget()
            if widget:
                widget.setVisible(False)

        self.populate()

    def populate(self):
        for light in pm.ls(type=["areaLight", "spotLight", "pointLight", "directionalLight", "volumeLight"]):
            light = pm.PyNode(light)
            self.addLight(light)


    def createLight(self):
        lightType = self.lightTypeCB.currentText()
        func = self.lightTypes[lightType]

        light = func()
        self.addLight(light)

    def isolate(self, val):
        lightWidgets = self.findChildren(LightWidget)
        for widget in lightWidgets:
            if widget !=  self.sender():
                widget.disableLight(val)

    def addLight(self, light):
        widget = LightWidget(light)
        widget.onSolo.connect(self.isolate)
        self.scrollLayout.addWidget(widget)




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



