# We are using the Qt library that Marcus made here so that we don't have to worry about Qt4 and Qt5
# If you don't want to use his library you can change it to one of the following
# In Maya 2017 or above we use Qt5 so we can just replace the library name
#     from PySide2 import QtWidgets, QtCore, QtGui
# In Maya 2016 and below, you'd have to replace both the library name and QtWidgets is called QtGui
#     from PySide import QtGui, QtCore
# But why have that hassle when you can just use this library that means your code will work anywhere?
from Qt import QtWidgets, QtCore, QtGui

# This is a more complex tool so we'll be importing quite a few more libraries this time
# This is the json library which we'll be using to write out data
import json

# This is the OS library that lets us deal with our operating system.
# Specifically we will use it to find our files
import os

# The pprint module is short for pretty print
# It is used to format dictionaries in a nice way
import pprint

# Finally this is our old faithful maya library
from maya import cmds


# We want to create a default directory that we can refer to later
# We use os.path.join because it uses the correct path separator for our operating system
# the userAppDir variable will give us the location where our maya documents are stored by default.
# We'll set out library inside a folder inside this folder
DIRECTORY = os.path.join( cmds.internalVar(userAppDir=True), 'controllerLibrary')


# We start by creating our code so that it can work without the UI
# Dictionaries are a good way to store data
# We aren't adding much, so it's easiest to just inherit from a dictionary.
# This lets our library act like its a dictionary while giving us our custom features
class ControllerLibrary(dict):

    # First of all we need a function to create a directory
    # We allow the code to set another directory, but we set a default value of our current directory
    def createDir(self, directory=DIRECTORY):
        # We check if our directory doesn't exist
        if not os.path.exists(directory):
            # If it doesn't exist, we make the directory
            os.mkdir(directory)

    # First lets standardize how we will save our files
    # the **info argument will be new to you
    # similar to how we used *args in the previous example to capture all arguments
    # ** is used to capture all keyword arguments into the variable called info
    # Info will be a dictionary
    def save(self, name, screenshot=True, directory=DIRECTORY, **info):
        """
        The save function will save the current scene as a controller
        Args:
            name: the name to save the controller as
            screenshot: Whether or not to save a screenshot
            directory: the directory to save to
            **info: any extra info we might want to store
        """
        # We will start by creating the directory just to make sure it exists
        self.createDir(directory)

        # We use the same os.path.join to construct the name of our output maya file
        path = os.path.join(directory, '%s.ma' % name)

        # Similarly we construct the name of our json file that will store any info
        infoFile = os.path.join(directory, '%s.json' % name)

        # If we've been told to save the screenshot, lets run a little more code
        if screenshot:
            # We call to anotehr method to create the screenshot
            # Then we use the return value of that to store in the info dictionary
            info['screenshot'] = self.saveScreenshot(name, directory=directory)

        # We store some more information in the info dictionary
        info['name'] = name
        info['path'] = path

        # Now we rename the file to what we want it to be saved as
        cmds.file(rename=path)

        # If something is selected, we only export the selection, otherwise we save the wholefile
        if cmds.ls(selection=True):
            cmds.file(force=True, exportSelected=True)
        else:
            cmds.file(save=True, force=True)

        # Since we are a dictionary, we can save data to ourself
        self[name] = info

        # Finally we open a file to write to on disk
        # The with keyword is used to denote a context wheree the file is called f
        # This will open a file for us, run all the logic we give it, then close the file out
        with open(infoFile, 'w') as f:
            # We use the json library to convert our dictionary to a common data format
            # We write it to f
            # and we give each line an indentation of 4 spaces to be easy to read
            json.dump(info, f, indent=4)

    # Now we have a find function that will be used to find all the controllers in the given directory
    def find(self, directory=DIRECTORY):
        # First we check if the directory even exists, because why waste our time otherwise?
        if not os.path.exists(directory):
            return

        # Now we list all the files in that directory
        files = os.listdir(directory)

        # We are only interested in finding all the maya ascii files
        # We use list comprehension to reduce the files we're looking at
        mayaFiles = [f for f in files if f.endswith('.ma')]

        # Now we loop through the maya files we found
        for ma in mayaFiles:
            # We grab the name and the file extension of the file
            name, ext = os.path.splitext(ma)

            # We'll have to construct the name of the screenshot and the json file so that we can find them
            infoFile = '%s.json' % name
            screenshot = '%s.jpg' % name

            # If the infoFile exists, we'll construct its full path and try to read it in
            if infoFile in files:
                infoFile = os.path.join(directory, infoFile)

                # Similar to the way we wrote out the file, we'll read it in
                with open(infoFile, 'r') as f:
                    # The JSON module will read our file, and convert it to a python dictionary
                    data = json.load(f)
            else:
                # But if the file doesn't exist, we'll just make an empty dictionary
                data = {}

            # If we have a screenshot, lets store the info in the dictionary so we know where to find it later
            if screenshot in files:
                data['screnshot'] = os.path.join(directory, screenshot)

            # Then lets store some basic information
            data['name'] = name
            data['path'] = os.path.join(directory, ma)

            # Finally since we're a dictionary, we can save data to ourselves like we would to a dictionary
            self[name] = data

    # This function will be used to load the controller with the given name
    def load(self, name):
        path = self[name]['path']
        # We tell the file command to import, and tell it to not use any nameSpaces
        cmds.file(path, i=True, usingNamespaces=False)

    # This function will save a screenshot to the given directory with the given name
    def saveScreenshot(self, name, directory=DIRECTORY):
        path = os.path.join(directory, '%s.jpg' % name)

        # We'll fit the view to the objects in our scene or our selection
        cmds.viewFit()

        # We'll change our render format to jpg
        cmds.setAttr("defaultRenderGlobals.imageFormat", 8) # This is the value for jpeg

        # Finally we'll save out our image using the playblast module
        # There are a lot of arguments here so it's good to use the documentation to know what's going on
        cmds.playblast(completeFilename=path, forceOverwrite=True, format='image', width=200, height=200,
                       showOrnaments=False, startTime=1, endTime=1, viewer=False)

        # Return the path of the file we saved
        return path


