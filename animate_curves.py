import bpy
from mathutils import Vector

def make_animated_curve_from_abc(src=""):
    origCrvs=bpy.data.objects[src]
    cObj=bpy.data.curves.new(name="myCrv",type="CURVE")
    cObj.dimensions='3D'
    cObjSpline=cObj.splines.new('NURBS')
    myPts=[]
    for i,op in enumerate(origCrvs.data.splines[0].points):
        x,y,z,w=op.co
        myPts.append(Vector((x,y,z,w)))

    cObjSpline.points.add(len(myPts)-1)
    cObjSpline.order_u=2

    for i,pt in enumerate(cObjSpline.points):
        x,y,z,w=myPts[i]
        pt.co=[x,y,z,w]
    cObj=bpy.data.objects.new(name="myCrv",object_data=cObj)
    bpy.context.scene.objects.link(cObj)    
    bpy.context.scene.objects.active=cObj

    for fr in range(1,120):
        bpy.context.scene.frame_set(fr)
        for sp in cObj.data.splines:
            for i,pt in enumerate(sp.points):
                pt.co=origCrvs.data.splines[0].points[i].co[:]
                pt.keyframe_insert(data_path="co",frame=fr)
                
resCrvs=[]
for obj in bpy.data.objects:
    if obj.data:
        if obj.data.rna_type.name == "Curve":
            resCrvs.append(obj)
            make_animated_curve_from_abc(src=obj.name)
                    