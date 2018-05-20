import maya.cmds as mc
import sys
data={rig_name:{'Geometry':None,'nonScalables':None,'POS':{'ADJ_grp':{'ADJ':{'motionSystem':{"IKSystem":None,"FKSystem":None},'skeletonSystem':None}}}}}
def make_recurcive_grps(root="",data={}):
    rig_name=root
    for k,v in data.items():
        res_top=mc.group(n=k,em=True)
        if res_top != rig_name:
            mc.parent(res_top,rig_name)    
        if isinstance(v,dict):
            make_recurcive_grps(root=k,data=v)
            
make_recurcive_grps(root="test_rig",data=data)
