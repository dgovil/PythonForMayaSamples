# In this excercise we will create a simple cube!
# Just a reminder that anything after a # is just a comment and will not be run

# We need to import the commands (cmds for short) library from maya to be able to give Maya commands to run
# The import statement lets us bring in other python libraries, called modules from python packages.
# In this case we are bringing in the cmds module from the maya package
from maya import cmds

# We create a cube by giving maya the polyCube command
# Maya will then give us back the cube's transform and its' shape.
# We will store both in a variable called cube.
# Variables are like nicknames we can give to objects in python, so that we don't need to know how to actually call it.
# Sort of like that guy at work who always forgets my name and calls me Dave.
cube = cmds.polyCube()

# OKAY I LIED!
# We've created the cube, but that's not exciting is it? Let's go further and make it ready to animate with a control.

# If we print out the contents of the cube variable we see that it will contain a transform and a shape
# You should see something like [u'pCube1', u'polyCube1']
print cube

# This is called a list, so we can say the type of cube is a list.
# If you don't believe me, you can run this and it will say: <type 'list'>
print type(cube)

# Lists are , well, a list of objects. They can contain anything, even other lists.
# In this case, the list contains the names of the transform and the shape of the cube.
# We need to get just the transform, which is the first member of the list
transform = cube[0]

# While humans count lists from 1, computers count lists from 0.
# It takes a while to get used to it, but you'll learn it quickly enough
# So we've taken the first object in the list, with index of 0.
# If you want the shape instead, you can get the second item in the list, at index 1
# As you can see the [] notation is used to get the item at that index
shape = cube[1]

# Now lets create a nurbs circle controller to parent the cube under
# But I don't remember the command to create a circle!
# If you create a nurbs circle manually, it will show you the circle command in the script editor
# So we can deduce it will be the following
circle = cmds.circle()

# Similar to the cube, we've created a circle and got back a list of the circle transform and its' shape
# We can see this by printing out the contents of circle
print circle

# We only need the transform so lets take just the transform like we did above
# As you can see here, you can always repurpose a variable and it will now refer to the new thing we point it to.
# Just like my coworker calls a few different people Dave, I can call a few different things circle
circle = circle[0]

# Okay so we have the circle transform (circle) and the cube's transform (transform)
# Let's parent the cube under the circle
# What you see here is that we can give commands more details on how to run.
# In this case, we're telling the parent command to take the transform we found earlier from the cube
#       and then put it under the circle transform we found aboove
# These are called positional arguments as their order is important
cmds.parent(transform, circle)

# Now that we can controle the cube with the circle, lets lock the cube's controls
# We're going to set the attributes of the cube to locked
# Maya uses the period symbol to show that attributes belong to an object. e.g. pCube1.transform
# transform is a string and we can use the plus symbol to add another string to it
# As you can see, strings can use either single or double quotes as long as you end them with the same
# lock is an example of a keyword argument. Its' order is not important as you refer to the argument name directly.
cmds.setAttr(transform+'.translate', lock=True)
cmds.setAttr(transform+".rotate", lock=True)
cmds.setAttr(transform+'.scale', lock=True)

# Finally lets select the circle
cmds.select(circle)

# And there you have it, you've quickly learned how to prop things!