# This will be our first Qt UI!
# We'll be creating a dialog, so lets start by inheriting from Qt's QDialog
class ControllerLibraryUI(QtWidgets.QDialog):

    def __init__(self):
        # super is an interesting function
        # It gets the class that our class is inheriting from
        # This is called the superclass
        # The reason is that because we redefined __init__ in our class, we no longer call the code in the super's init
        # So we need to call our super's init to make sure we are initialized like it wants us to be
        super(ControllerLibraryUI, self).__init__()

        # We set our window title
        self.setWindowTitle('Controller Library UI')

        # We store our library as a variable that we can access from inside us
        self.library = ControllerLibrary()

        # Finally we build our UI
        self.buildUI()

    def buildUI(self):
        # Just like we made a column layout in the last UI, in Qt we have a vertical box layout
        # We tell it that we want to apply the layout to this class (self)
        layout = QtWidgets.QVBoxLayout(self)

        # We want to make another widget to store our controls to save the controller
        # A widget is what we call a UI element
        saveWidget = QtWidgets.QWidget()
        # Every widget needs a layout. We want a Horizontal Box Layout for this one, and tell it to apply to our widget
        saveLayout = QtWidgets.QHBoxLayout(saveWidget)
        # Finally we add this widget to our main widget
        layout.addWidget(saveWidget)

        # Our first order of business is to have a text box that we can enter a name
        # In Qt this is called a LineEdit
        self.saveNameField = QtWidgets.QLineEdit()
        # We will then add this to our layout for our save controls
        saveLayout.addWidget(self.saveNameField)

        # We add a button to call the save command
        saveBtn = QtWidgets.QPushButton('Save')
        # When the button is clicked it fires a signal
        # A signal can be connected to a function
        # So when the button is called, it will call the function that is given.
        # In this case, we tell it to call the save method
        saveBtn.clicked.connect(self.save)
        # and then we add it to our save layout
        saveLayout.addWidget(saveBtn)

        # Now we'll set up the list of all our items
        # The size is for the size of the icons we will display
        size = 64
        # First we create a list widget, this will list all the items we give it
        self.listWidget = QtWidgets.QListWidget()
        # We want the list widget to be in IconMode like a gallery so we set it to a mode
        self.listWidget.setViewMode(QtWidgets.QListWidget.IconMode)
        # We set the icon size of this list
        self.listWidget.setIconSize(QtCore.QSize(size, size))
        # then we set it to adjust its position when we resize the window
        self.listWidget.setResizeMode(QtWidgets.QListWidget.Adjust)
        # Finally we set the grid size to be just a little larger than our icons to store our text label too
        self.listWidget.setGridSize(QtCore.QSize(size+12, size+12))
        # And finally, finally, we add it to our main layout
        layout.addWidget(self.listWidget)

        # Now we need a layout to store our buttons
        # So first we create a widget to store this layout
        btnWidget = QtWidgets.QWidget()
        # We create another horizontal layout and tell it to apply to our btn widdget
        btnLayout = QtWidgets.QHBoxLayout(btnWidget)
        # And we add this widget to our main UI
        layout.addWidget(btnWidget)

        # Similar to above we create three buttons
        importBtn = QtWidgets.QPushButton('Import!')
        # And we connect it to the relevant functions
        importBtn.clicked.connect(self.load)
        # And finally we add them to the button layout
        btnLayout.addWidget(importBtn)

        refreshBtn = QtWidgets.QPushButton('Refresh')
        refreshBtn.clicked.connect(self.populate)
        btnLayout.addWidget(refreshBtn)

        closeBtn = QtWidgets.QPushButton('Close')
        closeBtn.clicked.connect(self.close)
        btnLayout.addWidget(closeBtn)

        # After all that, we'll populate our UI
        self.populate()

    def load(self):
        # We will ask the listWidget what our currentItem is
        currentItem = self.listWidget.currentItem()

        # If we don't have anything selected, it will tell us None is selected, so we can skip this method
        if not currentItem:
            return

        # We then get the text label of the current item. This will be the name of our control
        name = currentItem.text()
        # Then we tell our library to load it
        self.library.load(name)

    def save(self):
        # We start off by getting the name in the text field
        name = self.saveNameField.text()

        # If the name is not given, then we will not continue and we'll warn the user
        # The strip method will remove empty characters from the string, so that if the user entered spaces, it won't be valid
        if not name.strip():
            cmds.warning("You must give a name!")
            return

        # We use our library to save with the given name
        self.library.save(name)
        # Then we repopulate our UI with the new data
        self.populate()
        # And finally, lets remove the text in the name field so that they don't accidentally overwrite the file
        self.saveNameField.setText('')

    def populate(self):
        # This function will be used to populate the UI. Shocking. I know.

        # First lets clear all the items that are in the list to start fresh
        self.listWidget.clear()

        # Then we ask our library to find everything again in case things changed
        self.library.find()

        # Now we iterate through the dictionary
        # This is why I based our library on a dictionary, because it gives us all the nice tricks a dictionary has
        for name, info in self.library.items():
            # We create an item for the list widget and tell it to have our controller name as a label
            item = QtWidgets.QListWidgetItem(name)

            # We set its tooltip to be the info from the json
            # The pprint.pformat will format our dictionary nicely
            item.setToolTip(pprint.pformat(info))

            # Finally we check if there's a screenshot available
            screenshot = info.get('screenshot')
            # If there is, then we will load it
            if screenshot:
                # So first we make an icon with the path to our screenshot
                icon = QtGui.QIcon(screenshot)
                # then we set the icon onto our item
                item.setIcon(icon)

            # Finally we add our item to the list
            self.listWidget.addItem(item)

# This is a convenience function to display our UI
def showUI():
    # Create an instance of our UI
    ui = ControllerLibraryUI()
    # Show the UI
    ui.show()
    # Return the ui instance so people using this function can hold on to it
    return ui
