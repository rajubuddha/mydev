# mydev

//gateway submit


import sys
import os
sys.path.insert(0,r"C:\Program Files\Southpaw\tactic\src\client")
from tactic_client_lib import TacticServerStub
a=TacticServerStub(server='localhost:8081',user='admin',password='raju',login='admin',project='admin',site="localhost:8081")
import maya.cmds as mc

cFn=mc.file(q=True,sn=True)
oFn=os.path.split(cFn)[-1].split("_")
prjDict={"md":'mydev','lay':'layout'}

try:
    cTask=a.eval("@SOBJECT(%s/shot['name','%s'].sthpw/task['process','%s'])"%(prjDict[oFn[0]],oFn[2],prjDict[oFn[3]]))[0]
    print "found task..."
    a.eval("@UPDATE(@SOBJECT(sthpw/task['code','%s']['process','%s']),'status','Complete')"%(cTask['code'],prjDict[oFn[3]]))
    print "updated task..."
    cTask=a.eval("@SOBJECT(%s/shot['name','%s'])"%(prjDict[oFn[0]],oFn[2]))[0]
    #snapshot = a.directory_checkin(search_key=cTask['__search_key__'], context="layout", dir="C:/Users/Aruna/Desktop/testCheck", description="dir ok",checkin_type="auto")    
    res=a.simple_checkin( search_key=cTask['__search_key__'], context=prjDict[oFn[3]], file_path=cFn, snapshot_type="file", description="Submit from Maya", use_handoff_dir=False, file_type="main", is_current=True, level_key=None, breadcrumb=False, metadata={}, mode="replace",, is_revision=False,keep_file_name=False, create_icon=False,checkin_type="auto", checkin_cls='pyasm.checkin.FileCheckin')
    print "task submited..."    
except:
    mc.warning('please try again/check your naming conventsion <project>_<ep>_<seq>_<shot>_<process>_<version>.<ext>'
    
    
    
