import maya.cmds as mc

btns=[('shirt',(1,0,0,0)),('pant',(0,1,0,0)),('color',(0,0,1,0)),('body',(1,0,0,1)),('hair',(0,1,0,1)),('shoe',(0,0,1,1)),('test01',(1,0,1,0)),('test02',(0,1,1,0)),('test03',(1,1,0,0))]

if mc.window("rgbMaker",ex=True):
    mc.deleteUI("rgbMaker")

if mc.windowPref("rgbMaker",ex=True):
    mc.windowPref("rgbMaker",r=True)

mc.window("rgbMaker",wh=(150,300))
mc.columnLayout(adj=True)
for btn,ca in btns:
    mc.button(btn,l=btn)
mc.showWindow("rgbMaker")