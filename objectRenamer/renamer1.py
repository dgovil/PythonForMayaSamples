"""
This is a utility to add suffixes to objects based on the object type.
This helps keep our scene tidy and organized.
"""

# First we import the commands library from Maya so we can issue commands to Maya
from maya import cmds

# First we want to check if we have something selected
# We will ask maya to list (ls) everything that is selected (selection=True)
# We should also get the full path to the object instead of just the name of the object
selection = cmds.ls(selection=True, long=True)

# This will give us back a list of the paths of all the objects we have selected
print selection

# Now we need to check if we might not have something selected
# We will check the length of the selection list to see if it is 0 (empty) in which case we will just list everything

# This is an If statement, where we are saying: "If it is true that the length is zero, then do the part after that"
# Unlike other programming languages, python uses indentation to show when something is inside a block of code
# For example, the indented line after the if statement is inside the if statement
if len(selection) == 0:
    # This is inside the if statement
    selection = cmds.ls(long=True, dag=True)
# This is outside it.

# We can run into an issue where we'll rename a parent before a child, causing the path to the child to change.
# To work around that we'll sort the list by length

# So this can be a little confusing
# Just like Maya has attributes on objects with the period, so does python.
# The list object has a sort method on it, that will sort itself.
# Usually this will sort it alphabetically, but we want to sort by length and to reverse it to put the longest first
selection.sort(key=len, reverse=True)


# Now we need to loop through the objects and rename them
# We'll use a for loop for this
# We step through all the items one by one in the selection object, assign it to a variable (obj) and run the logic below it
for obj in selection:
    # For each object in the selection list, run the following logic

    # The name will be something like grandparent|parent|child
    # We just want the child part of the name, so we split using the | character which gives us a list of ['grandparent', 'parent', 'child']
    # We need to get the last item in the list, so we use [-1]. This means we backwards through the list and pick the next item, which would therefore be the last item
    shortName = obj.split('|')[-1]

    print "Before rename: ", shortName

    # If the object is a transform, then we should check if it has a shape below it
    children = cmds.listRelatives(obj, children=True) or []

    # We will only do this if there is one child
    if len(children) == 1:
        # We will take the first child
        child = children[0]
        objType = cmds.objectType(child)
    else:
        # Now we get the object type of the current object
        objType = cmds.objectType(obj)

    # We use a bunch of if statements to find the suffix we want to add
    # An if statement can have three parts. the if, elif and else
    if objType == "mesh":
        suffix = 'geo'
    elif objType == "joint":
        suffix = 'jnt'
    elif objType == 'camera':
        print "Skipping camera"
        continue
    else:
        suffix = 'grp'

    # Now we need to construct the new name
    newName = shortName+"_"+suffix

    # Now tell it to rename the obj to the new name with the suffix
    cmds.rename(obj, newName)

    print "After rename: ", newName