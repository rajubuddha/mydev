import win32gui
tempWindowName=win32gui.GetWindowText (win32gui.GetForegroundWindow())
import time
allProgs={}
while True:
    tempWindowName=win32gui.GetWindowText (win32gui.GetForegroundWindow())
    cFile=tempWindowName.split()
    if cFile:
        if cFile[1] in allProgs.keys():
            try:
                allProgs[cFile[1]]=allProgs[cFile[1]]+.1
            except:pass
        else:
            allProgs[cFile[1]] = 0.1
    time.sleep(0.1)
    print allProgs