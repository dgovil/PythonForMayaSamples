from maya import cmds
import tweener
from gearCreator import gears2 as gear


# We put a lot of work into making our window for the tweener.
# But what if we want to make another window? Do we have to write everything again?

# Fortunately Python classes support inheritance
# Just like your inherit your good looks from your parents, Python classes can inherit methods and attributes from their parents

# So we first make a Base Window that we can reuse.
# This will have just the bare functionality to make a window
class BaseWindow(object):
    windowName = "BaseWindow"

    def show(self):
        if cmds.window(self.windowName, query=True, exists=True):
            self.close()

        cmds.window(self.windowName)
        self.buildUI()
        cmds.showWindow()

    def buildUI(self):
        # This is a placeholder method
        pass

    # Again, the *args variable means that we don't know how many arguments we will receive so lets put them all inside this argument called args
    def reset(self, *args):
        # This is a placeholder method
        pass

    def close(self, *args):
        cmds.deleteUI(self.windowName)


# For our tweener UI, we inherit from our BaseWindow
# Just like our BaseWindow inherits from the Python object, our TweenerWindow inherits from BaseWindow
# This means that it will get all the attributes and methods that the Base Window has
class TweenerWindow(BaseWindow):
    # The Base Window has a windowName attribute
    # By defining it here, we are overriding it.
    # Just like you may have different taste in music than your parents golden oldies, a child class can have
    #       different attributes than its parent
    windowName = "TweenerWindow"

    # Similarly we redefine the buildUI method.
    # When buildUI is called in any methods from BaseWindow, it will know to refer to our overriden variable here
    def buildUI(self):
        column = cmds.columnLayout()
        cmds.text(label="Use this slider to set the tween amount")

        cmds.rowLayout(numberOfColumns=2)
        self.slider = cmds.floatSlider(min=0, max=100, value=50, step=1, changeCommand=tweener.tween)
        cmds.button(label="Reset", command=self.reset)

        cmds.setParent(column)
        cmds.button(label="Close", command=self.close)

    # And again, we just need to override the reset method
    # We don't need to define the close, or show methods because it gets those from BaseWindow
    def reset(self, *arg):
        cmds.floatSlider(self.slider, edit=True, value=50)


# Now that we have our tweener working, we can work on our Gear Creator Window
# Just like the Tweener we inherit from BaseWindow which gives us all its attributes and methods
class GearWindow(BaseWindow):
    # We redefine the window name
    windowName = "GearWindow"

    # Our old friend init, which is called whenever we create a new window
    def __init__(self):
        # we just need to store our current gear inside a variable
        self.gear = None

    # Just like the Tweener, we just redefine the buildUI to customize our UI
    # It gets called from the show method that we inherited
    def buildUI(self):
        column = cmds.columnLayout()
        cmds.text(label="Use the slider to modify the number of teeth the gear will have")

        cmds.rowLayout(numberOfColumns=4)

        # This label will show the number of teeth we've set
        self.label = cmds.text(label="10")
        # Unlike the tweener, we use an integer slider and we set it to run the modifyGear method as it is dragged
        self.slider = cmds.intSlider(min=5, max=30, value=10, step=1, dragCommand=self.modifyGear)
        cmds.button(label="Make Gear", command=self.makeGear)
        cmds.button(label="Reset", command=self.reset)

        cmds.setParent(column)
        cmds.button(label="Close", command=self.close)

    def makeGear(self, *args):
        # We first need to see what the slider is set to, to find how many teeth we need to make
        teeth = cmds.intSlider(self.slider, query=True, value=True)

        # We make a near gear class instance
        self.gear = gear.Gear()

        # Now we create the gear with the given number of teeth
        self.gear.create(teeth=teeth)

    def modifyGear(self, teeth):
        # When the slider is changes, this method will be called.
        # First we will update the label that displays the number of teeth
        # the str() function converts the number into a string
        cmds.text(self.label, edit=True, label=str(teeth))

        # If there is a gear already made, then we will set the slider to edit it
        if self.gear:
            self.gear.changeTeeth(teeth=teeth)

    def reset(self, *args):
        # When we reset, we will intentionally say we're done with this gear, move on to the next one
        # So moving the slider now will not adjust an existing gear
        self.gear = None

        # We will reset the slider value
        cmds.intSlider(self.slider, edit=True, value=10)

        # And finally reset the label value
        # the str() function converts the number into a string
        cmds.text(self.label, edit=True, label=str(10))
