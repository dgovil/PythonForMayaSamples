# Namespace aliasing
import maya.cmds as cmds

def createPipe(spans=20):
    transform, shape = cmds.polyPipe(subdivisionsAxis=spans)
    return transform

def createGear(teeth=10, length=1):
    spans = teeth * 2
    pipe = createPipe(spans=spans)
    sideFaces = range(spans*2, spans*3, 2)

    cmds.select(clear=True)
    for face in sideFaces:
        cmds.select('%s.f[%s]' % (pipe, face), add=True)

    extrude = cmds.polyExtrudeFacet(localTranslateZ=length)
    return pipe, extrude[0]

def changeLength(extrude, length=1):
    cmds.polyExtrudeFacet(extrude, edit=True, ltz=length)