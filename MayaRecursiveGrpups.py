import maya.cmds as mc
import sys
rig_name="new_rig"
data={rig_name:{'POS':{'ADJ_grp':{'ADJ':{'motionSystem':None,'skeletonSystem':None}}},'Geometry':None,'nonScalables':None}}

def make_recurcive_grps(root="",data={}):
    rig_name=root
    for k,v in data.items():
        res_top=mc.group(n=k,em=True)
        if res_top != rig_name:
            mc.parent(res_top,rig_name)    
        if isinstance(v,dict):
            make_recurcive_grps(root=k,data=v)
            

def make_square_ctrl(parent="",radius=1):
    cir_res=mc.circle(ch=False,r=radius,nr=(0,1,0),d=1,s=4)
    mc.xform("%s.cv[*]"%cir_res[0],ro=(0,45,0),ws=True)
    cShape=mc.ls(cir_res[0],et="nurbsCurve",dag=True)
    mc.parent(cShape[0],parent,add=True,shape=True)
    mc.delete(cir_res[0])

make_recurcive_grps(root=rig_name,data=data)
make_square_ctrl(parent="POS",radius=1.5)
make_square_ctrl(parent="ADJ",radius=1)

object="ADJ"
non_keyable_attrs=["s","sx","sz","sy","v"]
for atr in non_keyable_attrs:
    mc.setAttr("%s.%s"%(object,atr),k=False)
    mc.setAttr("%s.%s"%(object,atr),l=True)

object="POS"    
add_attrs={'controls':["long",1],'joints':['long',1],'meshDisplay':["enum",'Normal:Template:Reference:']}
add_attrs_order=['controls','joints','meshDisplay']
for atr in add_attrs_order:
    v=add_attrs[atr]
    if v[0] not in ['string','enum']:
        mc.addAttr(object,ln=atr,at=v[0],dv=v[1])
    else:
        mc.addAttr(object,ln=atr,at=v[0],en=v[1])
    mc.setAttr("%s.%s"%(object,atr),k=False,cb=True)
   
mc.parentConstraint("ADJ",'Geometry',mo=True)
mc.scaleConstraint("ADJ",'Geometry',mo=True)
mc.setAttr("Geometry.overrideEnabled",1)
mc.connectAttr("POS.meshDisplay","Geometry.overrideDisplayType",f=True)
mc.connectAttr("POS.controls","motionSystem.v",f=True)
mc.connectAttr("POS.joints","skeletonSystem.v",f=True)
