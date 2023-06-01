# Changes to the course if using Python 3 and Maya 2022 and later

## Table of Contents

* [Editor](#editor)
* [Syntax Changes](#python-3-syntax-changes)
* [Maya Changes](#changes-in-newer-versions-of-maya)

## Editor
We recommend using VSCode as the new code editor when following the course.

Starting with Maya2022, the DevKit no longer ships with the "other" folder that contained the completion file. Use the MayaCode and MayaPy extensions for VSCode for easy autocomplete setup. Be sure to create the userSetup.py script to configure the port forwarding to Maya.

Refer to the guide compiled on the process <a>here <href link=https://github.com/benjaminbeilharz/aswf-slp/blob/main/setups/VSCode_to_Maya_connection.md></a>

The refactoring feature used in lesson 69 is also supported in VSCode.

## Python 3 Syntax Changes
* <code>**Print**</code> has now been changed to a function, so all calls to <code>print</code> will need to have the parameters surrounded by parentheses - i.e. <code>print("hello world")</code> or <code>print(help(...))</code>

* <code>**Reload**</code> is now located in the <code>importlib</code> library. To use it, include the line 
<br>
    <code> import importlib.reload as reload </code>
</br>
in the Maya python editor before using the <code>reload(...)</code> when testing the course scripts.
    * To elevate your dev experience we recommend including this line in the **userSetup.py** script referred to earlier.

**Lighting Manager** - 
In lesson 62, <code>basestring</code> is no longer supported in python3. Instead replace it with <code>str</code>.
Similary, there are longer two forms integers (int and long) in python3. So in lesson 66, when casting the reference for the main window, instead of <code>long(win)</code> use <code>int(win)</code>.

For more changes between python2 and python3, check out <a>this reference page<href link=https://python-future.org/compatible_idioms.html></a>.

## Changes in newer versions of Maya
Aside from icon changes, there is one main update to Maya that is noteworthy for this course. The **default renderer** has been changed from **Maya Software** to **Arnold**. For the **Controller Library** project, make sure to _change the default renderer to Maya Software_ like it is in the tutorials. 

The setting is the second dropdown in the Render Settings window.
