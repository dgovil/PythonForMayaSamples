# The 'as' keyword lets us give a nickname of our choosing to the module we import.
# The name given to an imported module is a namepsace and it helps keep our code tidy
import maya.cmds as cmds


# We create a function called createGear
# the 'def' keyword is used to indicate we will create a function
# 'createGear' will be the name of our function
# the function has parameters inside ( ), with two: one for teeth and one for length. Each has a default value
def createGear(teeth=10, length=0.3):
    """
    This function will create a gear with the given parameters
    Args:
        teeth: The number of teeth to create
        length: The length of the teeth

    Returns:
        A tuple of the transform, constructor and extrude node
    """
    # Above this is the docstring enclosed in """ """ that documents the function
    # This helps for people who want to use the function without needing to read the code

    # Teeth are every alternate face, so we double the number of teeth to get the number of spans required
    spans = teeth * 2

    # the polyPipe command will create a polygon pipe
    # the subdivisionsAxis will say how many divisions we'll have along it's length
    # It returns a list of [transform, constructor]
    # Instead of getting a list and then extracting it's members, we can directly expand it to variables like here
    # The transform is the name of the node created and the constructor is the node that creates the pipe and controls its parameters
    transform, constructor = cmds.polyPipe(subdivisionsAxis=spans)

    # We need to select all the faces that will become the teeth.
    # We use the range function to start at span times 2 because that's where the side faces start from
    # Then we continue until span times 3 because that's where it ends
    # The third optional parameter is how big the steps we will take are.
    # So we'll be taking 2 steps instead of 1. e.g. 0, 2, 4, 6, 8
    # This will return a list of numbers
    sideFaces = range(spans * 2, spans * 3, 2)

    # Now we need to clear the selection because we'll be adding each face to it
    cmds.select(clear=True)

    # We'll loop through all the faces in the list of sideFaces
    for face in sideFaces:
        # We'll add to the selection
        # The '%s.f[%s]' notation looks odd but it expands to something like pPipe1.f[20]
        # Which tells it to select the 20th face of the pPipe1 object
        # The %s notation means it is a placeholder for the value of the variables after the %
        cmds.select('%s.f[%s]' % (transform, face), add=True)

    # Now we extrude the selected faces by the given length
    # This gives us back the value of the extrude node inside a list
    extrude = cmds.polyExtrudeFacet(localTranslateZ=length)[0]

    # Finally we return a tuple of (transform, constructor, extrude)
    # A tuple is similar to a list but cannot be modified.
    # Notice that we don't need to provide the parenthesis that define a tuple, just adding  the comma here will do it for us

    # Here the transform is our gear node, the constructor is the node that creates the original pipe and the extrude is the node that extrudes the faces
    return transform, constructor, extrude


# We now create the changeTeeth function that will modify our constructor and extrude node to change the teeth we get
def changeTeeth(constructor, extrude, teeth=10, length=0.3):
    """
    Change the number of teeth on a gear with a given number of teeth and a given length for the teeth.
    This will create a new extrude node.
    Args:
        constructor (str): the constructor node
        extrude (str): the extrude node
        teeth (int): the number of teeth to create
        length (float): the length of the teeth to create
    """
    # Just like before we calculate the number of spans required by duplicating the number of teeth.
    spans = teeth * 2

    # We then use the same polyPipe command we used to create the pipe to modify it, this time providing the edit=True parameter
    # This edit parameter tells it we want to modify its attributes instead of creating a new one
    cmds.polyPipe(constructor, edit=True,
                  subdivisionsAxis=spans)

    # As we did when creating it we need to get a list of faces to extrude as teeth
    sideFaces = range(spans * 2, spans * 3, 2)
    faceNames = []

    # We need to get a list in the following format
    # [u'f[40]', u'f[42]', u'f[44]', u'f[46]', u'f[48]', u'f[50]', u'f[52]', u'f[54]', u'f[56]', u'f[58]']

    # So we'll loop through all the sidefaces
    for face in sideFaces:
        # And we'll use the string substitution to create the names
        # In this case, %s will be replaced by 'face' which is the number of our face
        faceName = 'f[%s]' % (face)

        # We'll add this to our list of faceNames
        faceNames.append(faceName)

    # Then we must modify the extrude's parameter for which components it affects.
    # This takes a few different arguments

    # The extrude node has an attribute called inputComponents
    # To change it we can use a simple setAttr call instead of recreating the extrude which can be expensive
    # The arguments to changing a list of components is slightly different than a simple setAttr
    # it is:
    #   cmds.setAttr('extrudeNode.inputComponents', numberOfItems, item1, item2, item3, type='componentList')
    cmds.setAttr('%s.inputComponents' % (extrude),
                 len(faceNames),
                 *faceNames,
                 type="componentList")

    # The *faces will be new to you.
    # It basically means to expand a list in place for arguments
    # so if the list has ['f[1]', 'f[2]'] etc, it will be expanded in the arguments to be like this
    # cmds.setAttr('extrudeNode.inputComponents', 2, 'f[1]', 'f[2]', type='componentList'

    cmds.polyExtrudeFacet(extrude, edit=True, ltz=length)
