import time,datetime
from tactic_client_lib import TacticServerStub

ser=TacticServerStub.get()
pyLgn=ser.eval('$LOGIN')
cDate=str(datetime.datetime.now()).split(' ')[0]
coTime=int(time.time())
loTs=str(datetime.datetime.now()).split('.')[0]
pyLoginLog=ser.eval("@SOBJECT(sthpw/login_log['date','%s']['login','%s'])"%(cDate,pyLgn))[0]
pyDifTime=abs(int(pyLoginLog['start_time'])-coTime)
tDur=time.strftime("%H:%M:%S", time.gmtime(pyDifTime))
ser.update(search_key=pyLoginLog['__search_key__'],data={'signout_time':loTs,'end_time':coTime,'duration':tDur})


import time,datetime
from tactic_client_lib import TacticServerStub

cTime=str(time.time()).split('.')[0]
cDate=str(datetime.datetime.now()).split(' ')[0]
ser=TacticServerStub.get();
proj=ser.eval('$PROJECT');
lgn=ser.eval('$LOGIN');
expRes=ser.eval("@COUNT(sthpw/attendance['date','%s']['login','%s']['project','%s'])"%(cDate,lgn,proj))

if (expRes<1):
    ser.insert(search_type='sthpw/attendance',data={'project':proj,'login':lgn,'date':cDate})

expRes=ser.eval("@COUNT(sthpw/login_log['date','%s']['login','%s'])"%(cDate,lgn));

if (expRes<1):
    ser.insert(search_type='sthpw/login_log',data={'login':lgn,'start_time':cTime,'date':cDate})
