"""
In this code sample we learn about defining functions.
We'll restructure the code from the first renamer example into a function we can call
"""

from maya import cmds

# We define a dictionary here using the {} notation
# Dictionaries are an association of a key and a value.
# In a real dictionary you'd have the word (key) and the definition (value)
# In this case you have the key as the objectType and the value as a suffix.
# For the camera we will set None as we want to use it to indicate Camera's should have no suffix
SUFFIXES = {
    "mesh": "geo",
    "joint": "jnt",
    "camera": None,
}

# And if something doesn't have an appropriate suffix, lets default to group.
DEFAULT = "grp"

# Here we create our first function.
# The word 'def' is used to define (def-ine) a function
# Following the def, is the name of the function
# In the parenthesis () we provide an argument, and give it an optional default value
# This means that when someone uses our function they can provide some input, but the default value means they don't have to.
#
# Following the function is some text in triple quotes. This is called a docstring.
# Docstrings are documentation on how to use the function and are a good practice to write so that people
#       can understand how to use your function without reading the code
def rename(selection=False):
    """
    Renames objects by adding suffixes based on the object type
    Args:
        selection (bool): Whether we should use the selection or not. Defaults to False

    Raises:
        RuntimeError: If nothing is selected

    Returns:
        list: A list of all the objects renamed
    """

    # Our function has an input called selection.
    # This is used to let it know if we should use the selection or not

    # The ls function also takes an input called selection, and we can just pass that through
    objects = cmds.ls(selection=selection, dag=True)

    # Now if we are trying to use the selection and nothing is selected, lets give an error
    if selection and not objects:
        # We raise an exception, just like you would raise a complaint against someone
        # We give a RuntimeError because the error is to do with how we run this
        # And we give a message with some details
        # This will end our function and display a detailed error message (traceback) to our users
        raise RuntimeError("You don't have anything selected")

    # Now we need to sort our items from longest to shortest again so that we don't rename parents before children
    objects.sort(key=len, reverse=True)

    # Now we loop through all the objects we have
    for obj in objects:

        # We get the shortname again by splitting at the last |
        shortName = obj.split('|')[-1]

        # Now we see if there are children and if there are we get their type.
        # This is in case we receive a transform and not its shape
        children = cmds.listRelatives(obj, children=True) or []
        if len(children) == 1:
            child = children[0]
            objType = cmds.objectType(child)
        else:
            objType = cmds.objectType(obj)

        # Now we look at the dictionary and ask to get the value associated with the key
        # In this case, if objType is mesh, we will get geo
        # If the dictionary doesn't hold the item, it will return the default value instead that we ask it for
        suffix = SUFFIXES.get(objType, DEFAULT)

        # If we can't get a suffix, we will continue
        # Continue means that we will continue on to the next item and skip the logic for this one
        if not suffix:
            continue

        # To prevent adding the suffix twice, we'll check if it already has the suffix and skip it if it does
        if shortName.endswith('_'+suffix):
            continue

        # Now we'll make the new name using string formatting
        # Instead of using the + symbol, we can use the %s symbol to insert strings
        newName = '%s_%s' % (shortName, suffix)
        cmds.rename(shortName, newName)

        # Now we find where in the list of objects our current object is
        index = objects.index(obj)

        # Then we replace it in the list with the name of the new object
        objects[index] = obj.replace(shortName, newName)

    # Finally we return the list back to the user of our function
    # Returning is how a function can let things outside it know what the result of it is
    return objects