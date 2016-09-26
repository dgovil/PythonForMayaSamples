"""
In this code sample we learn about defining functions.
We'll restructure the code from the first renamer example into a function we can call
"""

from maya import cmds

SUFFIXES = {
    "mesh": "geo",
    "joint": "jnt",
    "camera": None,
}

DEFAULT = "grp"

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

    objects = cmds.ls(selection=selection, dag=True)
    if selection and not objects:
        raise RuntimeError("You don't have anything selected")

    objects.sort(key=len, reverse=True)
    for obj in objects:
        shortName = obj.split('|')[-1]

        children = cmds.listRelatives(obj, children=True) or []
        if len(children) == 1:
            child = children[0]
            objType = cmds.objectType(child)
        else:
            objType = cmds.objectType(obj)

        suffix = SUFFIXES.get(objType, DEFAULT)

        if not suffix:
            continue

        if shortName.endswith('_'+suffix):
            continue

        newName = '%s_%s' % (shortName, suffix)
        cmds.rename(shortName, newName)

        index = objects.index(obj)
        objects[index] = obj.replace(shortName, newName)

    return objects