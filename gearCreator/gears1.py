# The 'as' keyword lets us give a nickname of our choosing to the module we import.
# The name given to an imported module is a namepsace and it helps keep our code tidy
import maya.cmds as cmds

# We create a function called createPipe
# the 'def' keyword is used to indicate we will create a function
# 'createPipe' will be the name of our function
# the function has parameters inside ( ), with one called span
def createPipe(spans=20):
    """
    Creates a polygon pipe object
    Args:
        spans (int): the number of divisions we want along the length

    Returns:
        str: the name of the transform that was created
    """
    # Above this is the docstring enclosed in """ """ that documents the function
    # This helps for people who want to use the function without needing to read the code

    # the polyPipe command will create a polygon pipe
    # the subdivisionsAxis will say how many divisions we'll have along it's length
    # It returns a list of [transform, shape]
    # Instead of getting a list and then extracting it's members, we can directly expand it to variables like here
    transform, shape = cmds.polyPipe(subdivisionsAxis=spans)

    # Finally we return the transform
    return transform

# Our makeTeeth function will take the pipe object, the number of teeth to make and the length of the teeth
def makeTeeth(pipe, teeth=10, length=0.3):
    """
    For a given pipe with a number of spans, create teeth of a given length
    Args:
        pipe (str): the name of the pipe object we'll use
        teeth (int): the number of teeth to create
        length (float): the length of the teeth

    Returns:
        str: the name of the extrude node that was created
    """
    # Since the teeth will be on every other face, we need double the spans
    spans = teeth * 2

    # We need to select all the faces that will become the teeth.
    # We use the range function to start at span times 2 because that's where the side faces start from
    # Then we continue until span times 3 because that's where it ends
    # The third optional parameter is how big the steps we will take are.
    # So we'll be taking 2 steps instead of 1. e.g. 0, 2, 4, 6, 8
    # This will return a list of numbers
    sideFaces = range(spans*2, spans*3, 2)

    # Now we need to clear the selection because we'll be adding each face to it
    cmds.select(clear=True)

    # We'll loop through all the faces in the list of sideFaces
    for face in sideFaces:
        # We'll add to the selection
        # The '%s.f[%s]' notation looks odd but it expands to something like pPipe1.f[20]
        # Which tells it to select the 20th face of the pPipe1 object
        # The %s notation means it is a placeholder for the value of the variables after the %
        cmds.select('%s.f[%s]' % (pipe, face), add=True)

    # Now we extrude the selected faces by the given length
    # This gives us back the value of the extrude node inside a list
    extrude = cmds.polyExtrudeFacet(localTranslateZ=length)

    # We just need to give back the first value of the list, so we get that and return it to whoever uses our function
    return extrude[0]


def createGear(teeth=10, length=0.3):
    """
    Creates a gear with the given number of teeth of the given length
    Args:
        teeth (int): the number of teeth to create
        length (float): the length of the gears

    Returns:
        list: [transform, extrudeNode]
    """
    # Since the teeth will be on every other face, we need double the spans
    spans = teeth * 2

    # Now we'll call our createPipe function which will give us back the pipe transform
    pipe = createPipe(spans=spans)

    # Now we'll use the makeTeeth function we created
    extrude = makeTeeth(pipe, teeth=teeth, length=length)

    # Finally we'll return the gear that was created
    return pipe, extrude


def changeLength(extrude, length=1):
    """
    For a given extrude node, change the length to the given value

    Args:
        extrude (str): the name of the extrude node
        length (float): the length to set the extrude node to
    """
    # We use the same command we used to create the extrude node, but now with the edit flag
    # When editing, we give it the extrude node we created so it knows what to edit
    # Maya commands accept shorthand arguments
    # In this case, ltz is the shorthand for localTranslateZ
    cmds.polyExtrudeFacet(extrude, edit=True, ltz=length)

    # For this function we don't return anything


def changeTeeth(gear, teeth=10, length=0.3):
    """
    Change the number of teeth on a gear with a given number of teeth and a given length for the teeth.
    This will create a new extrude node.
    Args:
        gear (str): the name of the gear that will be created
        teeth (int): the number of teeth to create
        length (float): the length of the teeth to create

    Returns:
        str: the name of the new extrude node
    """
    # We'll list the connections of the gear's inMesh. This gives us back a list
    inputs = cmds.listConnections(gear+'.inMesh')

    # We'll make a temporary variable called extrude
    extrude = None
    # We loop through the input nodes
    for node in inputs:
        # We check if its an extrude node
        if cmds.objectType(node) == 'polyExtrudeFace':
            # If it is, we store it in the extrude variable we created
            extrude = node
            # We now break out of this loop, which means that we'll stop the loop completely
            break

    # Now that we have the extrude node we need to find the polyPipe construction node to change it
    polyPipe = getConstructor(extrude)

    # Once we find that , we no longer need this extrude node so lets get rid of it
    cmds.delete(extrude)

    # Now we edit the polyPipe by giving it to the polyPipe command with the edit parameter
    # We'll use the shorthand for subdivisionsaxis which is sa
    cmds.polyPipe(polyPipe, edit=True, sa=teeth*2)

    # Finally we use the makeTeeth function again to create the teeth again with the new faces
    extrude = makeTeeth(gear, teeth=teeth, length=length)

    # Finally we return the name of the new extrude node
    return extrude


def getConstructor(extrude):
    """
    Finds the polyPipe creation node from a given extrude node
    Args:
        extrude (str): The name of the extrude node
    Returns:
        str: the name of the polyPipe construction node
    """
    # We will list the connections coming into the extrude node's inputPolymesh
    # This will return a list of things that are connected
    inputs = cmds.listConnections('%s.inputPolymesh' % extrude)

    # Now loop through the nodes that are connected to try and find it
    for node in inputs:
        # We'll check if the node is a polyPipe node
        if cmds.objectType(node) == 'polyPipe':
            # If it is, we'll return it. This will exit the function immediately and send back the name of the node
            return node