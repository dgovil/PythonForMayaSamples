"""
This is our final project and is an example of how to use python outside Maya to create command line tools

We'll make a script that can be both reused by other python libraries and from the command line.
It will support standard commandline flags to control its options
"""

# The argparse module is a standard module for creating command line tools
import argparse

# The re module gives us the power of regular expressions, which is an advanced pattern matching library
import re

# And of course we need the os module to interact with the operating system
import os

# Shutil is another utility that we may need to copy a file
import shutil


def main():
    """
    This is the function that gets run by default when this module is executed.
    It is common convention to call this first function 'main' but it can be called anything you like
    """
    # First lets create a new parser to parse the command line arguments
    # The arguments we're giving it are ones that will be displayed when a user incorrectly uses your tool or if they ask for help
    parser = argparse.ArgumentParser(description="This is a simple batch renaming tool to rename sequences of files",
                                     usage="To replace all files with hello wtih goodbye: python renamer.py hello goodbye")
    # We'll add two positional arguments. These must be given
    parser.add_argument('inString', help="The word or regex pattern to replace")
    parser.add_argument('outString',help="The word or regex pattern to replace it with")
    # Then we'll add some keyword arguments. Like in python functions, they default to a value so are optional
    # The first one is set to store_true, which means it is False by default but if provided will be set to True
    # Therefore you don't provide a value to it
    #
    # The first argument is the short flag name
    # The second is the long version of the same flag
    parser.add_argument('-d', '--duplicate', help="Should we duplicate or write over the original files", action='store_true')
    parser.add_argument('-r', '--regex', help="Whether the inputs will be using regex or not", action='store_true')

    # This last argument doesn't say store true, which means a value must be given for it, or it will default to None
    parser.add_argument('-o', '--out', help="The location to deposit these files. Defaults to this directory")

    # Finally we tell the parser to parse the arguments from the command line
    args = parser.parse_args()

    # We use these arguments to provide input to our rename function
    rename(args.inString, args.outString, duplicate=args.duplicate,
           outDir=args.out, regex=args.regex)

def rename(inString, outString, duplicate=True, inDir=None, outDir=None, regex=False):
    """
    A simple function to rename all the given files in a given directory
    Args:
        inString:  the input string to find and replace
        outString: the output string to replace it with
        duplicate: Whether we should duplicate the renamed files to prevent writing over the originals
        inDir: what the directory we should operate in
        outDir: the directory we should write to.
        regex: Whether we should use regex instead of simple string replace
    """
    # If no input directory is provided, we'll use the current working directory that the script was called from
    if not inDir:
        inDir = os.getcwd()

    # If not output directory is provided we'll use the same directory as the current working directory
    if not outDir:
        outDir = inDir

    # It is possible that the output directory is provided in relative terms ("../../")
    # abspath will convert this to a real path
    outDir = os.path.abspath(outDir)

    # It is also possible that the output directory does not exist.
    # We should error early if it does not exist
    if not os.path.exists(outDir):
        raise IOError("%s does not exist!" % outDir)
    if not os.path.exists(inDir):
        raise IOError("%s does not exist!" % inDir)

    # Finally we loop through all the files in the current directory
    for f in os.listdir(inDir):
        # We will start by skipping over files that start with a dot.
        # This is a sign that they are hidden and should not be modified
        if f.startswith('.'):
            continue

        # If we are told to use regex, then lets use the regex module to replace the string
        if regex:
            # use regex's substitute function to replace
            name = re.sub(inString, outString, f)
        else:
            # Otherwise lets just use regular string replace
            name = f.replace(inString, outString)

        # Finally if the name is identical, then don't bother renaming it because it's wasted time
        if name == f:
            continue

        # Now lets construct the full paths to copy from since we only currently have the name of the actual file
        src = os.path.join(inDir, f)
        dest = os.path.join(outDir, name)

        # If we're told to duplicate, we'll use the shutil library and its' copy2 function to copy the file
        if duplicate:
            shutil.copy2(src, dest)
        else:
            # Otherwise we'll just use the os module to rename the file
            os.rename(src, dest)


# We want to run the main() method when this python script is loaded
# But we only want to do it when it's run directly and not when it's imported by something else
# So we use this little check
#
# We check if the namespace (__name__) is __main__
# This means that the code is being run directly instead of being imported into a namespace
#
# It's recommended to design like this so your code can be imported and reused even if you intend to only run it directly
if __name__ == '__main__':
    # If this is true, then we run main()
    main()