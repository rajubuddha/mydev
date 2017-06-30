import bpy
pathwise_cf_details={}
pathwise_obj_details={}
pathwise_mat_details={}
newSdrs=['new_sdr','new_sdr3','new_sdr2']
for obj in bpy.data.objects:
    for mc in obj.modifiers:
        if mc.type == 'MESH_SEQUENCE_CACHE':
            if pathwise_obj_details.get(mc.cache_file.filepath):
                if obj.name not in pathwise_obj_details[mc.cache_file.filepath]:
                    pathwise_obj_details[mc.cache_file.filepath].append(obj.name)
                    
            else:
                pathwise_obj_details[mc.cache_file.filepath]=[obj.name].sort()
                
            if pathwise_cf_details.get(mc.cache_file.name):
                if obj.name not in pathwise_cf_details[mc.cache_file.name]:
                    pathwise_cf_details[mc.cache_file.name].append(obj.name)
            else:
                pathwise_cf_details[mc.cache_file.name]=[obj.name]
                
    
    for cn in obj.constraints:
        if cn.type == 'TRANSFORM_CACHE':
            if pathwise_obj_details.get(cn.cache_file.filepath):
                if obj.name not in pathwise_obj_details[cn.cache_file.filepath]:
                    pathwise_obj_details[cn.cache_file.filepath].append(obj.name).sort()
            else:
                pathwise_obj_details[cn.cache_file.filepath]=[obj.name]
                
            if pathwise_cf_details.get(cn.cache_file.name):
                
                if obj.name not in pathwise_cf_details[cn.cache_file.name]:
                
                    pathwise_cf_details[cn.cache_file.name].append(obj.name)
            else:
                pathwise_cf_details[cn.cache_file.name]=[obj.name]
                     
    for idx,ms in enumerate(obj.material_slots):
        print(obj.name,ms.name,ms)
        ms.material=bpy.data.materials[newSdrs[idx]]
        if pathwise_mat_details.get(obj.name):
            pathwise_mat_details[obj.name].append((ms.name,idx))
        else:
            pathwise_mat_details[obj.name]=[(ms.name,idx)]
            
            
'''   
print(pathwise_cf_details)

print(pathwise_obj_details)
print(pathwise_mat_details)
for k,v in pathwise_obj_details.items():
    cobj=None
    for ko,vo in pathwise_mat_details.items():
        if vo == v[0]:
            cobj=ko
        
    print(k,v[0],pathwise_mat_details[v[0]])'''
    
