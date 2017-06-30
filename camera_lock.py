import bpy

#bpy.ops.mesh.primitive_uv_sphere_add()
#bpy.ops.object.editmode_togg
for i in bpy.data.objects:
    if i.data.rna_type:
        if i.data.rna_type.name == 'Camera':
            i.lock_location[0]=True
            i.lock_location[1]=True
            i.lock_location[2]=True
            i.lock_rotation[0]=True
            i.lock_rotation[1]=True
            i.lock_rotation[2]=True
            i.lock_scale[0]=True
            i.lock_scale[1]=True
            i.lock_scale[2]=True