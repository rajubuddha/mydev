def makeMRRAmbient(inFile="",inSdr=""):
    
    rmHsv=mc.shadingNode("remapHsv",asUtility=True)
    mc.setAttr("{0}.saturation[1].saturation_FloatValue".format(rmHsv),0.5)
    mc.connectAttr("{0}.outColor".format(inFile),"{0}.color".format(rmHsv),f=True)
    mulDiv=mc.shadingNode("multiplyDivide",asUtility=True)
    mc.setAttr("{0}.input2".format(mulDiv),0.2,.2,.2)
    mc.connectAttr("{0}.outColor".format(rmHsv),"{0}.input1".format(mulDiv),f=True)
    mc.connectAttr("{0}.output".format(mulDiv),"{0}.ambientColor".format(inSdr),f=True)

def getAllSdrsDoAction():
    
    sgs=mc.ls(et="shadingEngine")
    sgs.remove('initialShadingGroup')
    sgs.remove('initialParticleSE')
    for i in sgs:
        sdr=mc.listConnections(i+".ss")[0]
        clrCons=mc.listConnections(sdr+".color")
        if clrCons:
            if "outColor" in mc.listAttr(clrCons[0]):
                makeMRRAmbient(inFile=clrCons[0],inSdr=sdr)