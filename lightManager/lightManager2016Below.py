"""
This is the same as the lightManager code but for Maya 2016 and Below which use the dockControl instead of the workspaceControl.
The main changes are in the __init__ method of the LightManager class, the getDock function and the deleteDock function

Fair Warning: This will be the most complex example in the course using more advanced maya features alongside
              more advanced python features than previous examples.
"""

# First of all let me grab the Qt module because it has somethings I want that I don't need to use often
import json
import os

import Qt

# I will use the following modules more often, so let me import them directly
import time
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
            logger.debug('Converting node to a PyNode')
            light = pm.PyNode(light)

        # We might also get passed the transform instead of the light shape, either as a PyNode or a name.
        # So we'll check if it's a transform node and then get the shape
        if isinstance(light, pm.nodetypes.Transform):
            light = light.getShape()

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
        # When we delete the light, we need to also delete our widget
        # So lets set our parent to Nothing. This will remove it from the manager UI and tells Qt to stop holding onto it
        self.setParent(None)
        # There is a period of time before Qt deletes it after we tell it to remove it
        # So lets mark its visibility to False
        self.setVisible(False)
        # Then we tell instruct it to delete it later just in case it hasn't gotten the hint yet
        self.deleteLater()

        # We only delete the light itself after the widget is deleted so that in the event of an error, we don't do any damage to the scene
        # We use the light's transform to make sure we are deleting at the transform level and not just the shape under it
        pm.delete(self.light.getTransform())

    def setColor(self):
        # First of all we get the color values from the light. This will be a list of 3 floats
        lightColor = self.light.color.get()
        # Then we provide this to the maya's color editor which gives us back the color the user specified
        color = pm.colorEditor(rgbValue=lightColor)

        # Annoyingly, it gives us back a string instead of a list of numbers.
        # So we split the string, and then convert it to floats
        r, g, b, a = [float(c) for c in color.split()]

        # We then use the r,g,b to set the colors on the light and the button
        color = (r, g, b)
        self.light.color.set(color)
        self.setButtonColor(color)

    def setButtonColor(self, color=None):
        # This function sets the color on the color picker button
        # If no color is provided, we get the color from the light
        if not color:
            # We use pymels methods to query the value
            color = self.light.color.get()

        # We make sure that any provided color is a list of 3 items
        # Assert is a one liner that is similar to this piece of code:
        #
        # if not len(color) == 3:
        #       raise Exception("You must provide a list of 3 colors")
        #
        # It is generally useful for validating inputs with simple checks
        assert len(color) == 3, "You must provide a list of 3 colors"

        # Finally everything gives us the r,g,b in normalized floats from 0 to 1
        # Qt expects it in integer values from 0 to 255
        # So we multiply the members of color by 255 to get the correct number
        r, g, b = [c * 255 for c in color]

        # Qt lets us style objects using CSS similar to in websites
        # So we give it a CSS string with the correct r,g,b values and a full alpha
        self.colorBtn.setStyleSheet('background-color: rgba(%s, %s, %s, 1.0);' % (r, g, b))


