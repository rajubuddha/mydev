def moveToGrid():
    
    import maya.cmds as mc
    
    allMTG=[]
    for t in mc.ls(et="transform"):
        if "move_to_grid" in mc.listAttr(t):
            allMTG.append(t)

    mtgGrp=mc.group(n="mtgGrp",em=True)
    allLocCons=[]
    locDict={}
    for l in allMTG:
        res=mc.spaceLocator(n="%s_loc"%l.replace(":","_"))
        mc.parent(res,mtgGrp)
        pCon=mc.parentConstraint(l,res)[0]
        allLocCons.append(pCon)
        locDict[res[0]]=l
    mc.bakeResults(mtgGrp,sm=True,t=(1,120),hi="below",sb=1,dic=True,pok=True,sac=False,ral=False,rba=False,bol=False,mr=True,cp=False,s=True)
    mc.delete(allLocCons)
    
    for loc,obj in locDict.items():
        mc.parentConstraint(loc,obj)
    mc.delete(mtgGrp,c=True)
    mLoc=mc.spaceLocator(n="MainMoveToGridLocator")
    
    allChars=[]
    for r in allMTG:
        if "/char/" in mc.referenceQuery(r,f=True):
            con=mc.parentConstraint(r,mLoc[0])
            mc.delete(con)
    mc.parentConstraint(mLoc[0],mtgGrp,mo=True)