import bpy
pathwise_cf_details={}
pathwise_cfext_details={}
pathwise_obj_details={}
pathwise_mat_details={}
org_obj_mat={}
obj_name_maps={}
#newSdrs=['new_sdr','new_sdr3','new_sdr2']
for obj in bpy.data.objects:
    for mc in obj.modifiers:
        if mc.type == 'MESH_SEQUENCE_CACHE':
            if pathwise_obj_details.get(mc.cache_file.filepath):
                if obj.name not in pathwise_obj_details[mc.cache_file.filepath]:
                    pathwise_obj_details[mc.cache_file.filepath].append(obj.name)
            else:
                pathwise_obj_details[mc.cache_file.filepath]=[obj.name].sort()
                
            if pathwise_cf_details.get(mc.cache_file.filepath):
                pathwise_cf_details[mc.cache_file.filepath].append(obj.name)
                print('added')
                
            else:
                print('added new')
                pathwise_cf_details[mc.cache_file.filepath]=[obj.name]
                
            if obj_name_maps.get(mc.object_path.split('/')[1]):
                obj_name_maps[mc.object_path.split('/')[1]].append(obj.name)
                print('added')
                
            else:
                print('added new')
                obj_name_maps[mc.object_path.split('/')[1]]=[obj.name]
                
    
    for cn in obj.constraints:
        if cn.type == 'TRANSFORM_CACHE':
            if pathwise_obj_details.get(cn.cache_file.filepath):
                if obj.name not in pathwise_obj_details[cn.cache_file.filepath]:
                    pathwise_obj_details[cn.cache_file.filepath].append(obj.name).sort()
            else:
                pathwise_obj_details[cn.cache_file.filepath]=[obj.name]
                
            if pathwise_cf_details.get(cn.cache_file.filepath):
                
                if obj.name not in pathwise_cf_details[cn.cache_file.filepath]:
                
                    pathwise_cf_details[cn.cache_file.filepath].append(obj.name)
            else:
                pathwise_cf_details[cn.cache_file.filepath]=[obj.name]
                
            if obj_name_maps.get(cn.object_path.split('/')[1]):

                obj_name_maps[cn.object_path.split('/')[1]].append(obj.name)

            else:

                obj_name_maps[cn.object_path.split('/')[1]]=[obj.name]                
                     
    for idx,ms in enumerate(obj.material_slots):

        if pathwise_mat_details.get(obj.name):
            pathwise_mat_details[obj.name].append((ms.name,idx))
        else:
            pathwise_mat_details[obj.name]=[(ms.name,idx)]

for k,v in  obj_name_maps.items():
    
    #print(pathwise_mat_details[k])
    org_obj_mat[k]=pathwise_mat_details[k]

print(pathwise_cf_details)
print(obj_name_maps)
print(org_obj_mat)
'''
mat_dict={}
for obj in bpy.data.objects:

    if str(obj.library) != 'None' :
        print('original link objects ',obj.library.filepath)
        for i,loms in enumerate(obj.material_slots):
            
            if mat_dict.get(obj.name):
                mat_dict[obj.name].append([i,loms.material])
            else:
                mat_dict[obj.name]=[i,loms.material]

for obj in bpy.data.objects:        
    for i,loms in enumerate(obj.material_slots):
        obj.material_slots[i].material=mat_dict[obj.name][1]
'''
'''   
print(pathwise_obj_details)
print(pathwise_mat_details)
for k,v in pathwise_obj_details.items():
    cobj=None
    for ko,vo in pathwise_mat_details.items():
        if vo == v[0]:
            cobj=ko
        
    print(k,v[0],pathwise_mat_details[v[0]])'''
    
