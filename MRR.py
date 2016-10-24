import maya.cmds as mc
import maya.mel as mel


class MRR_ML():
    def makeCustomClr(self, *args):

        resPass = mc.shadingNode('renderPass', asRendering=True, name="rgb01")
        mel.eval(
            'applyAttrPreset {0} "C:/Program Files/Autodesk/Maya2015/presets/attrPresets/renderPass/customColor.mel" 1;'.format(
                resPass))

        return resPass

    def makeMRRAmbient(self, inFile="", inSdr="", *args):

        rmHsv = mc.shadingNode("remapHsv", asUtility=True)
        mc.setAttr("{0}.saturation[1].saturation_FloatValue".format(rmHsv), 0.5)
        mc.connectAttr("{0}.outColor".format(inFile), "{0}.color".format(rmHsv), f=True)
        mulDiv = mc.shadingNode("multiplyDivide", asUtility=True)
        mc.setAttr("{0}.input2".format(mulDiv), 0.2, .2, .2)
        mc.connectAttr("{0}.outColor".format(rmHsv), "{0}.input1".format(mulDiv), f=True)
        mc.connectAttr("{0}.output".format(mulDiv), "{0}.ambientColor".format(inSdr), f=True)

    def getAllSdrsDoAction(self, *args):

        sgs = mc.ls(et="shadingEngine")
        sgs.remove('initialShadingGroup')
        sgs.remove('initialParticleSE')
        for i in sgs:
            sdr = mc.listConnections(i + ".ss")[0]
            clrCons = mc.listConnections(sdr + ".color")
            if clrCons:
                if "outColor" in mc.listAttr(clrCons[0]):
                    makeMRRAmbient(inFile=clrCons[0], inSdr=sdr)

    def makeRgbCb(self, inClrA=(1, 0, 0, 0), inSdr="phong1", inRPass="rgb01", inBufName="%s_buf" % "shirt", *args):
        
        cb = mc.shadingNode("writeToColorBuffer", asUtility=True, n=inBufName)
        mc.setAttr(cb + ".color", inClrA[0], inClrA[1], inClrA[2])
        mc.setAttr(cb + ".alpha", inClrA[3])
        mc.setAttr(cb + ".evaluationPassThrough", 0, 0, 0)
        mc.setAttr(cb + ".evaluationMode", 1)
        mc.connectAttr(cb + ".outEvaluationPassThroughR", inSdr + ".glowIntensity")
        mc.connectAttr(inRPass + ".message", cb + ".renderPass")

    def makeRgbUI(self, *args):

        btns = [('shirt', (1, 0, 0, 0)), ('pant', (0, 1, 0, 0)), ('color', (0, 0, 1, 0)), ('body', (1, 0, 0, 1)),
                ('hair', (0, 1, 0, 1)), ('shoe', (0, 0, 1, 1)), ('test01', (1, 0, 1, 0)), ('test02', (0, 1, 1, 0)),
                ('test03', (1, 1, 0, 0))]
        if mc.window("rgbMaker", ex=True):
            mc.deleteUI("rgbMaker")

        if mc.windowPref("rgbMaker", ex=True):
            mc.windowPref("rgbMaker", r=True)

        mc.window("rgbMaker", wh=(150, 300))
        mc.columnLayout(adj=True)
        for btn, ca in btns:
            mc.button(btn, l=btn)
        mc.showWindow("rgbMaker")


MRR_ML().makeRgbUI()
