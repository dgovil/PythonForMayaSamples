# Python For Maya: An Artist Friendly Course

Code samples for people who take part in my Python for Maya course

The course is not currently live, but this code repo will represent the projects being taught by the course.

This course will teach Python for Maya using an artist friendly approach, by breaking down concepts into small digestible pieces and giving projects with real world use.


## Projects We'll Be Completing

During the course, we'll create a few different projects to both showcase how Python is useful in a real world context,and to learn new concepts

* Create and prop geometry with a simple rig ([LINK](introduction/))
* Rename and organize a scene ([LINK](objectRenamer/))
* Automatically create Gears for modelling with a configurable amount of teeth ([LINK](gearCreator/))
* An Animation Tweener with a simple UI ([LINK](tweener/))
* A Library tool for Rigging Controls with a UI ([LINK](controllerLibrary/))
* A Light Manager
* A command line file tool to manage image sequences

## Tools That We'll Be Using

For the course we will use the following

* **Maya 2017**

  This is currently the latest version of Maya and has some major changes that will be covered.
  Feel free to use an older version of Maya (as low as 2011), as I will cover the differences and give you the knowledge to adapt
  
  You can download an education version of Maya 2017 here: http://www.autodesk.com/education/free-software/maya
  You can download a Maya 2017 trial here: http://www.autodesk.com/products/maya/free-trial
  
* **Python 2.7**

  Obviously, this course will use Python, but it is important to note we will be using Python 2.7 and not Python 3.x
  
  If you do not already have Python installed, I recommend downloading Anaconda instead.
  It is a packaged version of Python that comes with a lot of great libraries prebuilt for you, and is much easier to get started with than the official Python.
  Please remember to download the Python 2.7 version

  https://www.continuum.io/downloads
  
  Maya 2017 uses Python 2.7 and this is also the agreed upon standard by the VFX Reference Platform www.vfxplatform.com
  Maya 2014-2016 also use Python 2.7, whereas Maya 2011-2013 use Python 2.6.
  
  The latest version of Python is Python 3.5, however Python 3.x has introduced many breaking changes to Python.
  These changes are for the better but due to large investment into Python 2 code, Maya will continue to be on Python 2 for a while longer.
  
* **PyCharm**

  PyCharm is a very well established IDE with a lot of useful features for a beginner to both learn with and grown into a full fledged developer.
  It is my editor of choice today.
  
  I would recommend downloading PyCharm Edu from here: https://www.jetbrains.com/pycharm-edu/
  
  PyCharm Edu is a version of PyCharm with a simplified interface (optional) and coursework that will help a user learn Python in their spare time.
  
* **Maya DevKit**

  Unfortunately from Maya 2016 onwards, Autodesk stopped shipping the Maya developer kit with Maya.
  This isn't super necessary for our course, but it does provide some nice autocomplete features in our editors.
  
  If you're on **Maya 2016** download the zip file from here: https://github.com/autodesk-adn/Maya-devkit
  
  If you're on **Maya 2017** download it from here: https://apps.autodesk.com/MAYA/en/Detail/Index?id=6303159649350432165&appLang=en
  
  
  Instructions on how to set up your directories for your specific OS are here: http://help.autodesk.com/view/MAYAUL/2017/ENU//?guid=__files_Setting_up_your_build_environment_htm
  
  
  
* **Other Editors**

  There are a lot of other editors, and I will personally not be using them for this course.
  However, if you have a preference for other editors, I will go over setting up the editors with Maya.
  The following editors will be covered
  
  * Sublime Text
  * Atom
  * Visual Studio Code
  * Eclipse
  
* **Operating System**
  My preferred operating system is **Windows** and it will be what I will be using for the entire course.
  That said, I also use **macOS** and **Linux** and where anything should be treated differently, I will make mention of it.
  

## Libraries That Will Be Covered

The course will cover the following libraries

* `maya.cmds`
* `pymel`
* `Qt`
* `PySide` / `PySide2`