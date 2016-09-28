"""
In this code sample, we'll convert the functions we created earlier to make a gear, into a class.
A class is a python object that lets you contain functions that relate to a specific object easily
"""
import maya.cmds as cmds

# The class keyword creates a class, ours will be called Gear
# We will base our class on the python 'object'
# Object is the base for everything in python, and by basing off of the python 'object' we get all of its
#       attributes for free
class Gear(object):
    """
    Classes can have docstrings too that will describe how to use it

    In this case you would use it like this

    # This creates an instance of the class.
    # Classes descrive an object, instances are the objects that they describe
    # For example an Animal class describes an animal, but a dog on the street would be an instance of an Animal
    gearA = Gear()

    gearA.create(teeth=20, length=0.2)
    gearA.changeTeeth(teeth=10, length=0.5)
    """
    # The __init__ function is something that classes use a lot
    # They get run whenever you initialize a new instance of a class
    # For example when you do this gearA = Gear() it will run the __init__
    # You can think of them as the entryway to a class that tells it how to set up
    #
    # Most functions inside a class will take a first parameter called self that tells it to refer to itself.
    # Kind of like how you need to know you are yourself, the self parameter tells an instance it is itself
    def __init__(self):
        # We will just use this __init__ to create placeholder variables on the class
        # Variables that start with self are set on the instance and can be accessed outside this function
        self.shape = None
        self.transform = None
        self.constructor = None
        self.extrude = None

    # Another thing, functions inside a class are called methods
    def create(self, teeth=10, length=0.3):
        # The logic here is the same as in the functional version of this
        spans = teeth * 2

        # We refer to the createPipe method with self because we want to know to call the method that is inside this class
        # Notice we aren't getting a variable back from this method
        # Because we will store the variables on the class, we don't have to pass around them from a return (though we can if we choose to)
        self.createPipe(spans)

        # Similarly we call self.makeTeeth which is a method inside this class
        self.makeTeeth(teeth=teeth, length=length)

    def createPipe(self, spans):
        # We set the transform and shape to the class variables
        self.transform, self.shape = cmds.polyPipe(subdivisionsAxis=spans)

        # I didn't like having to find the constructor from the extrude node
        # Lets just find it now and save it to the class because it won't change
        for node in cmds.listConnections('%s.inMesh' % self.transform):
            if cmds.objectType(node) == 'polyPipe':
                self.constructor = node
                break

    def makeTeeth(self, teeth=10, length=0.3):
        # The logic here is exactly the same as in the makeTeeth function we created
        spans = teeth * 2
        sideFaces = range(spans * 2, spans * 3, 2)

        cmds.select(clear=True)
        for face in sideFaces:
            cmds.select('%s.f[%s]' % (self.transform, face), add=True)

        # Instead of returning a value, lets just store the extrude node onto the class as a class variable
        self.extrude = cmds.polyExtrudeFacet(localTranslateZ=length)
        cmds.select(clear=True)

    def changeLength(self, length=0.3):
        # Because we stored the extrude node on the class, we can just get it directly
        # This way we don't need to be told what extrude node to change
        cmds.polyExtrudeFacet(self.extrude, edit=True, ltz=length)

    def changeTeeth(self, teeth=10, length=0.3):
        # Since we know what the extrude node is, we'll just refer to it directly
        cmds.delete(self.extrude)
        # Similarly we know what node the constructor is, so we can refer to it directly
        cmds.polyPipe(self.constructor, edit=True, sa=teeth * 2)
        # Then we can just call the makeTeeth directly
        self.makeTeeth(teeth=teeth, length=length)