class LightingManager(QtWidgets.QWidget):
    """
    This is the main lighting manager.
    To call it we just do

    LightingManager(dock=True) and it will display docked, otherwise dock=False will display it as a window

    """

    # This is a dictionary of Light types to use for the Manager.
    # The Key is the name that will be displayed in the UI
    # The Value is the function that will be called
    lightTypes = {
        "Point Light": pm.pointLight,
        "Spot Light": pm.spotLight,
        # This is our first exposure to partial
        # Partial is like a lambda, and in most cases are identical.
        # The difference is lambdas get their values when they run, partials get their values when you create it
        # In this case, we are saying make a partial function to call pm.shadingNode and everything else will be arguments to it
        # This is the same as
        #
        # def createAreaLight(self):
        #     pm.shadingNode('areaLight', asLight=True)
        #
        # But it can be convenient to just use a partial rather than making functions for everything
        "Area Light": partial(pm.shadingNode, 'areaLight', asLight=True),
        "Directional Light": pm.directionalLight,
        "Volume Light": partial(pm.shadingNode, 'volumeLight', asLight=True)
    }

    def __init__(self, dock=False):
        # First lets delete a dock if we have one so that we aren't creating more than we neec
        deleteDock()
        # Then if we have a UI called lightingManager, we'll delete it so that we can only have one instance of this
        # A try except is a very important part of programming when we don't want an error to stop our code
        # We first try to do something and if we fail, then we do something else.
        try:
            pm.deleteUI('lightingManager')
        except:
            logger.debug('No previous UI exists')
        # <=Maya2016: For Maya 2016 and below we always put it inside a QDialog and only dock at the end of this __init__
        # Then we create a new dialog and give it the main maya window as its parent
        # we also store it as the parent for our current UI to be put inside
        parent = QtWidgets.QDialog(parent=getMayaMainWindow())
        # We set its name so that we can find and delete it later
        # <=Maya2016: This also lets us attach the light manager to our dock control
        parent.setObjectName('lightingManager')
        # Then we set the title
        parent.setWindowTitle('Lighting Manager')

        # Finally we give it a layout
        dlgLayout = QtWidgets.QVBoxLayout(parent)

        # Now we are on to our actual widget
        # We've figured out our parent, so lets send that to the QWidgets initialization method
        super(LightingManager, self).__init__(parent=parent)

        # We call our buildUI method to construct our UI
        self.buildUI()

        # Now we can tell it to populate with widgets for every light
        self.populate()

        # We then add ourself to our parents layout
        self.parent().layout().addWidget(self)
        # Finally if we're not docked, then we show our parent
        parent.show()

        # <=Maya2016: For Maya 2016 and below we need to create the dock after we create our widget's parent window
        if dock:
            getDock()

    def buildUI(self):
        # Like in the LightWidget we show our
        layout = QtWidgets.QGridLayout(self)

        # We create a combobox
        # Comboboxes are essentially dropdown selectionwidgets
        self.lightTypeCB = QtWidgets.QComboBox()
        # We populate it with the items in our lightTypes dictionary
        # I like to have my items alphabetically so I sort it to begin with
        for lightType in sorted(self.lightTypes):
            # We add the option to the combobox
            self.lightTypeCB.addItem(lightType)
        # Finally we add it to the layout in row 0, column 0
        # We tell it take 1 row and two columns worth of space
        layout.addWidget(self.lightTypeCB, 0, 0, 1, 2)

        # We create a button to create the chosen lights
        createBtn = QtWidgets.QPushButton('Create')
        # We connect the button so it calls the createLight method when its clicked
        createBtn.clicked.connect(self.createLight)
        # We add it to the layout in row 0, column 2
        layout.addWidget(createBtn, 0, 2)

        # We want to put all the LightWidgets inside a scrolling container
        # We first need a container widget
        scrollWidget = QtWidgets.QWidget()
        # We want to make sure this widget only tries to be the maximum size of its contents
        scrollWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        # Then we give it a vertical layout because we want everything arranged vertically
        self.scrollLayout = QtWidgets.QVBoxLayout(scrollWidget)

        # Finally we create a scrollArea that will be in charge of scrolling its contents
        scrollArea = QtWidgets.QScrollArea()
        # Make sure it's resizable so it resizes as the UI grows or shrinks
        scrollArea.setWidgetResizable(True)
        # Then we set it to use our container widget to scroll
        scrollArea.setWidget(scrollWidget)
        # Then we add this scrollArea to the main layout, at row 1, column 0
        # We tell it to take 1 row and 3 columns of space
        layout.addWidget(scrollArea, 1, 0, 1, 3)

        # We add the save button to save our lights
        saveBtn = QtWidgets.QPushButton('Save')
        # When clicked it will call the saveLights method
        saveBtn.clicked.connect(self.saveLights)
        # We add it to row 2, column 0
        layout.addWidget(saveBtn, 2, 0)

        # We also add an import button to import our lights
        importBtn = QtWidgets.QPushButton('Import')
        # When clicked it will call the importLights method
        importBtn.clicked.connect(self.importLights)
        # We add it to row 2, column 1
        layout.addWidget(importBtn, 2, 1)

        # We need a refresh button to manually force the UI to refresh on changes
        refreshBtn = QtWidgets.QPushButton('Refresh')
        # We'll connect this to the refresh method
        refreshBtn.clicked.connect(self.refresh)
        # Finally we add it to the layout at row 2, column 2
        layout.addWidget(refreshBtn, 2, 2)

    def refresh(self):
        # This is one of the rare times I use a while loop
        # It could be done in a for loop, but I want to show you how a while loop would look

        # We say that while the scrollLayout.count() gives us any Truth-y value we will run the logic
        # count() tells us how many children it has
        while self.scrollLayout.count():
            # We take the first child of the layout, and ask for the associated widget
            # Taking the child, means that it is no longer under the care of its parent
            widget = self.scrollLayout.takeAt(0).widget()
            # Some objects don't have widgets, so we'll only run this for objects with a widget
            if widget:
                # We set the visibility to False because there is a period where it will still be alive
                widget.setVisible(False)
                # Then we tell it to kill the widget when it can
                widget.deleteLater()

        # Finally we tell it to populate again
        self.populate()

    def populate(self):
        # We list all the existing lights in the scene by type of the lights
        for light in pm.ls(type=["areaLight", "spotLight", "pointLight", "directionalLight", "volumeLight"]):
            # PyMel gives us back a PyNode for each object it lists
            # We will pass this to the addLight method that will create the widget for it
            self.addLight(light)

    def saveLights(self):
        # We'll now save the lights down to a JSON file that can be shared as a preset

        # The properties dictionary will hold all the light properties to save down
        properties = {}

        # First lets get all the light widgets that exist in our manager
        for lightWidget in self.findChildren(LightWidget):
            # For each widget we can get its' light object
            light = lightWidget.light

            # Then we need to get its transform node
            transform = light.getTransform()

            # Finally we add it to the dictionary.
            # The key will be the name of the transform which we get by converting the node to a string
            # Then we simply query the attributes of the light that we want to save down
            properties[str(transform)] = {
                'translate': list(transform.translate.get()),
                'rotation': list(transform.rotate.get()),
                'lightType': pm.objectType(light),
                'intensity': light.intensity.get(),
                'color': light.color.get()
            }

        # We fetch the light manager directory to save in
        directory = self.getDirectory()

        # We then construct the name of the lightFile to save
        # We'll be using time.strftime to construct a name using the current time
        # %m%d will give 0701 for July 1st (month and day)
        # so we'd end up with a name like lightFile_0701.json stored in our directory
        lightFile = os.path.join(directory, 'lightFile_%s.json' % time.strftime('%m%d'))

        # Next we open the file to write
        with open(lightFile, 'w') as f:
            # Then we use json to write out our file to this location
            json.dump(properties, f, indent=4)

        # A helpful logger call tells us where the file was saved to.
        logger.info('Saving file to %s' % lightFile)

    def getDirectory(self):
        # The getDirectory method will give us back the name of our library directory and create it if it doesn't exist
        directory = os.path.join(pm.internalVar(userAppDir=True), 'lightManager')
        if not os.path.exists(directory):
            os.mkdir(directory)
        return directory

    def importLights(self):
        # This function goes over importing the lights back in.
        # We first find the directory
        directory = self.getDirectory()

        # Then we use the QFileDialog to open a file browser so we can select the json file to import
        # We give it self as the part, a name for the browser and tell it which directory to open to
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Light Browser", directory)

        # Next we open the fileName in read mode
        with open(fileName[0], 'r') as f:
            # Then we use json to load the file into a dictionary
            properties = json.load(f)

        # We loop through the keys and values of this dictionary using properties.items()
        for light, info in properties.items():

            # We find the light type from the info
            lightType = info.get('lightType')

            # Then for each of the light types we support, we check if they match the light type
            for lt in self.lightTypes:
                # But the light type of a Point Light is pointLight, so we convert Point Light to pointLight and then compare
                if ('%sLight' % lt.split()[0].lower()) == lightType:
                    # If we found a match, then we break out
                    break
            else:
                # For Loops also have an else statement. This only runs when the loop has not been broken out of
                # We assume if we haven't broken out of the loop, then we haven't found the light type
                # If that's the case, we just notify the user and continue on to the next light
                logger.info('Cannot find a corresponding light type for %s (%s)' % (light, lightType))
                continue

            # we can reuse variable from the loop, in this case lt was the light type.
            # We use this to create a light
            light = self.createLight(lightType=lt)

            # then we set the parameters on the light itself
            light.intensity.set(info.get('intensity'))
            light.color.set(info.get('color'))

            # Then we get the transform of the light to set its parameters
            transform = light.getTransform()
            transform.translate.set(info.get('translate'))
            transform.rotate.set(info.get('rotation'))

        # After that's done, we call the populate method to refresh our interface
        self.populate()

    def createLight(self, lightType=None, add=True):
        # This function creates lights. Duh.
        # First we get the text of the combobox if we haven;t been given a light
        if not lightType:
            lightType = self.lightTypeCB.currentText()

        # Then we look up the lightTypes dictionary to find the function to call
        func = self.lightTypes[lightType]

        # All our functions are pymel functions so they'll return a pymel object
        light = func()
        # We wil pass this to the addLight method if the method has been told to add it
        if add:
            self.addLight(light)

    def addLight(self, light):
        # This will create a LightWidget for the given light and add it to the UI
        # First we create the LightWidget
        widget = LightWidget(light)

        # Then we connect the onSolo signal from the widget to our isolate method
        widget.onSolo.connect(self.isolate)
        # Finally we add it to the scrollLayout
        self.scrollLayout.addWidget(widget)

    def isolate(self, val):
        # This function will isolate a single light
        # First we find all our children who are LightWidgets
        lightWidgets = self.findChildren(LightWidget)
        # We'll loop through the list to perform our logic
        for widget in lightWidgets:
            # Every signal lets us know who sent it that we can query with sender()
            # So for every widget we check if its the sender
            if widget != self.sender():
                # If it's not the widget, we'll disable it
                widget.disableLight(val)


def getMayaMainWindow():
    """
    Since Maya is Qt, we can parent our UIs to it.
    This means that we don't have to manage our UI and can leave it to Maya.

    Returns:
        QtWidgets.QMainWindow: The Maya MainWindow
    """
    # We use the OpenMayaUI API to get a reference to Maya's MainWindow
    win = omui.MQtUtil_mainWindow()
    # Then we can use the wrapInstance method to convert it to something python can understand
    # In this case, we're converting it to a QMainWindow
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    # Finally we return this to whoever wants it
    return ptr


def getDock(name='LightingManagerDock'):
    """
    This function creates a dock with the given name.
    It's an example of how we can mix Maya's UI elements with Qt elements
    Args:
        name: The name of the dock to create

    Returns:
        QtWidget.QWidget: The dock's widget
    """
    # First lets delete any conflicting docks
    deleteDock(name)
    # Then we create a dockControl dock using Maya's UI tools
    # This gives us back the name of the dock created
    
    # <=Maya2016: In Maya 2016 and below, we just give our Light Managers object name to the dockControl.
    # You can see this name when we do self.setObjectName in the LightManagers __init__ method
    ctrl = pm.dockControl(name, area='right', content='lightingManager', allowedArea='all', label="Lighting Manager")

    # And then we return the control name
    return ctrl


def deleteDock(name='LightingManagerDock'):
    """
    A simple function to delete the given dock
    Args:
        name: the name of the dock
    """
    # We use the dockControl to see if the dock exists
    if pm.dockControl(name, query=True, exists=True):
        # If it does we delete it
        pm.deleteUI(name)
